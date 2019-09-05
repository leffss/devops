import threading
from channels.generic.websocket import WebsocketConsumer
from threading import Thread
from asgiref.sync import async_to_sync
import socket
from django.conf import settings
from server.models import RemoteUserBindHost
from webssh.models import TerminalSession
import django.utils.timezone as timezone
import json
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from util.tool import gen_rand_char, terminal_log
import time
import traceback
from util.tool import gen_rand_char
import platform
from guacamole.client import GuacamoleClient
from .guacamoleclient import Client
import os
import re
import base64
from django.http.request import QueryDict
from webssh.tasks import celery_save_res_asciinema, celery_save_terminal_log


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
        self.user_agent = None
        self.guacamoleclient = None
        self.lock = False

    def connect(self):
        self.accept('guacamole')
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)  # 加入组
        self.session = self.scope.get('session', None)
        if not self.session.get('islogin', None):    # 未登录直接断开 websocket 连接
            self.close(3001)

        if not self.session['issuperuser']:
            hosts = RemoteUserBindHost.objects.filter(
                Q(id=self.hostid),
                Q(user__username=self.session['username']) | Q(group__user__username=self.session['username']),
            ).distinct()
            if not hosts:
                self.close(3001)

        self.remote_host = RemoteUserBindHost.objects.get(id=self.hostid)
        if not self.remote_host.enabled:
            self.close(3001)

        _type = 7
        if self.remote_host.get_protocol_display() == 'vnc':    # vnc 登陆不需要账号
            _type = 8

        self.guacamoleclient = Client(websocker=self)
        self.guacamoleclient.connect(
            protocol=self.remote_host.get_protocol_display(),
            hostname=self.remote_host.ip,
            port=self.remote_host.port,
            username=self.remote_host.remote_user.username,
            password=self.remote_host.remote_user.password,
            width=self.width,
            height=self.height,
            dpi=self.dpi,
        )

        for i in self.scope['headers']:
            if i[0].decode('utf-8') == 'user-agent':
                self.user_agent = i[1].decode('utf-8')
                break

        data = {
            'name': self.channel_name,
            'group': self.group,
            'user': self.session.get('username'),
            'host': self.remote_host.ip,
            'username': self.remote_host.remote_user.username,
            'protocol': self.remote_host.protocol,
            'port': self.remote_host.port,
            'type': _type,  # 7 webrdp  8 webvnc
            'address': self.scope['client'][0],
            'useragent': self.user_agent,
        }
        TerminalSession.objects.create(**data)

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)
            if close_code == 3001:
                pass
            else:
                self.guacamoleclient.close()
        except:
            pass
        finally:
            if self.guacamoleclient.res:
                try:
                    tmp = list(self.guacamoleclient.res)
                    self.guacamoleclient.res = []
                    if platform.system().lower() == 'linux':
                        celery_save_res_asciinema.delay(settings.MEDIA_ROOT + '/' + self.guacamoleclient.res_file, tmp, False)
                    else:
                        with open(settings.MEDIA_ROOT + '/' + self.guacamoleclient.res_file, 'a+') as f:
                            for line in tmp:
                                f.write('{}'.format(line))
                except:
                    pass

                try:
                    if platform.system().lower() == 'linux':
                        celery_save_terminal_log.delay(
                            self.session.get('username'),
                            self.remote_host.hostname,
                            self.remote_host.ip,
                            self.remote_host.get_protocol_display(),
                            self.remote_host.port,
                            self.remote_host.remote_user.username,
                            '',
                            self.guacamoleclient.res_file,
                            self.scope['client'][0],
                            self.user_agent,
                            self.start_time,
                        )
                    else:
                        terminal_log(
                            self.session.get('username'),
                            self.remote_host.hostname,
                            self.remote_host.ip,
                            self.remote_host.get_protocol_display(),
                            self.remote_host.port,
                            self.remote_host.remote_user.username,
                            '',
                            self.guacamoleclient.res_file,
                            self.scope['client'][0],
                            self.user_agent,
                            self.start_time,
                        )
                except:
                    pass
                
            TerminalSession.objects.filter(name=self.channel_name, group=self.group).delete()

    def receive(self, text_data=None, bytes_data=None):
        # print(text_data)
        if not self.lock:
            self.guacamoleclient.shell(text_data)
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
        except BaseException:
            pass

    # 会话外使用 channels.layers 设置 type 为 close.message 调用此函数
    def close_message(self, data):
        try:
            message = str(base64.b64encode('当前会话已被管理员关闭'.encode('utf-8')), 'utf-8')
            # 给客户端发送toastr警告
            # 需要在 guacamole/js/all.js 中自定义 toastr 的处理处理方法
            self.send('6.toastr,1.2,{0}.{1};'.format(len(message), message))
            self.close()
        except BaseException:
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
