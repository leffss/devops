"""
基于 ansible v2.8.5 的 api，低于 v2.8 不适用
"""
import traceback
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
def gen_rand_char(length=10, chars='0123456789zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA'):
    return ''.join(random.sample(chars, length))


def convert_byte(byte):
    byte = int(byte)
    if byte <= 1024:
        return '{} B'.format(byte)
    elif 1024 < byte <= 1048576:
        return '{} KB'.format('%.2f' % (byte / 1024))
    elif 1048576 < byte <= 1073741824:
        return '{} MB'.format('%.2f' % (byte / 1024 / 1024))
    elif 1073741824 < byte <= 1099511627776:
        return '{} GB'.format('%.2f' % (byte / 1024 / 1024 / 1024))
    elif byte > 1099511627776:
        return '{} TB'.format('%.2f' % (byte / 1024 / 1024 / 1024 / 1024))


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
                        gen_rand_char(8) + '.txt'
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
                        gen_rand_char(8) + '.txt'
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

