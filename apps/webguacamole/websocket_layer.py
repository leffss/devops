import threading
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from server.models import RemoteUserBindHost
from webssh.models import TerminalSession
import django.utils.timezone as timezone
from django.db.models import Q
from asgiref.sync import async_to_sync
from util.tool import gen_rand_char, terminal_log, res
from util.crypto import decrypt
import time
from .guacamoleclient import Client, ClientView
import re
import base64
from django.http.request import QueryDict
import os
import shutil
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


try:
    terminal_exipry_time = settings.CUSTOM_TERMINAL_EXIPRY_TIME
except Exception:
    terminal_exipry_time = 60 * 30


class WebGuacamole(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        query_string = self.scope.get('query_string').decode()
        guacamole_args = QueryDict(query_string=query_string, encoding='utf-8')
        self.hostid = int(guacamole_args.get('hostid'))
        self.remote_host = None
        self.width = guacamole_args.get('width')
        self.height = guacamole_args.get('height')
        self.dpi = guacamole_args.get('dpi')
        self.session = None
        self.start_time = timezone.now()
        self.send_flag = 0  # 0 发送自身通道，1 发送 group 通道，作用为当管理员查看会话时，进入 group 通道
        self.group = 'session_' + gen_rand_char()
        self.guacamoleclient = None
        self.lock = False
        self.last_operation_time = time.time()
        self.closed = False
        self.client = None
        self.user_agent = None

    def connect(self):
        self.accept('guacamole')
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)  # 加入组
        self.session = self.scope.get('session', None)
        if not self.session.get('islogin', None):    # 未登录直接断开 websocket 连接
            self.close(3001)

        if 'webguacamole终端' not in self.session[settings.INIT_PERMISSION]['titles']:    # 判断权限
            self.close(3001)

        if not self.session['issuperuser']:
            hosts = RemoteUserBindHost.objects.filter(
                Q(id=self.hostid),
                Q(enabled=True),
                Q(user__username=self.session['username']) | Q(group__user__username=self.session['username']),
            ).distinct()
        else:
            hosts = RemoteUserBindHost.objects.filter(
                Q(id=self.hostid),
                Q(enabled=True),
            ).distinct()
        if not hosts:
            self.close(3001)

        self.remote_host = RemoteUserBindHost.objects.get(id=self.hostid)

        _type = 7
        if self.remote_host.get_protocol_display() == 'vnc':    # vnc 登陆不需要账号
            _type = 8

        # guacamole 连接性能参数设置
        # enable_wallpaper    如果设置为true，则开启桌面壁纸渲染。默认为不开启
        # enable_theming    如果设置为true，则开启窗口和控件的主题。默认为不开启
        # enable_font_smoothing 如果设置为“true”，文本将以平滑的边缘呈现。默认情况下，RDP上的文本粗体呈现，因为这减少了文本使用的颜色数量，从而减少了连接所需的带宽。
        # enable_full_window_drag   如果设置为“true”，窗口的内容将随着窗口的移动而显示。默认情况下，RDP服务器将仅在窗口拖动时绘制窗口边框。
        # enable_desktop_composition    如果设置为“true”，则允许使用透明窗口和阴影等图形效果。默认情况下，此类效果（如果可用）被禁用。
        # enable_menu_animations    如果设置为“true”，菜单开启和关闭动画将被允许。默认情况下禁用菜单动画。

        self.guacamoleclient = Client(websocker=self)
        if 'webguacamole终端文件上传下载' not in self.session[settings.INIT_PERMISSION]['titles']:  # 判断权限
            kwargs = {
                'protocol': self.remote_host.get_protocol_display(),
                'hostname': self.remote_host.ip,
                'port': self.remote_host.port,
                'username': self.remote_host.remote_user.username,
                'password': decrypt(self.remote_host.remote_user.password),
                'width': self.width,
                'height': self.height,
                'dpi': self.dpi,
                'enable_font_smoothing': "true",
            }
            if self.remote_host.remote_user.domain:
                kwargs['domain'] = self.remote_host.remote_user.domain
            if self.remote_host.security:
                kwargs['security'] = self.remote_host.security
            self.guacamoleclient.connect(**kwargs)
        else:
            kwargs = {
                'protocol': self.remote_host.get_protocol_display(),
                'hostname': self.remote_host.ip,
                'port': self.remote_host.port,
                'username': self.remote_host.remote_user.username,
                'password': decrypt(self.remote_host.remote_user.password),
                'width': self.width,
                'height': self.height,
                'dpi': self.dpi,
                'enable_font_smoothing': "true",
                'enable_drive': "true",
                'drive_name': "filesystem",
                'drive_path': "/fs/{}".format(self.group),
                'create_drive_path': "true",
            }
            if self.remote_host.remote_user.domain:
                kwargs['domain'] = self.remote_host.remote_user.domain
            if self.remote_host.security:
                kwargs['security'] = self.remote_host.security
            self.guacamoleclient.connect(**kwargs)
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
            'host': self.remote_host.ip,
            'username': self.remote_host.remote_user.username,
            'protocol': self.remote_host.protocol,
            'port': self.remote_host.port,
            'type': _type,  # 7 webrdp  8 webvnc
            'address': self.client,
            'useragent': self.user_agent,
            'connect_info': '{0}_{1}_{2}_{3}'.format(self.width, self.height, self.dpi, self.guacamoleclient.guacamoleclient.id)
        }
        TerminalSession.objects.create(**data)
        t = threading.Thread(target=self.check_timeout)
        t.daemon = True
        t.start()
        # 给客户端发送组信息，用于web页面上传文件，需要在 guacamole/js/all.js 中自定义 group 的处理处理方法
        self.send('5.group,10.group_name,{0}.{1};'.format(len(self.group), self.group))

    def disconnect(self, close_code):
        time.sleep(0.5)
        if not self.closed:
            self.closed = True
            if 'webguacamole终端文件上传下载' in self.session[settings.INIT_PERMISSION]['titles']:
                try:
                    upload_file_path = os.path.join(settings.GUACD_ROOT, self.group)
                    shutil.rmtree(upload_file_path, ignore_errors=True)
                except Exception:
                    pass
            try:
                async_to_sync(self.channel_layer.group_send)(self.group, {  # 关闭 viewer
                    "type": "close.viewer",
                    "text": "",
                })
                async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)
                if close_code != 3001:
                    self.guacamoleclient.close()
            except Exception:
                pass
            finally:
                if self.guacamoleclient.res:
                    try:
                        tmp = list(self.guacamoleclient.res)
                        self.guacamoleclient.res = []
                        res(self.guacamoleclient.res_file, tmp, False)
                    except Exception:
                        pass

                    try:
                        terminal_log(
                            self.session.get('username'),
                            self.remote_host.hostname,
                            self.remote_host.ip,
                            self.remote_host.get_protocol_display(),
                            self.remote_host.port,
                            self.remote_host.remote_user.username,
                            self.guacamoleclient.file_cmd,
                            self.guacamoleclient.res_file,
                            self.client,
                            self.user_agent,
                            self.start_time,
                        )
                    except Exception:
                        pass

                TerminalSession.objects.filter(name=self.channel_name, group=self.group).delete()

    def receive(self, text_data=None, bytes_data=None):
        if not self.lock:
            self.guacamoleclient.shell(text_data)
            if not text_data.startswith('4.sync') and not text_data.startswith('3.nop'):
                self.last_operation_time = time.time()
        else:
            if text_data.startswith('4.sync') or text_data.startswith('3.nop'):
                self.guacamoleclient.shell(text_data)
            else:
                if re.match(r'^5\.mouse,.*1\.1;$', text_data) or re.match(r'^3\.key,.*1\.1;$', text_data):
                    message = str(base64.b64encode('当前会话已被管理员锁定'.encode('utf-8')), 'utf-8')
                    self.send('6.toastr,1.1,{0}.{1};'.format(len(message), message))    # 给客户端发送警告

    # 会话外使用 channels.layers 设置 type 为 group.message 调用此函数
    def group_message(self, data):
        try:
            self.send(data['text'])
        except Exception:
            pass

    # 会话外使用 channels.layers 设置 type 为 close.message 调用此函数
    def close_message(self, data):
        try:
            message = str(base64.b64encode('当前会话已被管理员关闭'.encode('utf-8')), 'utf-8')
            # 给客户端发送toastr警告
            # 需要在 guacamole/js/all.js 中自定义 toastr 的处理处理方法
            self.send('6.toastr,1.2,{0}.{1};'.format(len(message), message))
            self.close()
        except Exception:
            pass

    def lock_message(self, data):
        if not self.lock:
            self.lock = True
            message = str(base64.b64encode('当前会话已被管理员锁定'.encode('utf-8')), 'utf-8')
            self.send('6.toastr,1.1,{0}.{1};'.format(len(message), message))

    def unlock_message(self, data):
        if self.lock:
            self.lock = False
            message = str(base64.b64encode('当前会话已被管理员解锁'.encode('utf-8')), 'utf-8')
            self.send('6.toastr,1.0,{0}.{1};'.format(len(message), message))

    def check_timeout(self, sleep_time=3):
        while 1:
            if self.closed:
                break

            if int(time.time() - self.last_operation_time) >= terminal_exipry_time:
                try:
                    message = str(base64.b64encode('由于长时间没有操作或者没有数据返回，连接已断开!'.encode('utf-8')), 'utf-8')
                    self.send('6.toastr,1.2,{0}.{1};'.format(len(message), message))
                    self.close()
                except Exception:
                    pass
                break

            time.sleep(sleep_time)

    def upload_message(self, data):
        cmd_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        filename = data['text']
        self.guacamoleclient.file_cmd += cmd_time + "\t" + '上传文件 - {}'.format(filename) + '\n'


class WebGuacamole_view(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None

    def connect(self):
        self.accept('guacamole')
        self.session = self.scope.get('session', None)
        if not self.session.get('islogin', None):  # 未登录直接断开 websocket 连接
            self.close()

        if '终端会话查看' not in self.session[settings.INIT_PERMISSION]['titles']:    # 判断权限
            self.close()

        query_string = self.scope.get('query_string').decode()
        args = QueryDict(query_string=query_string, encoding='utf-8')
        self.group = args.get('group')

        terminalsession = object
        try:
            terminalsession = TerminalSession.objects.get(group=self.group)
        except Exception:
            self.close()

        tmp = terminalsession.connect_info.split("_")
        width = tmp[0]
        height = tmp[1]
        dpi = tmp[2]
        protocol = tmp[3]

        self.guacamoleclient = ClientView(websocker=self)
        self.guacamoleclient.connect(
            protocol=protocol,
            hostname='',
            port='',
            username='',
            password='',
            width=width,
            height=height,
            dpi=dpi,
            enable_font_smoothing="true",
        )
        # 发送分辨率信息到查看模式的客户端
        self.send("7.display,{0}.{1},{2}.{3},{4}.{5};".format(len(width), width, len(height), height, len(dpi), dpi))

        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)  # 加入组

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)
        self.guacamoleclient.close()

    def receive(self, text_data=None, bytes_data=None):
        if text_data.startswith('4.sync') or text_data.startswith('3.nop'):
            self.guacamoleclient.shell(text_data)

    def close_viewer(self, data):
        message = str(base64.b64encode('会话已关闭'.encode('utf-8')), 'utf-8')
        self.send('6.toastr,1.2,{0}.{1};'.format(len(message), message))
        self.close()

    def upload_message(self, data):
        pass
