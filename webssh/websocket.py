from channels.generic.websocket import WebsocketConsumer
from .ssh import SSH
from django.conf import settings
from django.http.request import QueryDict
from django.utils.six import StringIO
import django.utils.timezone as timezone
from devops.settings import TMP_DIR
from server.models import RemoteUserBindHost
from webssh.models import TerminalLog
from django.db.models import Q
import os
import json
import re
import time

try:
    session_exipry_time = settings.CUSTOM_SESSION_EXIPRY_TIME
except BaseException:
    session_exipry_time = 60 * 30


def terminal_log(user, hostname, ip, protocol, port, username, cmd, detail, address, useragent, start_time):
    event = TerminalLog()
    event.user = user
    event.hostname = hostname
    event.ip = ip
    event.protocol = protocol
    event.port = port
    event.username = username
    event.cmd = cmd
    event.detail = detail
    event.address = address
    event.useragent = useragent
    event.start_time = start_time
    event.save()


class WebSSH(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = {'status': 0, 'message': None}
        """
        status:
            0: ssh 连接正常, websocket 正常
            1: 发生未知错误, 关闭 ssh 和 websocket 连接

        message:
            status 为 1 时, message 为具体的错误信息
            status 为 0 时, message 为 ssh 返回的数据, 前端页面将获取 ssh 返回的数据并写入终端页面
        """
        self.session = None
        self.remote_host = None
        self.start_time = None
    
    def connect(self):
        """
        打开 websocket 连接, 通过前端传入的参数尝试连接 ssh 主机
        :return:
        """
        self.accept()
        self.start_time = timezone.now()
        self.session = self.scope.get('session', None)
        if not self.session.get('islogin', None):    # 未登录直接断开 websocket 连接
            self.message['status'] = 2
            self.message['message'] = 'You are not login in...'
            message = json.dumps(self.message)
            self.send(message)
            self.close(3001)

        self.check_login()

        query_string = self.scope.get('query_string').decode()
        ssh_args = QueryDict(query_string=query_string, encoding='utf-8')

        width = ssh_args.get('width')
        height = ssh_args.get('height')
        width = int(width)
        height = int(height)

        auth = None
        ssh_key_name = '123456'
        hostid = int(ssh_args.get('hostid'))
        try:
            if not self.session['issuperuser']:     # 普通用户判断是否有相关主机或者权限
                hosts = RemoteUserBindHost.objects.filter(
                    Q(id=hostid),
                    Q(user__username=self.session['username']) | Q(group__user__username=self.session['username']),
                ).distinct()
                if not hosts:
                    self.message['status'] = 2
                    self.message['message'] = 'Host is not exist...'
                    message = json.dumps(self.message)
                    self.send(message)
                    self.close(3001)
            self.remote_host = RemoteUserBindHost.objects.get(id=hostid)
            if not self.remote_host.enabled:
                try:
                    self.message['status'] = 2
                    self.message['message'] = 'Host is disabled...'
                    message = json.dumps(self.message)
                    self.send(message)
                    self.close(3001)
                except BaseException:
                    pass
        except BaseException:
            self.message['status'] = 2
            self.message['message'] = 'Host is not exist...'
            message = json.dumps(self.message)
            self.send(message)
            self.close(3001)
        host = self.remote_host.ip
        port = self.remote_host.port
        user = self.remote_host.remote_user.username
        passwd = self.remote_host.remote_user.password
        timeout = 15
        self.ssh = SSH(websocker=self, message=self.message)
        ssh_connect_dict = {
            'host': host,
            'user': user,
            'port': port,
            'timeout': timeout,
            'pty_width': width,
            'pty_height': height,
            'password': passwd,
        }
        if auth == 'key':
            ssh_key_file = os.path.join(TMP_DIR, ssh_key_name)
            with open(ssh_key_file, 'r') as f:
                ssh_key = f.read()

            string_io = StringIO()
            string_io.write(ssh_key)
            string_io.flush()
            string_io.seek(0)
            ssh_connect_dict['ssh_key'] = string_io

            os.remove(ssh_key_file)

        self.ssh.connect(**ssh_connect_dict)
        if self.remote_host.remote_user.enabled:
            if self.session.get('issuperuser', None):  # 超级管理员才能使用 su 跳转功能
                if self.remote_host.remote_user.superusername:
                    self.ssh.su_root(
                        self.remote_host.remote_user.superusername,
                        self.remote_host.remote_user.superpassword,
                        0.3,
                    )

    def disconnect(self, close_code):
        try:
            if close_code == 3001:
                pass
            else:
                self.ssh.close()
        except:
            pass
        finally:
            # 过滤点结果中的颜色字符
            self.ssh.res = re.sub(r'(\[\d{2};\d{2}m|\[0m)', '', self.ssh.res)
            # print('命令: ')
            # print(self.ssh.cmd)
            # print('结果: ')
            # print(res)
            user_agent = None
            for i in self.scope['headers']:
                if i[0].decode('utf-8') == 'user-agent':
                    user_agent = i[1].decode('utf-8')
                    break
            if self.ssh.cmd:
                terminal_log(
                    self.session.get('username'),
                    self.remote_host.hostname,
                    self.remote_host.ip,
                    self.remote_host.get_protocol_display(),
                    self.remote_host.port,
                    self.remote_host.remote_user.username,
                    self.ssh.cmd,
                    self.ssh.res,
                    self.scope['client'][0],
                    user_agent,
                    self.start_time,
                )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if type(data) == dict:
            if data['data'] and '\r' in data['data']:
                self.check_login()
            status = data['status']
            if status == 0:
                data = data['data']
                self.ssh.shell(data)
            else:
                cols = data['cols']
                rows = data['rows']
                self.ssh.resize_pty(cols=cols, rows=rows)

    def check_login(self):
        lasttime = int(self.scope['session']['lasttime'])
        now = int(time.time())
        if now - lasttime > session_exipry_time:
            self.message['status'] = 2
            self.message['message'] = 'Your login is expired...'
            message = json.dumps(self.message)
            self.send(message)
            self.close(3001)
        else:
            self.scope['session']['lasttime'] = now
            self.scope["session"].save()
