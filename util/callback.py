"""
基于 ansible v2.8.5 的 api，低于 v2.8 不适用
"""
import os
import sys
import time
import json
import random
from django.conf import settings
import django.utils.timezone as timezone
# 回调基类，处理ansible的成功失败信息，这部分对于二次开发自定义可以做比较多的自定义
from ansible.plugins.callback import CallbackBase
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()


# 生成随机字符串
def gen_rand_char(length=16, chars='0123456789zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA'):
    return ''.join(random.sample(chars, length))


def convert_byte(byte, digits=2):
    byte = int(byte)
    if byte <= 1024:
        return '{} B'.format(byte)
    elif 1024 < byte <= 1048576:
        return '{} KB'.format('%.{0}f'.format(digits) % (byte / 1024))
    elif 1048576 < byte <= 1073741824:
        return '{} MB'.format('%.{0}f'.format(digits) % (byte / 1024 / 1024))
    elif 1073741824 < byte <= 1099511627776:
        return '{} GB'.format('%.{0}f'.format(digits) % (byte / 1024 / 1024 / 1024))
    elif byte > 1099511627776:
        return '{} TB'.format('%.{0}f'.format(digits) % (byte / 1024 / 1024 / 1024 / 1024))


def save_res(res_file, res):
    with open(settings.MEDIA_ROOT + '/' + res_file, 'a+') as f:
        for line in res:
            f.write('{}\n'.format(line))


class CallbackModule(CallbackBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_ok = []
        self.host_unreachable = []
        self.host_failed = []
        self.error = ''

    def v2_runner_on_unreachable(self, result):
        print(result)
        self.host_unreachable.append({'host': result._host.name, 'task_name': result.task_name,
                                      'result': result._result, 'success': False, 'msg': 'unreachable'})

    def v2_runner_on_ok(self, result, *args, **kwargs):
        print(result)
        self.host_ok.append({'host': result._host.name, 'task_name': result.task_name,
                             'result': result._result, 'success': True, 'msg': 'ok'})

    def v2_runner_on_failed(self, result, *args, **kwargs):
        print(result)
        self.host_failed.append({'host': result._host.name, 'task_name': result.task_name,
                                 'result': result._result, 'success': False, 'msg': 'failed'})

    def v2_playbook_on_no_hosts_matched(self):
        self.error = 'skipping: No match hosts.'

    def get_res(self):
        return self.host_ok, self.host_failed, self.host_unreachable, self.error


class CopyCallbackModule(CallbackBase):
    def __init__(self, group, src, dst, user, user_agent, client, _hosts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.src = src
        self.dst = dst
        self.user = user
        self.user_agent = user_agent
        self.client = client
        self.hosts = _hosts
        self.start_time_django = timezone.now()
        self.message = dict()
        self.res = []
        self.start_time = time.time()
        self.last_save_time = self.start_time
        tmp_date1 = time.strftime("%Y-%m-%d", time.localtime(int(self.start_time)))
        tmp_date2 = time.strftime("%Y%m%d%H%M%S", time.localtime(int(self.start_time)))
        if not os.path.isdir(os.path.join(settings.RECORD_ROOT, tmp_date1)):
            os.makedirs(os.path.join(settings.RECORD_ROOT, tmp_date1))
        self.res_file = settings.RECORD_DIR + '/' + tmp_date1 + '/' + 'batch_' + tmp_date2 + '_' + \
                        gen_rand_char(16) + '.txt'
        self.res.append(    # 结果保存为asciinema格式，以便更方便的回放
            json.dumps(
                {
                    "version": 2,
                    "width": 250,  # 设置足够宽，以便播放时全屏不至于显示错乱
                    "height": 40,
                    "timestamp": int(self.start_time),
                    "env": {"SHELL": "/bin/sh", "TERM": "linux"}
                }
            )
        )

    def v2_runner_on_unreachable(self, result):
        if 'msg' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stdout=result._result.get('msg').strip())
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：不可达 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stdout=result._result.get('msg').strip().replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：不可达 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        if 'changed' in result._result:
            if 'backup_file' in result._result:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：成功 | changed: {changed} >> \n{stdout}</code>'.format(
                    host=result._host.name,
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    src=self.src.split('/')[-1],
                    dst=self.dst,
                    stdout='大小: {}  远程备份: {}'.format(convert_byte(result._result.get('size')), result._result.get('backup_file')),
                    changed=result._result.get('changed'),
                )
                data2 = '\033[01;32m主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：成功 | changed: {changed} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                    host=result._host.name,
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    src=self.src.split('/')[-1],
                    dst=self.dst,
                    stdout='大小: {}  远程备份: {}'.format(convert_byte(result._result.get('size')), result._result.get('backup_file')),
                    changed=result._result.get('changed'),
                )
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2]))
            else:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：成功 | changed: {changed} >> \n{stdout}</code>'.format(
                    host=result._host.name,
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    src=self.src.split('/')[-1],
                    dst=self.dst,
                    stdout='大小: {}'.format(convert_byte(result._result.get('size'))),
                    changed=result._result.get('changed'),
                )
                data2 = '\033[01;32m主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：成功 | changed: {changed} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                    host=result._host.name,
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    src=self.src.split('/')[-1],
                    dst=self.dst,
                    stdout='大小: {}'.format(convert_byte(result._result.get('size'))),
                    changed=result._result.get('changed'),
                )
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2]))
        else:
            data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：成功 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            data2 = '\033[01;32m主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：成功 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'msg' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：失败 >> \n{stderr}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stderr=result._result.get('msg').strip())
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：失败 >> \r\n{stderr}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stderr=result._result.get('msg').strip().replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：失败 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 上传： {src} --> {dst} | 状态：失败 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                src=self.src.split('/')[-1],
                dst=self.dst,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)


class ModuleCallbackModule(CallbackBase):
    def __init__(self, group, cmd, user, user_agent, client, _hosts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.cmd = cmd
        self.user = user
        self.user_agent = user_agent
        self.client = client
        self.hosts = _hosts
        self.start_time_django = timezone.now()
        self.message = dict()
        self.res = []
        self.start_time = time.time()
        self.last_save_time = self.start_time
        tmp_date1 = time.strftime("%Y-%m-%d", time.localtime(int(self.start_time)))
        tmp_date2 = time.strftime("%Y%m%d%H%M%S", time.localtime(int(self.start_time)))
        if not os.path.isdir(os.path.join(settings.RECORD_ROOT, tmp_date1)):
            os.makedirs(os.path.join(settings.RECORD_ROOT, tmp_date1))
        self.res_file = settings.RECORD_DIR + '/' + tmp_date1 + '/' + 'batch_' + tmp_date2 + '_' + \
                        gen_rand_char(16) + '.txt'
        self.res.append(    # 结果保存为asciinema格式，以便更方便的回放
            json.dumps(
                {
                    "version": 2,
                    "width": 250,  # 设置足够宽，以便播放时全屏不至于显示错乱
                    "height": 40,
                    "timestamp": int(self.start_time),
                    "env": {"SHELL": "/bin/sh", "TERM": "linux"}
                }
            )
        )

    def v2_runner_on_unreachable(self, result):
        if 'msg' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('msg').strip())
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：不可达 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('msg').strip().replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：不可达 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        if 'rc' in result._result and 'stdout' in result._result:
            if result._result['stderr']:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 | 状态码：{rc} >> \n{stdout}\n{stderr}</code>'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip(),
                    stderr=result._result.get('stderr').strip())
                data2 = '\033[01;32m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 | 状态码：{rc} >> \r\n{stdout}\033[0m\r\n\033[01;31m{stderr}\r\n\r\n\033[0m'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip().replace('\n', '\r\n'),
                    stderr=result._result.get('stderr').strip().replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
            else:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip())
                data2 = '\033[01;32m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 | 状态码：{rc} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip().replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        elif 'results' in result._result and 'rc' in result._result:
            data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('results')[0].strip())
            data2 = '\033[01;32m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 | 状态码：{rc} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name, rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('results')[0].strip().replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        elif 'module_stdout' in result._result and 'rc' in result._result:
            data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('module_stdout').strip())
            data2 = '\033[01;32m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 | 状态码：{rc} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name, rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('module_stdout').strip().replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        else:
            data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            data2 = '\033[01;32m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：成功 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        self.message['status'] = 0
        # 执行 script 模块时会提示多余的 'Shared connection to xxx.xxx.xxx.xxx closed.' 原因未知
        self.message['message'] = data.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'stderr' in result._result:
            if result._result['stdout']:
                data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：失败 | 状态码：{rc} >> \n{stdout}\n{stderr}</code>'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip(),
                    stderr=result._result.get('stderr').strip())
                data2 = '\033[01;31m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：失败 | 状态码：{rc} >> \r\n{stdout}\r\n{stderr}\r\n\r\n\033[0m'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip().replace('\n', '\r\n'),
                    stderr=result._result.get('stderr').strip().replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
            else:
                data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：失败 | 状态码：{rc} >> \n{stderr}</code>'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stderr=result._result.get('stderr').strip())
                data2 = '\033[01;31m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：失败 | 状态码：{rc} >> \r\n{stderr}\r\n\r\n\033[0m'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stderr=result._result.get('stderr').strip().replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        elif 'module_stdout' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：失败 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name,
                rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('module_stdout').strip())
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：失败 | 状态码：{rc} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('module_stdout').strip().replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：失败 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 命令/脚本： {cmd} | 状态：失败 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        self.message['status'] = 0
        self.message['message'] = data.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)


class SetupCallbackModule(CallbackBase):
    """
    回调函数
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_ok = []
        self.host_unreachable = []
        self.host_failed = []
        self.error = ''

    def v2_runner_on_unreachable(self, result):
        self.host_unreachable.append({'host': result._host.name, 'task_name': result.task_name, 'result': result._result, 'success': False, 'msg': 'unreachable'})

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.host_ok.append({'host': result._host.name, 'task_name': result.task_name,  'result': result._result, 'success': True, 'msg': 'ok'})

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.host_failed.append({'host': result._host.name, 'task_name': result.task_name, 'result': result._result, 'success': False, 'msg': 'failed'})

    def get_res(self):
        return self.host_ok, self.host_failed, self.host_unreachable, self.error


class PlayBookCallbackModule(CallbackBase):
    def __init__(self, group, playbook, user, user_agent, client, _hosts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.playbook = playbook
        self.user = user
        self.user_agent = user_agent
        self.client = client
        self.hosts = _hosts
        self.hosts2 = {}    # v2_playbook_on_stats 函数使用
        self.start_time_django = timezone.now()
        self.message = dict()
        self.res = []
        self.start_time = time.time()
        self.last_save_time = self.start_time
        tmp_date1 = time.strftime("%Y-%m-%d", time.localtime(int(self.start_time)))
        tmp_date2 = time.strftime("%Y%m%d%H%M%S", time.localtime(int(self.start_time)))
        if not os.path.isdir(os.path.join(settings.RECORD_ROOT, tmp_date1)):
            os.makedirs(os.path.join(settings.RECORD_ROOT, tmp_date1))
        self.res_file = settings.RECORD_DIR + '/' + tmp_date1 + '/' + 'batch_' + tmp_date2 + '_' + \
                        gen_rand_char(16) + '.txt'
        self.res.append(    # 结果保存为asciinema格式，以便更方便的回放
            json.dumps(
                {
                    "version": 2,
                    "width": 250,  # 设置足够宽，以便播放时全屏不至于显示错乱
                    "height": 40,
                    "timestamp": int(self.start_time),
                    "env": {"SHELL": "/bin/sh", "TERM": "linux"}
                }
            )
        )
        self.is_setup = False

    def v2_runner_on_unreachable(self, result):
        self.hosts2[result._host.name] = '{host}_{ip}_{user}'.format(
            host=result._host.name,
            ip=result._host.host_data['ip'],
            user=result._host.host_data['username']
        )
        if 'msg' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=result._result.get('msg').strip())
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 状态：不可达 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=result._result.get('msg').strip().replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 状态：不可达 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        self.hosts2[result._host.name] = '{host}_{ip}_{user}'.format(
            host=result._host.name,
            ip=result._host.host_data['ip'],
            user=result._host.host_data['username']
        )
        if self.is_setup:
            # playbook 默认会运行 setup 模块，速度较慢，如无需要可以关闭，这里不显示结果
            pass
        else:
            if 'rc' in result._result and 'stdout' in result._result:
                if result._result['stderr']:
                    data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \n{stdout}\n{stderr}</code>'.format(
                        host=result._host.name, rc=result._result.get('rc'),
                        ip=result._host.host_data['ip'],
                        user=result._host.host_data['username'],
                        stdout=result._result.get('stdout').strip(),
                        stderr=result._result.get('stderr').strip())
                    data2 = '\033[01;32m主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \r\n{stdout}\033[0m\r\n\033[01;31m{stderr}\r\n\r\n\033[0m'.format(
                        host=result._host.name, rc=result._result.get('rc'),
                        ip=result._host.host_data['ip'],
                        user=result._host.host_data['username'],
                        stdout=result._result.get('stdout').strip().replace('\n', '\r\n'),
                        stderr=result._result.get('stderr').strip().replace('\n', '\r\n'))
                    delay = round(time.time() - self.start_time, 6)
                    self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
                else:
                    data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                        host=result._host.name, rc=result._result.get('rc'),
                        ip=result._host.host_data['ip'],
                        user=result._host.host_data['username'],
                        stdout=result._result.get('stdout').strip())
                    data2 = '\033[01;32m主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                        host=result._host.name, rc=result._result.get('rc'),
                        ip=result._host.host_data['ip'],
                        user=result._host.host_data['username'],
                        stdout=result._result.get('stdout').strip().replace('\n', '\r\n'))
                    delay = round(time.time() - self.start_time, 6)
                    self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
            elif 'results' in result._result and 'rc' in result._result:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('results')[0].strip())
                data2 = '\033[01;32m主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('results')[0].strip().replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
            elif 'module_stdout' in result._result and 'rc' in result._result:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('module_stdout').strip())
                data2 = '\033[01;32m主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('module_stdout').strip().replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
            else:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 >> \n{stdout}</code>'.format(
                    host=result._host.name,
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
                data2 = '\033[01;32m主机：{host}_{ip}_{user} | 状态：成功 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                    host=result._host.name,
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
            self.message['status'] = 0
            # 执行 script 模块时会提示多余的 'Shared connection to xxx.xxx.xxx.xxx closed.' 原因未知
            self.message['message'] = data.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')
            message = json.dumps(self.message)
            async_to_sync(channel_layer.group_send)(self.group, {
                "type": "send.message",
                "text": message,
            })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        self.hosts2[result._host.name] = '{host}_{ip}_{user}'.format(
            host=result._host.name,
            ip=result._host.host_data['ip'],
            user=result._host.host_data['username']
        )
        if 'stderr' in result._result:
            if result._result['stdout']:
                data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \n{stdout}\n{stderr}</code>'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('stdout').strip(),
                    stderr=result._result.get('stderr').strip())
                data2 = '\033[01;31m主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \r\n{stdout}\r\n{stderr}\r\n\r\n\033[0m'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('stdout').strip().replace('\n', '\r\n'),
                    stderr=result._result.get('stderr').strip().replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
            else:
                data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \n{stderr}</code>'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stderr=result._result.get('stderr').strip())
                data2 = '\033[01;31m主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \r\n{stderr}\r\n\r\n\033[0m'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stderr=result._result.get('stderr').strip().replace('\n', '\r\n'))
                delay = round(time.time() - self.start_time, 6)
                self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        elif 'module_stdout' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name,
                rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=result._result.get('module_stdout').strip())
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=result._result.get('module_stdout').strip().replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：失败 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            data2 = '\033[01;31m主机：{host}_{ip}_{user} | 状态：失败 >> \r\n{stdout}\r\n\r\n\033[0m'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False).replace('\n', '\r\n'))
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')]))
        self.message['status'] = 0
        self.message['message'] = data.replace('Shared connection to {} closed.'.format(result._host.host_data['ip']), '')
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        # 指定条结果或者指定秒数或者占用指定内存就保存一次
        if len(self.res) > 100 or int(time.time() - self.last_save_time) > 60 or \
                sys.getsizeof(self.res) > 20971752:
            tmp = list(self.res)
            self.res = []
            self.last_save_time = time.time()
            save_res(self.res_file, tmp)

    def v2_playbook_on_no_hosts_matched(self):
        data = '<code style="color: #FF0000">没有匹配到主机，请确保 playbook 中 hosts 设置正确的值</code>'
        data2 = '\033[01;31m没有匹配到主机，请确保 playbook 中 hosts 设置正确的值\r\n\r\n\033[0m'
        delay = round(time.time() - self.start_time, 6)
        self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })

    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            data = format('<code style="color: #FFFFFF">PLAY', '*<150') + '</code>'
            data2 = format('PLAY', '*<150') + ' \r\n\r\n'
        else:
            data = format(f'<code style="color: #FFFFFF">PLAY [{name}]', '*<150') + '</code>'
            data2 = format(f'PLAY [{name}]', '*<150') + ' \r\n\r\n'
        delay = round(time.time() - self.start_time, 6)
        self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })

    def v2_playbook_on_task_start(self, task, is_conditional):
        if task.get_name() == 'Gathering Facts':
            self.is_setup = True
        else:
            self.is_setup = False
        data = format(f'<code style="color: #FFFFFF">TASK [{task.get_name()}]', '*<150') + '</code>'
        data2 = format(f'TASK [{task.get_name()}]', '*<150') + ' \r\n\r\n'
        delay = round(time.time() - self.start_time, 6)
        self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })

    def v2_runner_on_skipped(self, result):
        self.hosts2[result._host.name] = '{host}_{ip}_{user}'.format(
            host=result._host.name,
            ip=result._host.host_data['ip'],
            user=result._host.host_data['username']
        )
        if 'changed' in result._result:
            del result._result['changed']
        data = '<code style="color: #FFFF00">[{}_{}_{}]=> {}: {}</code>'.format(
            result._host.name,
            result._host.host_data['ip'],
            result._host.host_data['username'],
            '跳过',
            self._dump_results(result._result)
        )
        data2 = '[{}_{}_{}]=> {}: {}\r\n\r\n'.format(
            result._host.name,
            result._host.host_data['ip'],
            result._host.host_data['username'],
            '跳过',
            self._dump_results(result._result)
        )
        delay = round(time.time() - self.start_time, 6)
        self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        data = format('<code style="color: #FFFFFF">PLAY RECAP ', '*<150') + '</code>'
        data2 = format('PLAY RECAP ', '*<150') + '\r\n\r\n'
        delay = round(time.time() - self.start_time, 6)
        self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
        for h in hosts:
            s = stats.summarize(h)
            data = '<code style="color: #FFFFFF">{} : ok={} changed={} unreachable={} failed={} skipped={}</code>'.format(
                self.hosts2[h], s['ok'], s['changed'], s['unreachable'], s['failures'], s['skipped'])
            data2 = '{} : ok={} changed={} unreachable={} failed={} skipped={}\r\n\r\n'.format(
                self.hosts2[h], s['ok'], s['changed'], s['unreachable'], s['failures'], s['skipped'])
            delay = round(time.time() - self.start_time, 6)
            self.res.append(json.dumps([delay, 'o', data2]))
            self.message['status'] = 0
            self.message['message'] = data
            message = json.dumps(self.message)
            async_to_sync(channel_layer.group_send)(self.group, {
                "type": "send.message",
                "text": message,
            })

    def v2_playbook_on_handler_task_start(self, task):
        data = format(f'<code style="color: #FFFFFF">RUNNING HANDLER [{task.get_name()}]', '*<150') + '</code>'
        data2 = format(f'RUNNING HANDLER [{task.get_name()}]', '*<150') + ' \r\n\r\n'
        delay = round(time.time() - self.start_time, 6)
        self.res.append(json.dumps([delay, 'o', data2]))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })
