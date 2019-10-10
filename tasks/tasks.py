from devops.celery import app
from util.ansible_api import BaseInventory, AnsibleAPI, SetupCallbackModule, ModuleCallbackModule
from server.models import RemoteUserBindHost, ServerDetail
from webssh.models import TerminalLog
from user.models import LoginLog
import json
import traceback


@app.task()
def task_host_update_info(hostinfo):
    try:
        if hostinfo['platform'] in ['linux', 'unix']:
            host_data = [
                {
                    'hostname': hostinfo['hostname'],
                    'ip': hostinfo['ip'],
                    'port': hostinfo['port'],
                    'username': hostinfo['username'],
                    'password': hostinfo['password']
                }
            ]
            if hostinfo['superusername']:
                host_data[0]['become'] = {
                    'method': 'su',
                    'user': hostinfo['superusername'],
                    'pass': hostinfo['superpassword']
                }
            inventory = BaseInventory(host_data)
            callback = SetupCallbackModule()
            ansible_api = AnsibleAPI(
                dynamic_inventory=inventory,
                callback=callback
            )
            server_info, failed, unreach, error = ansible_api.get_server_info(hosts='all')
            if server_info:
                host = RemoteUserBindHost.objects.get(pk=hostinfo['id'])
                data = {
                    'server': host,
                    'cpu_model': server_info[0]['cpu_model'],
                    'cpu_number': server_info[0]['cpu_number'],
                    'vcpu_number': server_info[0]['vcpu_number'],
                    'disk_total': server_info[0]['disk_total'],
                    'ram_total': server_info[0]['ram_total'],
                    'swap_total': server_info[0]['swap_total'],
                    'kernel': server_info[0]['kernel'],
                    'system': server_info[0]['system'],
                    'filesystems': json.dumps(server_info[0]['filesystems']),
                    'interfaces': json.dumps(server_info[0]['interfaces']),
                    'server_model': server_info[0]['server_model'],
                }
                try:
                    ServerDetail.objects.create(**data)
                except Exception:
                    del data['server']
                    ServerDetail.objects.filter(server=host).update(**data)
            else:
                if failed:
                    for i in failed:
                        print(json.dumps(i, indent=4))
                if unreach:
                    for i in unreach:
                        print(json.dumps(i, indent=4))
                if error:
                    for i in error:
                        print(json.dumps(i, indent=4))
    except Exception:
        print(traceback.format_exc())


@app.task()
def task_run_cmd(hosts, group, cmd, issuperuser=False):
    host_data = list()
    for host in hosts:
        hostinfo = dict()
        hostinfo['hostname'] = host['hostname']
        hostinfo['ip'] = host['ip']
        hostinfo['port'] = host['port']
        hostinfo['username'] = host['username']
        hostinfo['password'] = host['password']
        if issuperuser:
            if host['superusername']:
                hostinfo['become'] = {
                    'method': 'su',
                    'user': host['superusername'],
                    'pass': host['superpassword']
                }
        host_data.append(hostinfo)
    inventory = BaseInventory(host_data)
    callback = ModuleCallbackModule(group=group, cmd=cmd)
    ansible_api = AnsibleAPI(
        dynamic_inventory=inventory,
        callback=callback
    )
    ansible_api.run_cmd(cmds=cmd, hosts='all', group=group)


@app.task(ignore_result=True)
def task_save_res(res_file, res, enter=True):
    if enter:
        with open(res_file, 'a+') as f:
            for line in res:
                f.write('{}\n'.format(line))
    else:
        with open(res_file, 'a+') as f:
            for line in res:
                f.write('{}'.format(line))


@app.task(ignore_result=True)
def task_save_terminal_log(user, hostname, ip, protocol, port, username, cmd, detail, address, useragent, start_time):
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


@app.task(ignore_result=True)
def task_save_event_log(user, event_type, detail, address, useragent):
    event = LoginLog()
    event.user = user
    event.event_type = event_type
    event.detail = detail
    event.address = address
    event.useragent = useragent
    event.save()


@app.task()
def task_test():
    host_data = [
        {
            'hostname': 'k8s1',
            'ip': '192.168.223.111',
            'port': 22,
            'username': 'root',
            'password': '123456',
            'groups': ['k8s'],
        },
        {
            'hostname': 'k8s2',
            'ip': '192.168.223.112',
            'port': 22,
            'username': 'leffss',
            'password': '123456',
            'groups': ['k8s'],
            'become': {
                'method': 'su',
                'user': 'root',
                'pass': '123456',
            },
        },
        {
            'hostname': 'k8s3',
            'ip': '192.168.223.113',
            'port': 22,
            'username': 'leffss',
            'password': '123456',
            'private_key': '/tmp/private_key',
            'become': {
                'method': 'sudo',
                'user': 'root',
                'pass': None,
            },
            'groups': ['k8s', 'server'],
            'vars': {'love': 'yes', 'test': 'no'},
        },
    ]
    private_key_file = './id_rsa'
    remote_user = 'root'
    extra_vars = {
        'var': 'test'
    }
    inventory = BaseInventory(host_data)
    ansible_api = AnsibleAPI(
        private_key_file=private_key_file,
        extra_vars=extra_vars,
        remote_user=remote_user,
        dynamic_inventory=inventory,
        # forks=4,
    )
    playbook_yml = '/home/workspace/devops/util/hello.yml'
    ansible_api.run_playbook(playbook_yml=playbook_yml)
    # ansible_api.run_module(module_name='setup', module_args='', hosts='k8s')
    # ansible_api.run_module(module_name='shell', module_args='echo "1" >> /tmp/test.txt', hosts='k8s')
    ansible_api.get_result()

