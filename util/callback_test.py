"""
基于 ansible v2.8.5 的 api，低于 v2.8 不适用
"""
import traceback
import os
import sys
import time
import json
import random
# 回调基类，处理ansible的成功失败信息，这部分对于二次开发自定义可以做比较多的自定义
from ansible.plugins.callback import CallbackBase


class PlayBookCallbackModule(CallbackBase):
    def __init__(self, group, cmd, user, user_agent, client, _hosts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.cmd = cmd
        self.user = user
        self.user_agent = user_agent
        self.client = client
        self.hosts = _hosts
        self.message = dict()
        self.res = []
        self.start_time = time.time()
        self.last_save_time = self.start_time
        self.is_setup = False

    def v2_runner_on_unreachable(self, result):
        if 'msg' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=result._result.get('msg').strip())
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
        print(data)


    def v2_runner_on_ok(self, result, *args, **kwargs):
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
                else:
                    data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                        host=result._host.name, rc=result._result.get('rc'),
                        ip=result._host.host_data['ip'],
                        user=result._host.host_data['username'],
                        stdout=result._result.get('stdout').strip())
            elif 'results' in result._result and 'rc' in result._result:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('results')[0].strip())
            elif 'module_stdout' in result._result and 'rc' in result._result:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('module_stdout').strip())
            else:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 状态：成功 >> \n{stdout}</code>'.format(
                    host=result._host.name,
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
            print(data)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'stderr' in result._result:
            if result._result['stdout']:
                data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \n{stdout}\n{stderr}</code>'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stdout=result._result.get('stdout').strip(),
                    stderr=result._result.get('stderr').strip())
            else:
                data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \n{stderr}</code>'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    stderr=result._result.get('stderr').strip())
        elif 'module_stdout' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：失败 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name,
                rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=result._result.get('module_stdout').strip())
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 状态：失败 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
        print(data)

    def v2_playbook_on_no_hosts_matched(self):
        data = '<code style="color: #FF0000">跳过：没有匹配的主机</code>'
        print(data)

    def v2_playbook_on_play_start(self, play):
        name = play.get_name().strip()
        if not name:
            data = format('<code style="color: #FFFFFF">PLAY', '*<150') + '</code>'
        else:
            data = format(f'<code style="color: #FFFFFF">PLAY [{name}]', '*<150') + '</code>'
        print(data)

    def v2_playbook_on_task_start(self, task, is_conditional):
        if task.get_name() == 'Gathering Facts':
            self.is_setup = True
        else:
            self.is_setup = False
        data = format(f'<code style="color: #FFFFFF">TASK [{task.get_name()}]', '*<150') + '</code>'
        print(data)

    def v2_runner_on_skipped(self, result):
        if 'changed' in result._result:
            del result._result['changed']
        data = '<code style="color: #FFFF00">[{}_{}_{}]=> {}: {}</code>'.format(
            result._host.name,
            result._host.host_data['ip'],
            result._host.host_data['username'],
            '跳过',
            self._dump_results(result._result)
        )
        print(data)

    def v2_playbook_on_stats(self, stats):
        hosts = sorted(stats.processed.keys())
        data = format('<code style="color: #FFFFFF">PLAY RECAP ', '*<150') + '</code>'
        print(data)
        for h in hosts:
            s = stats.summarize(h)
            data = '<code style="color: #FFFFFF">{} : ok={} changed={} unreachable={} failed={} skipped={}</code>'.format(
                h, s['ok'], s['changed'], s['unreachable'], s['failures'], s['skipped'])
            print(data)

    def v2_playbook_on_notify(self, handler, host):
        print('call v2_playbook_on_notify')
        self.playbook_on_notify(host, handler)

    def v2_playbook_on_handler_task_start(self, task):
        print('call v2_playbook_on_handler_task_start')
        print(task)
