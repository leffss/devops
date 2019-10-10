from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.http.request import QueryDict
from django.utils.six import StringIO
import django.utils.timezone as timezone
from devops.settings import TMP_DIR
from server.models import RemoteUserBindHost
from webssh.models import TerminalSession
from django.db.models import Q
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from util.tool import gen_rand_char, terminal_log, res
from tasks.tasks import task_run_cmd
import os
import json
import time
import traceback
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


try:
    session_exipry_time = settings.CUSTOM_SESSION_EXIPRY_TIME
except Exception:
    session_exipry_time = 60 * 30


class Cmd(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = 'session_' + gen_rand_char()
        self.session = dict()
        self.message = dict()

    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)(self.group, self.channel_name)  # 加入组
        self.session = self.scope.get('session', dict())
        if not self.session.get('islogin', None):    # 未登录直接断开 websocket 连接
            self.message['status'] = 1
            self.message['message'] = '未登录'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "close.channel",
                "text": message,
            })

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)  # 退出组
        except Exception:
            print(traceback.format_exc())

    def receive(self, text_data=None, bytes_data=None):
        data = dict()
        try:
            data = json.loads(text_data)
        except Exception:
            self.message['status'] = 1
            self.message['message'] = '提交的数据格式错误'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "close.channel",
                "text": message,
            })
        if data.get('hosts', None) and data.get('cmd', None):
            if self.session.get('issuperuser', None):
                hosts = RemoteUserBindHost.objects.filter(
                    Q(id__in=data['hosts'].split(',')),
                )
            else:
                hosts = RemoteUserBindHost.objects.filter(
                    Q(user__username=self.session['username']) | Q(
                        group__user__username=self.session['username']),
                    Q(id__in=data['hosts'].split(',')),
                )
            if not hosts:
                self.message['status'] = 1
                self.message['message'] = '未找到主机'
                message = json.dumps(self.message)
                async_to_sync(self.channel_layer.group_send)(self.group, {
                    "type": "close.channel",
                    "text": message,
                })

            ansible_hosts = list()
            for host in hosts:
                hostinfo = dict()
                hostinfo['id'] = host.id
                hostinfo['hostname'] = host.hostname
                hostinfo['ip'] = host.ip
                hostinfo['port'] = host.port
                hostinfo['username'] = host.remote_user.username
                hostinfo['password'] = host.remote_user.password
                if host.remote_user.enabled:
                    hostinfo['superusername'] = host.remote_user.superusername
                    hostinfo['superpassword'] = host.remote_user.superpassword
                else:
                    hostinfo['superusername'] = None
                ansible_hosts.append(hostinfo)
            task_run_cmd.delay(
                hosts=ansible_hosts, group=self.group,
                cmd=data['cmd'], issuperuser=self.session.get('issuperuser', False)
            )  # 执行

        else:
            self.message['status'] = 1
            self.message['message'] = '提交的数据格式错误'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "close.channel",
                "text": message,
            })

    def send_message(self, data):
        try:
            self.send(data['text'])
        except Exception:
            print(traceback.format_exc())

    def close_channel(self, data):
        try:
            self.send(data['text'])
            time.sleep(0.3)
            self.close()
        except Exception:
            print(traceback.format_exc())

