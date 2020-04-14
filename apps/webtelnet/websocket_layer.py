from channels.generic.websocket import WebsocketConsumer
from .telnet import Telnet
from django.conf import settings
from django.http.request import QueryDict
import django.utils.timezone as timezone
from server.models import RemoteUserBindHost
from webssh.models import TerminalSession
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from util.crypto import decrypt
import json
import time
import traceback
from util.tool import gen_rand_char, terminal_log, res
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


try:
    session_exipry_time = settings.CUSTOM_SESSION_EXIPRY_TIME
except Exception:
    session_exipry_time = 60 * 30


class WebTelnet(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = {'status': 0, 'message': None}
        """
        status:
            0: telnet 连接正常, websocket 正常
            1: 发生未知错误, 关闭 telnet 和 websocket 连接

        message:
            status 为 1 时, message 为具体的错误信息
            status 为 0 时, message 为 telnet 返回的数据, 前端页面将获取 telnet 返回的数据并写入终端页面
        """
        self.session = None
        self.remote_host = None
        self.start_time = None
        self.send_flag = 0      # 0 发送自身通道，1 发送 group 通道，作用为当管理员查看会话时，进入 group 通道
        self.group = 'session_' + gen_rand_char()
        self.lock = False  # 锁定会话
        self.client = None
        self.user_agent = None
    
    def connect(self):
        """
        打开 websocket 连接, 通过前端传入的参数尝试连接 telnet 主机
        :return:
        """
        self.accept()
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)  # 加入组
        self.start_time = timezone.now()
        self.session = self.scope.get('session', None)
        if not self.session.get('islogin', None):    # 未登录直接断开 websocket 连接
            self.message['status'] = 2
            self.message['message'] = 'You are not login in...'
            message = json.dumps(self.message)
            self.send(message)
            self.close(3001)

        if 'webtelnet终端' not in self.session[settings.INIT_PERMISSION]['titles']:    # 判断权限
            self.message['status'] = 2
            self.message['message'] = '无权限'
            message = json.dumps(self.message)
            self.send(message)
            self.close(3001)

        self.check_login()

        query_string = self.scope.get('query_string')
        telnet_args = QueryDict(query_string=query_string, encoding='utf-8')
        hostid = int(telnet_args.get('hostid'))
        try:
            if not self.session['issuperuser']:     # 普通用户判断是否有相关主机或者权限
                hosts = RemoteUserBindHost.objects.filter(
                    Q(id=hostid),
                    Q(enabled=True),
                    Q(user__username=self.session['username']) | Q(group__user__username=self.session['username']),
                ).distinct()
            else:
                hosts = RemoteUserBindHost.objects.filter(
                    Q(id=hostid),
                    Q(enabled=True),
                ).distinct()
            if not hosts:
                self.message['status'] = 2
                self.message['message'] = 'Host is not exist...'
                message = json.dumps(self.message)
                if self.send_flag == 0:
                    self.send(message)
                elif self.send_flag == 1:
                    async_to_sync(self.channel_layer.group_send)(self.group, {
                        "type": "chat.message",
                        "text": message,
                    })
                self.close(3001)
            self.remote_host = RemoteUserBindHost.objects.get(id=hostid)
        except Exception:
            print(traceback.format_exc())
            self.message['status'] = 2
            self.message['message'] = 'Host is not exist...'
            message = json.dumps(self.message)
            if self.send_flag == 0:
                self.send(message)
            elif self.send_flag == 1:
                async_to_sync(self.channel_layer.group_send)(self.group, {
                    "type": "chat.message",
                    "text": message,
                })
            self.close(3001)
        
        host = self.remote_host.ip
        port = self.remote_host.port
        user = self.remote_host.remote_user.username
        passwd = decrypt(self.remote_host.remote_user.password)
        timeout = 15
        self.telnet = Telnet(websocker=self, message=self.message)
        telnet_connect_dict = {
            'host': host,
            'user': user,
            'port': port,
            'password': passwd,
            'timeout': timeout,
        }

        self.telnet.connect(**telnet_connect_dict)
        if self.remote_host.remote_user.enabled:
            if self.remote_host.remote_user.superusername:
                if '登陆后su跳转超级用户' in self.session[settings.INIT_PERMISSION]['titles']:  # 判断权限
                    self.telnet.su_root(
                        self.remote_host.remote_user.superusername,
                        decrypt(self.remote_host.remote_user.superpassword),
                        1,
                    )

        for i in self.scope['headers']:
            if i[0].decode('utf-8') == 'user-agent':
                self.user_agent = i[1].decode('utf-8')
                break

        for i in self.scope['headers']:
            if i[0].decode('utf-8') == 'x-real-ip':
                self.client = i[1].decode('utf-8')
                break
            if i[0].decode('utf-8') == 'x-forwarded-for':
                self.client = i[1].decode('utf-8').split(',')[0]
                break
            self.client = self.scope['client'][0]
        data = {
            'name': self.channel_name,
            'group': self.group,
            'user': self.session.get('username'),
            'host': host,
            'username': user,
            'protocol': self.remote_host.protocol,
            'port': port,
            'type': 5,  # 5 webtelnet
            'address': self.client,
            'useragent': self.user_agent,
        }
        TerminalSession.objects.create(**data)

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)
            if close_code != 3001:
                self.telnet.close()
        except Exception:
            print(traceback.format_exc())
        finally:
            try:
                if self.telnet.cmd:
                    tmp = list(self.telnet.res_asciinema)
                    self.telnet.res_asciinema = []
                    res(self.telnet.res_file, tmp)
            except Exception:
                print(traceback.format_exc())
                
            user_agent = None
            for i in self.scope['headers']:
                if i[0].decode('utf-8') == 'user-agent':
                    user_agent = i[1].decode('utf-8')
                    break
            if self.telnet.cmd:
                terminal_log(
                    self.session.get('username'),
                    self.remote_host.hostname,
                    self.remote_host.ip,
                    self.remote_host.get_protocol_display(),
                    self.remote_host.port,
                    self.remote_host.remote_user.username,
                    self.telnet.cmd,
                    self.telnet.res_file,
                    self.client,
                    self.user_agent,
                    self.start_time,
                )
            TerminalSession.objects.filter(name=self.channel_name, group=self.group).delete()

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if type(data) == dict:
            if data['data'] and '\r' in data['data']:
                self.check_login()
            status = data['status']
            if status == 0:
                data = data['data']
                if self.lock:
                    self.message['status'] = 3
                    self.message['message'] = '当前会话已被管理员锁定'
                    message = json.dumps(self.message)
                    self.send(message)
                else:
                    self.telnet.shell(data)
            else:
                pass

    def check_login(self):
        lasttime = int(self.scope['session']['lasttime'])
        now = int(time.time())
        if now - lasttime > session_exipry_time:
            self.message['status'] = 2
            self.message['message'] = 'Your login is expired...'
            message = json.dumps(self.message)
            if self.send_flag == 0:
                self.send(message)
            elif self.send_flag == 1:
                async_to_sync(self.channel_layer.group_send)(self.group, {
                    "type": "chat.message",
                    "text": message,
                })
            self.close(3001)
        else:
            self.scope['session']['lasttime'] = now
            self.scope["session"].save()

    # 会话外使用 channels.layers 设置 type 为 chat.message 调用此函数
    def chat_message(self, data):
        try:
            message = json.loads(data['text'])
            if message['status'] == 0:
                self.send(data['text'])
            elif message['status'] == 1 or message['status'] == 2:      # 会话关闭
                self.send(data['text'])
                self.close()
            elif message['status'] == 3:    # 测试客户端显示消息框
                self.send(data['text'])
            elif message['status'] == 4:    # 有管理员进入查看模式
                self.send_flag = 1
                channel_layer = get_channel_layer()
                message = dict()
                message['status'] = 5
                message['message'] = self.telnet.res
                async_to_sync(channel_layer.send)(json.loads(data['text'])['message'], {
                    "type": "chat.message",
                    "text": json.dumps(message),
                })
            else:
                pass
        except Exception:
            pass

    def lock_message(self, data):
        if not self.lock:
            self.lock = True
            self.message['status'] = 3
            self.message['message'] = '当前会话已被管理员锁定'
            message = json.dumps(self.message)
            self.send(message)

    def unlock_message(self, data):
        if self.lock:
            self.lock = False
            self.message['status'] = 6
            self.message['message'] = '当前会话已被管理员解锁'
            message = json.dumps(self.message)
            self.send(message)
