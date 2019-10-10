"""
基于 ansible v2.8.5 的 api，低于 v2.8 不适用
"""

import json
import shutil
import re
import traceback
import multiprocessing
from multiprocessing import cpu_count
from ansible.plugins.callback import CallbackBase  # 回调基类，处理ansible的成功失败信息，这部分对于二次开发自定义可以做比较多的自定义
from ansible import constants as C  # 用于获取ansible内置的一些常量
from ansible.module_utils.common.collections import ImmutableDict  # 用于自定制一些选项
from ansible import context  # 上下文管理器，他就是用来接收 ImmutableDict 的示例对象
from ansible.parsing.dataloader import DataLoader  # 解析 json/ymal/ini 格式的文件
from ansible.vars.manager import VariableManager  # 管理主机和主机组的变量
from ansible.playbook.play import Play  # 用于执行 Ad-hoc 的核心类，即ansible相关模块，命令行的ansible -m方式
from ansible.executor.task_queue_manager import TaskQueueManager  # ansible 底层用到的任务队列管理器
from ansible.executor.playbook_executor import PlaybookExecutor  # 执行 playbook 的核心类，即命令行的ansible-playbook *.yml
from ansible.inventory.manager import InventoryManager  # 管理资产文件（动态资产、静态资产）或者主机列表
from ansible.inventory.host import Host     # 单台主机类
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
channel_layer = get_channel_layer()


class CallbackModule(CallbackBase):
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
        print(result)
        self.host_unreachable.append({'host': result._host.name, 'task_name': result.task_name, 'result': result._result, 'success': False, 'msg': 'unreachable'})

    def v2_runner_on_ok(self, result, *args, **kwargs):
        print(result)
        self.host_ok.append({'host': result._host.name, 'task_name': result.task_name,  'result': result._result, 'success': True, 'msg': 'ok'})

    def v2_runner_on_failed(self, result, *args, **kwargs):
        print(result)
        self.host_failed.append({'host': result._host.name, 'task_name': result.task_name, 'result': result._result, 'success': False, 'msg': 'failed'})

    def v2_playbook_on_no_hosts_matched(self):
        self.error = 'skipping: No match hosts.'

    def get_res(self):
        return self.host_ok, self.host_failed, self.host_unreachable, self.error


class ModuleCallbackModule(CallbackBase):
    """
    回调函数
    """
    def __init__(self, group, cmd=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group = group
        self.cmd = cmd
        self.message = dict()

    def v2_runner_on_unreachable(self, result):
        if 'msg' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：不可达 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('msg').strip())
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：不可达 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })

    def v2_runner_on_ok(self, result, *args, **kwargs):
        if 'rc' in result._result and 'stdout' in result._result:
            if result._result['stderr']:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：成功 | 状态码：{rc} >> \n{stdout}\n{stderr}</code>'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip(),
                    stderr=result._result.get('stderr').strip())
            else:
                data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                    host=result._host.name, rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip())
        elif 'results' in result._result and 'rc' in result._result:
            data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('results')[0].strip())
        elif 'module_stdout' in result._result and 'rc' in result._result:
            data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：成功 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name, rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('module_stdout').strip())
        else:
            data = '<code style="color: #008000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：成功 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'stderr' in result._result:
            if result._result['stdout']:
                data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：失败 | 状态码：{rc} >> \n{stdout}\n{stderr}</code>'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stdout=result._result.get('stdout').strip(),
                    stderr=result._result.get('stderr').strip())
            else:
                data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：失败 | 状态码：{rc} >> \n{stderr}</code>'.format(
                    host=result._host.name,
                    rc=result._result.get('rc'),
                    ip=result._host.host_data['ip'],
                    user=result._host.host_data['username'],
                    cmd=self.cmd,
                    stderr=result._result.get('stderr').strip())
        elif 'module_stdout' in result._result:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：失败 | 状态码：{rc} >> \n{stdout}</code>'.format(
                host=result._host.name,
                rc=result._result.get('rc'),
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=result._result.get('module_stdout').strip())
        else:
            data = '<code style="color: #FF0000">主机：{host}_{ip}_{user} | 命令： {cmd} | 状态：失败 >> \n{stdout}</code>'.format(
                host=result._host.name,
                ip=result._host.host_data['ip'],
                user=result._host.host_data['username'],
                cmd=self.cmd,
                stdout=json.dumps(result._result, indent=4, ensure_ascii=False))
        self.message['status'] = 0
        self.message['message'] = data
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })

    def v2_playbook_on_no_hosts_matched(self):
        self.message['status'] = 0
        self.message['message'] = '<code style="color: #FF0000">skipping: No match hosts.</code>'
        message = json.dumps(self.message)
        async_to_sync(channel_layer.group_send)(self.group, {
            "type": "send.message",
            "text": message,
        })


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


class BaseHost(Host):
    """
    处理单个主机
    """
    def __init__(self, host_data):
        self.host_data = host_data
        hostname = host_data.get('hostname') or host_data.get('ip')
        port = host_data.get('port') or 22
        super().__init__(hostname, port)
        self.__set_required_variables()
        self.__set_extra_variables()

    def __set_required_variables(self):
        host_data = self.host_data
        self.set_variable('ansible_host', host_data['ip'])
        self.set_variable('ansible_port', host_data['port'])

        if host_data.get('username'):
            self.set_variable('ansible_user', host_data['username'])

        # 添加密码和秘钥
        if host_data.get('password'):
            self.set_variable('ansible_ssh_pass', host_data['password'])
        if host_data.get('private_key'):
            self.set_variable('ansible_ssh_private_key_file', host_data['private_key'])

        # 添加become支持
        become = host_data.get('become', False)
        if become:
            self.set_variable('ansible_become', True)
            self.set_variable('ansible_become_method', become.get('method', 'sudo'))
            self.set_variable('ansible_become_user', become.get('user', 'root'))
            self.set_variable('ansible_become_pass', become.get('pass', ''))
        else:
            self.set_variable('ansible_become', False)

    def __set_extra_variables(self):
        for k, v in self.host_data.get('vars', {}).items():
            self.set_variable(k, v)

    def __repr__(self):
        return self.name


class BaseInventory(InventoryManager):
    """
    生成Ansible inventory对象的
    """
    loader_class = DataLoader
    variable_manager_class = VariableManager
    host_manager_class = BaseHost

    def __init__(self, host_list=None):
        if host_list is None:
            host_list = []
        self.host_list = host_list
        assert isinstance(host_list, list)
        self.loader = self.loader_class()
        self.variable_manager = self.variable_manager_class()
        super().__init__(self.loader)

    def get_groups(self):
        return self._inventory.groups

    def get_group(self, name):
        return self._inventory.groups.get(name, None)

    def parse_sources(self, cache=False):
        group_all = self.get_group('all')
        ungrouped = self.get_group('ungrouped')

        for host_data in self.host_list:
            host = self.host_manager_class(host_data=host_data)
            self.hosts[host_data['hostname']] = host
            groups_data = host_data.get('groups')
            if groups_data:
                for group_name in groups_data:
                    group = self.get_group(group_name)
                    if group is None:
                        self.add_group(group_name)
                        group = self.get_group(group_name)
                    group.add_host(host)
            else:
                ungrouped.add_host(host)
            group_all.add_host(host)

    def get_matched_hosts(self, pattern):
        return self.get_hosts(pattern)


class AnsibleAPI:
    def __init__(self, check=False, remote_user='root', private_key_file=None, forks=cpu_count(),
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
        # constants里面可以找到这些参数，ImmutableDict代替了较老的版本的nametuple的方式
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
        # self.result_row = self.results_callback.result_row

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

    def run_cmd(self, cmds, hosts='all', group=None):
        """
        运行命令有三种 raw 、command 、shell
        1.command 模块不是调用的shell的指令，所以没有bash的环境变量
        2.raw很多地方和shell类似，更多的地方建议使用shell和command模块。
        3.但是如果是使用老版本python，需要用到raw，又或者是客户端是路由器，因为没有安装python模块，那就需要使用raw模块了
        """
        module_name = 'shell'
        self.run_module(module_name, cmds, hosts)
        if group:
            message = dict()
            message['status'] = 0
            message['message'] = '执行完毕...'
            message = json.dumps(message)
            async_to_sync(channel_layer.group_send)(group, {
                "type": "close.channel",
                "text": message,
            })

    def get_server_info(self, hosts='all'):
        """
        获取主机信息
        """
        self.run_module('setup', '', hosts)
        ok, failed, unreach, error = self.results_callback.get_res()
        infos = []
        if ok:
            for i in ok:
                info = dict()
                info['host'] = i['host']
                info['hostname'] = i['result']['ansible_facts']['ansible_hostname']
                info['cpu_model'] = i['result']['ansible_facts']['ansible_processor'][-1]
                info['cpu_number'] = int(i['result']['ansible_facts']['ansible_processor_count'])
                info['vcpu_number'] = int(i['result']['ansible_facts']['ansible_processor_vcpus'])
                info['kernel'] = i['result']['ansible_facts']['ansible_kernel']
                info['system'] = '{} {} {}'.format(i['result']['ansible_facts']['ansible_distribution'],
                                                   i['result']['ansible_facts']['ansible_distribution_version'],
                                                   i['result']['ansible_facts']['ansible_userspace_architecture'])
                info['server_model'] = i['result']['ansible_facts']['ansible_product_name']
                info['ram_total'] = round(int(i['result']['ansible_facts']['ansible_memtotal_mb']) / 1024)
                info['swap_total'] = round(int(i['result']['ansible_facts']['ansible_swaptotal_mb']) / 1024)
                info['disk_total'], disk_size = 0, 0
                for k, v in i['result']['ansible_facts']['ansible_devices'].items():
                    if k[0:2] in ['sd', 'hd', 'ss', 'vd']:
                        if 'G' in v['size']:
                            disk_size = float(v['size'][0: v['size'].rindex('G') - 1])
                        elif 'T' in v['size']:
                            disk_size = float(v['size'][0: v['size'].rindex('T') - 1]) * 1024
                        info['disk_total'] += round(disk_size, 2)
                info['filesystems'] = []
                for filesystem in i['result']['ansible_facts']['ansible_mounts']:
                    tmp = dict()
                    tmp['mount'] = filesystem['mount']
                    tmp['size_total'] = filesystem['size_total']
                    tmp['size_available'] = filesystem['size_available']
                    tmp['fstype'] = filesystem['fstype']
                    info['filesystems'].append(tmp)

                info['interfaces'] = []
                interfaces = i['result']['ansible_facts']['ansible_interfaces']
                for interface in interfaces:
                    # lvs 模式时 lo 也可能会绑定 IP 地址
                    if re.match(r"^(eth|bond|bind|eno|ens|em|ib)\d+?", interface) or interface == 'lo':
                        tmp = dict()
                        tmp['network_card_name'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get('device')
                        tmp['network_card_mac'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get('macaddress')
                        tmp['network_card_ipv4'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get(
                            'ipv4') if 'ipv4' in i['result']['ansible_facts'][
                            'ansible_{}'.format(interface)] else 'unknown'

                        tmp['network_card_ipv4_secondaries'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get(
                            'ipv4_secondaries') if 'ipv4_secondaries' in i['result']['ansible_facts'][
                            'ansible_{}'.format(interface)] else 'unknown'

                        tmp['network_card_ipv6'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get(
                            'ipv6') if 'ipv6' in i['result']['ansible_facts'][
                            'ansible_{}'.format(interface)] else 'unknown'

                        tmp['network_card_model'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get('type')
                        tmp['network_card_mtu'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get('mtu')
                        tmp['network_card_status'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get('active')
                        tmp['network_card_speed'] = i['result']['ansible_facts']['ansible_{}'.format(interface)].get('speed')
                        info['interfaces'].append(tmp)
                infos.append(info)
        return infos, failed, unreach, error

    def get_result(self):
        ok, failed, unreach, error = self.results_callback.get_res()

        if ok:
            print('ok-------------------start')
            # with open('/tmp/res.txt', 'a+') as f:
            #     for i in ok:
            #         f.write(json.dumps(i, indent=4))
            for i in ok:
                print(json.dumps(i, indent=4))
            print('ok-------------------end')

        if failed:
            print('failed-------------------start')
            for i in failed:
                print(json.dumps(i, indent=4))
            print('failed-------------------end')

        if unreach:
            print('unreach-------------------start')
            for i in unreach:
                print(json.dumps(i, indent=4))
            print('unreach-------------------end')

        if error:
            print('error-------------------start')
            print(error)
            print('error-------------------end')


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
    playbook_yml = './hello.yml'
    private_key_file = './id_rsa'
    remote_user = 'root'
    extra_vars = {
        'var': 'test'
    }
    inventory = BaseInventory(host_data)
    callback = CallbackModule()
    ansible_api = AnsibleAPI(
        private_key_file=private_key_file,
        extra_vars=extra_vars,
        remote_user=remote_user,
        dynamic_inventory=inventory,
        callback=callback,
        # forks=4,
    )

    # ansible_api.run_playbook(playbook_yml=playbook_yml)
    # ansible_api.run_module(module_name="shell", module_args="echo 'hello world!';echo $?", hosts="group1,group3")
    cmd = '. /etc/profile &> /dev/null; . ~/.bash_profile &> /dev/null; ip a;'
    ansible_api.run_module(module_name='shell', module_args=cmd, hosts='all')
    # ansible_api.run_cmd(cmds=cmd, hosts='k8s')
    # ansible_api.run_module(module_name='setup', module_args='', hosts='k8s')
    # ansible_api.get_server_info(hosts='lvs')
    # ansible_api.get_result()

