"""
基于 ansible v2.8.5 的 api，低于 v2.8 不适用
"""
from ansible.parsing.dataloader import DataLoader  # 解析 json/ymal/ini 格式的文件
from ansible.vars.manager import VariableManager  # 管理主机和主机组的变量
from ansible.inventory.manager import InventoryManager  # 管理资产文件（动态资产、静态资产）或者主机列表
from ansible.inventory.host import Host     # 单台主机类
from django.conf import settings
from util.crypto import decrypt
from ansible.plugins.connection import ConnectionBase


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

        # 设置 connection 插件连接方式
        self.set_variable('ansible_connection', settings.ANSIBLE_CONNECTION_TYPE)

        # ssh 连接参数，提升速度， 仅到连接插件为 ssh 时生效，paramiko 模式下不生效
        if settings.ANSIBLE_CONNECTION_TYPE == 'ssh':
            self.set_variable('ansible_ssh_args', '-C -o ControlMaster=auto -o ControlPersist=60s')

        # self.set_variable('ansible_host_key_checking', False)
        self.set_variable('ansible_ssh_host_key_checking', False)
        self.set_variable('ansible_host', host_data['ip'])
        self.set_variable('ansible_port', host_data['port'])

        if host_data.get('username'):
            self.set_variable('ansible_user', host_data['username'])

        # 添加密码和秘钥
        if host_data.get('password'):
            self.set_variable('ansible_ssh_pass', decrypt(host_data['password']))
        if host_data.get('private_key'):
            self.set_variable('ansible_ssh_private_key_file', host_data['private_key'])

        if settings.ANSIBLE_CONNECTION_TYPE == 'ssh':
            self.set_variable('ansible_ssh_pipelining', True)

        # 添加become支持
        become = host_data.get('become', False)
        if become:
            self.set_variable('ansible_become', True)
            self.set_variable('ansible_become_method', become.get('method', 'sudo'))
            if become.get('method', 'sudo') == 'sudo':
                if settings.ANSIBLE_CONNECTION_TYPE == 'ssh':
                    # ansible_ssh_pipelining 可以加快执行速度，但是不兼容 sudo，仅到连接插件为 ssh 时生效，paramiko 不生效
                    self.set_variable('ansible_ssh_pipelining', False)
            self.set_variable('ansible_become_user', become.get('user', 'root'))
            self.set_variable('ansible_become_pass', decrypt(become.get('pass', '')))
        else:
            self.set_variable('ansible_become', False)

    def __set_extra_variables(self):
        for k, v in self.host_data.get('vars', {}).items():
            self.set_variable(k, v)

    def __repr__(self):
        return self.name


class BaseInventory(InventoryManager):
    """
    生成 Ansible inventory 对象
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
