"""
基于 ansible v2.8.5 的 api，低于 v2.8 不适用，经测试兼容 v2.9
"""
import os
import json
import shutil
import re
import traceback
import random
from multiprocessing import cpu_count
from ansible import constants as C  # 用于获取ansible内置的一些常量
from ansible.module_utils.common.collections import ImmutableDict  # 用于自定制一些选项
from ansible import context  # 上下文管理器，他就是用来接收 ImmutableDict 的示例对象
from ansible.parsing.dataloader import DataLoader  # 解析 json/ymal/ini 格式的文件
from ansible.vars.manager import VariableManager  # 管理主机和主机组的变量
from ansible.playbook.play import Play  # 用于执行 Ad-hoc 的核心类，即ansible相关模块，命令行的ansible -m方式
from ansible.executor.task_queue_manager import TaskQueueManager  # ansible 底层用到的任务队列管理器
# 执行 playbook 的核心类，即命令行的ansible-playbook *.yml
from ansible.executor.playbook_executor import PlaybookExecutor
from util.inventory import BaseInventory
from util.callback_test import PlayBookCallbackModule


# 生成随机字符串
def gen_rand_char(length=10, chars='0123456789zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA'):
    return ''.join(random.sample(chars, length))


class AnsibleAPI:
    def __init__(self, check=False, remote_user='root', private_key_file=None, forks=cpu_count() * 2,
                 extra_vars=None, dynamic_inventory=None, callback=None):
        """
        可以选择性的针对业务场景在初始化中加入用户定义的参数
        """
        # 运行前检查，即命令行的-C
        self.check = check
        # key登陆文件
        self.private_key_file = private_key_file
        # 并发连接数
        self.forks = forks
        # 远端登陆用户
        self.remote_user = remote_user
        # 数据解析器
        self.loader = DataLoader()
        # 必须有此参数，假如通过了公钥信任，可以为空dict
        self.passwords = {}
        # 回调结果
        self.results_callback = callback
        # 组和主机相关，处理动态资产
        self.dynamic_inventory = dynamic_inventory
        # 变量管理器
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.dynamic_inventory)
        self.variable_manager._extra_vars = extra_vars if extra_vars is not None else {}
        # 自定义选项的初始化
        self.__init_options()

    def __init_options(self):
        """
        自定义选项，不用默认值的话可以加入到__init__的参数中
        """
        # ansible.constants 里面可以找到这些初始化参数，ImmutableDict 代替了老的版本（v2.7之前）的 nametuple 的方式，不兼容
        context.CLIARGS = ImmutableDict(
            connection='smart',
            remote_user=self.remote_user,
            ack_pass=None,
            sudo=True,
            sudo_user='root',
            ask_sudo_pass=False,
            module_path=None,
            become=True,
            become_method='sudo',
            become_user='root',
            check=self.check,
            listhosts=None,
            listtasks=None,
            listtags=None,
            syntax=None,
            diff=True,
            subset=None,
            timeout=15,
            private_key_file=self.private_key_file,
            host_key_checking=False,
            forks=self.forks,
            ssh_common_args='-o StrictHostKeyChecking=no',
            ssh_extra_args='-o StrictHostKeyChecking=no',
            verbosity=0,
            start_at_task=None,
        )

    def run_playbook(self, playbook_yml):
        """
        运行 playbook
        """
        playbook = None
        try:
            playbook = PlaybookExecutor(
                playbooks=[playbook_yml],
                inventory=self.dynamic_inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
            )
            playbook._tqm._stdout_callback = self.results_callback
            playbook.run()
        except Exception:
            print(traceback.format_exc())
        finally:
            if playbook._tqm is not None:
                playbook._tqm.cleanup()


    def run_module(self, module_name, module_args, hosts='all'):
        """
        运行 module
        """
        play_source = dict(
            name='Ansible Run Module',
            hosts=hosts,
            gather_facts='no',
            tasks=[
                {'action': {'module': module_name, 'args': module_args}},
            ]
        )
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=self.dynamic_inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                passwords=self.passwords,
                stdout_callback=self.results_callback,
            )
            tqm.run(play)
            # self.result_row = self.results_callback.result_row
        except Exception:
            print(traceback.format_exc())
        finally:
            # try:
            #     message = dict()
            #     message['status'] = 0
            #     message['message'] = '执行关闭'
            #     message = json.dumps(message)
            #     async_to_sync(channel_layer.group_send)(self.group, {
            #         "type": "send.message",
            #         "text": message,
            #     })
            # except:
            #     pass
            if tqm is not None:
                tqm.cleanup()
            # 这个临时目录会在 ~/.ansible/tmp/ 目录下
            shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)


if __name__ == '__main__':
    host_data = [
        {
            'hostname': 'k8s1',
            'ip': '192.168.223.111',
            'port': 22,
            'username': 'root',
            'password': '123456',
            'groups': ['k8s', 'test'],
        },
        {
            'hostname': 'k8s2',
            'ip': '192.168.223.112',
            'port': 22,
            'username': 'root',
            'password': '123456',
            'groups': ['k8s'],
        },
        {
            'hostname': 'k8s3',
            'ip': '192.168.223.113',
            'port': 22,
            'username': 'root',
            'password': '123456',
            'groups': ['k8s'],
        },
        {
            'hostname': 'k8s1_test',
            'ip': '192.168.223.111',
            'port': 22,
            'username': 'test',
            'password': '123456',
            'groups': ['k8s'],
            'become': {
                'method': 'su',
                'user': 'root',
                'pass': '123456',
            },
        },
        {
            'hostname': 'testserver',
            'ip': '8.8.8.8',
            'port': 2222,
            'username': 'root',
            'password': 'password',
            'private_key': '/tmp/private_key',
            'become': {
                'method': 'sudo',
                'user': 'root',
                'pass': None,
            },
            'groups': ['group1', 'group2'],
            'vars': {'love': 'yes'},
        },
    ]
    playbook_yml = '/home/workspace/devops/util/hello.yml'
    private_key_file = './id_rsa'
    remote_user = 'root'
    extra_vars = {
        'var': 'test'
    }
    inventory = BaseInventory(host_data)
    callback = PlayBookCallbackModule('saddasd', cmd='xx', user='admin', user_agent='admin',
                                       client='192.168.223.1', _hosts='192.168.223.111')
    ansible_api = AnsibleAPI(
        # private_key_file=private_key_file,
        # extra_vars=extra_vars,
        # remote_user=remote_user,
        dynamic_inventory=inventory,
        callback=callback,
        # forks=4,
    )

    ansible_api.run_playbook(playbook_yml=playbook_yml)
