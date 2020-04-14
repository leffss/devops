from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from server.models import RemoteUserBindHost
from user.models import User
from django.db.models import Q
from asgiref.sync import async_to_sync
from util.tool import gen_rand_char
from tasks.tasks import task_run_cmd, task_run_script, task_run_file, task_run_playbook, task_run_module
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


def get_hosts(issuperuser, ids, username):
    if issuperuser and username == 'admin':
        return RemoteUserBindHost.objects.filter(
                        Q(enabled=True),
                        Q(id__in=ids.split(',')),
                ).distinct()
    else:
        return RemoteUserBindHost.objects.filter(
            Q(enabled=True),
            Q(user__username=username) | Q(group__user__username=username),
            Q(id__in=ids.split(',')),
        ).distinct()


class Cmd(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = 'session_' + gen_rand_char()
        self.session = dict()
        self.message = dict()
        self.client = None
        self.user_agent = None
        self.is_running = False

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

        if '批量命令' not in self.session[settings.INIT_PERMISSION]['titles']:    # 判断权限
            self.message['status'] = 1
            self.message['message'] = '无权限'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "close.channel",
                "text": message,
            })

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

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)  # 退出组
        except Exception:
            pass

    def receive(self, text_data=None, bytes_data=None):
        if self.is_running:
            self.message['status'] = 1
            self.message['message'] = '当前通道已有任务在执行'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "send.message",
                "text": message,
            })
        else:
            self.is_running = True
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
                hosts = get_hosts(self.session.get('issuperuser', False), data['hosts'], self.session['username'])
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
                    cmd=data['cmd'],
                    user=self.session.get('username'),
                    user_agent=self.user_agent,
                    client=self.client,
                    issuperuser=True if '登陆后su跳转超级用户' in self.session[settings.INIT_PERMISSION]['titles'] else False,
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
            logger.error("send message error: {0}".format(traceback.format_exc()))

    def close_channel(self, data):
        try:
            self.send(data['text'])
            time.sleep(0.3)
            self.close()
        except Exception:
            logger.error("close channel error: {0}".format(traceback.format_exc()))


class Script(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = 'session_' + gen_rand_char()
        self.session = dict()
        self.message = dict()
        self.client = None
        self.user_agent = None
        self.is_running = False

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

        if '批量脚本' not in self.session[settings.INIT_PERMISSION]['titles']:    # 判断权限
            self.message['status'] = 1
            self.message['message'] = '无权限'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "close.channel",
                "text": message,
            })

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

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)  # 退出组
        except Exception:
            print(traceback.format_exc())

    def receive(self, text_data=None, bytes_data=None):
        if self.is_running:
            self.message['status'] = 1
            self.message['message'] = '当前通道已有任务在执行'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "send.message",
                "text": message,
            })
        else:
            self.is_running = True
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
            if data.get('hosts', None) and data.get('script', None) and data.get('script_name', None):
                hosts = get_hosts(self.session.get('issuperuser', False), data['hosts'], self.session['username'])
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
                task_run_script.delay(
                    hosts=ansible_hosts, group=self.group,
                    data=data,
                    user=self.session.get('username'),
                    user_agent=self.user_agent,
                    client=self.client,
                    issuperuser=True if '登陆后su跳转超级用户' in self.session[settings.INIT_PERMISSION]['titles'] else False,
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


class File(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = 'session_' + gen_rand_char()
        self.session = dict()
        self.message = dict()
        self.client = None
        self.user_agent = None
        self.is_running = False

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

        if '上传文件' not in self.session[settings.INIT_PERMISSION]['titles']:    # 判断权限
            self.message['status'] = 1
            self.message['message'] = '无权限'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "close.channel",
                "text": message,
            })

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

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)  # 退出组
        except Exception:
            print(traceback.format_exc())

    def receive(self, text_data=None, bytes_data=None):
        if self.is_running:
            self.message['status'] = 1
            self.message['message'] = '当前通道已有任务在执行'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "send.message",
                "text": message,
            })
        else:
            self.is_running = True
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
            if ('hosts' in data) and ('src' in data) and ('dst' in data) and ('backup' in data):
                if not data['src'].startswith(settings.TMP_ROOT):
                    self.message['status'] = 1
                    self.message['message'] = '无权限的源文件'
                    message = json.dumps(self.message)
                    async_to_sync(self.channel_layer.group_send)(self.group, {
                        "type": "close.channel",
                        "text": message,
                    })
                hosts = get_hosts(self.session.get('issuperuser', False), data['hosts'], self.session['username'])
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
                task_run_file.delay(
                    hosts=ansible_hosts, group=self.group,
                    data=data,
                    user=self.session.get('username'),
                    user_agent=self.user_agent,
                    client=self.client,
                    issuperuser=True if '登陆后su跳转超级用户' in self.session[settings.INIT_PERMISSION]['titles'] else False,
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


class Playbook(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = 'session_' + gen_rand_char()
        self.session = dict()
        self.message = dict()
        self.client = None
        self.user_agent = None
        self.is_running = False

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

        if 'playbook' not in self.session[settings.INIT_PERMISSION]['titles']:    # 判断权限
            self.message['status'] = 1
            self.message['message'] = '无权限'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "close.channel",
                "text": message,
            })

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

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)  # 退出组
        except Exception:
            print(traceback.format_exc())

    def receive(self, text_data=None, bytes_data=None):
        if self.is_running:
            self.message['status'] = 1
            self.message['message'] = '当前通道已有任务在执行'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "send.message",
                "text": message,
            })
        else:
            self.is_running = True
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
            if data.get('hosts', None) and data.get('playbook', None) and data.get('playbook_name', None):
                hosts = get_hosts(self.session.get('issuperuser', False), data['hosts'], self.session['username'])
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
                    user = User.objects.get(id=int(self.session.get('userid')))
                    hostinfo['groups'] = [x.group_name for x in host.host_group.filter(user=user)]
                    if host.remote_user.enabled:
                        hostinfo['superusername'] = host.remote_user.superusername
                        hostinfo['superpassword'] = host.remote_user.superpassword
                    else:
                        hostinfo['superusername'] = None
                    ansible_hosts.append(hostinfo)
                task_run_playbook.delay(
                    hosts=ansible_hosts, group=self.group,
                    data=data,
                    user=self.session.get('username'),
                    user_agent=self.user_agent,
                    client=self.client,
                    issuperuser=True if '登陆后su跳转超级用户' in self.session[settings.INIT_PERMISSION]['titles'] else False,
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


class Module(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = 'session_' + gen_rand_char()
        self.session = dict()
        self.message = dict()
        self.client = None
        self.user_agent = None
        self.is_running = False

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

        if 'module' not in self.session[settings.INIT_PERMISSION]['titles']:    # 判断权限
            self.message['status'] = 1
            self.message['message'] = '无权限'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "close.channel",
                "text": message,
            })

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

    def disconnect(self, close_code):
        try:
            async_to_sync(self.channel_layer.group_discard)(self.group, self.channel_name)  # 退出组
        except Exception:
            print(traceback.format_exc())

    def receive(self, text_data=None, bytes_data=None):
        if self.is_running:
            self.message['status'] = 1
            self.message['message'] = '当前通道已有任务在执行'
            message = json.dumps(self.message)
            async_to_sync(self.channel_layer.group_send)(self.group, {
                "type": "send.message",
                "text": message,
            })
        else:
            self.is_running = True
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
            if data.get('hosts', None) and data.get('module', None):
                hosts = get_hosts(self.session.get('issuperuser', False), data['hosts'], self.session['username'])
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
                task_run_module.delay(
                    hosts=ansible_hosts, group=self.group,
                    data=data,
                    user=self.session.get('username'),
                    user_agent=self.user_agent,
                    client=self.client,
                    issuperuser=True if '登陆后su跳转超级用户' in self.session[settings.INIT_PERMISSION]['titles'] else False,
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
