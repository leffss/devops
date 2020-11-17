from devops.celery import app
from util.ansible_api import AnsibleAPI
from util.callback import SetupCallbackModule, ModuleCallbackModule, CopyCallbackModule, PlayBookCallbackModule
from util.inventory import BaseInventory
from server.models import RemoteUserBindHost, ServerDetail
from webssh.models import TerminalLog, TerminalSession
from user.models import LoginLog
from batch.models import BatchCmdLog
from scheduler.models import SchedulerHost
from django.conf import settings
from datetime import datetime, timedelta
import json
import traceback
import os
import time
import random
import requests
import urllib3
urllib3.disable_warnings()


# 生成随机字符串
def gen_rand_char(length=16, chars='0123456789zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA'):
    return ''.join(random.sample(chars, length))


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
def task_run_cmd(hosts, group, cmd, user, user_agent, client, issuperuser=False):
    host_data = list()
    _hosts = ''
    for host in hosts:
        _hosts += '{}_{}_{}\n'.format(host['hostname'], host['ip'], host['username'])
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
    callback = ModuleCallbackModule(group, cmd=cmd, user=user, user_agent=user_agent, client=client, _hosts=_hosts)
    ansible_api = AnsibleAPI(
        dynamic_inventory=inventory,
        callback=callback
    )
    ansible_api.run_cmd(cmds=cmd, hosts='all', group=group)


@app.task()
def task_run_script(hosts, group, data, user, user_agent, client, issuperuser=False):
    host_data = list()
    _hosts = ''
    for host in hosts:
        _hosts += '{}_{}_{}\n'.format(host['hostname'], host['ip'], host['username'])
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
    callback = ModuleCallbackModule(group, cmd=data['script_name'], user=user, user_agent=user_agent, client=client, _hosts=_hosts)
    ansible_api = AnsibleAPI(
        dynamic_inventory=inventory,
        callback=callback
    )
    path = data.get('path', '/tmp')
    if path == '':
        path = '/tmp'
    exec = data.get('exec', '')
    script_name = data.get('script_name', '')
    script = data.get('script', '')

    now = time.time()
    tmp_date = time.strftime("%Y-%m-%d", time.localtime(int(now)))
    if not os.path.isdir(os.path.join(settings.SCRIPT_ROOT, tmp_date)):
        os.makedirs(os.path.join(settings.SCRIPT_ROOT, tmp_date))
    script_file = settings.SCRIPT_DIR + '/' + tmp_date + '/' + gen_rand_char(16) + '_' + script_name
    res_file = settings.MEDIA_ROOT + '/' + script_file
    with open(res_file, 'w+') as f:
        f.write(script)
    cmds = '{}'.format(res_file)
    cmds = cmds + ' ' + 'chdir={}'.format(path)
    if exec:
        cmds = cmds + ' ' + 'executable={}'.format(exec)
    else:
        if script_name.split('.')[-1] == 'py':
            cmds = cmds + ' ' + 'executable=/usr/bin/python'
        elif script_name.split('.')[-1] == 'pl':
            cmds = cmds + ' ' + 'executable=/usr/bin/perl'
        elif script_name.split('.')[-1] == 'rb':
            cmds = cmds + ' ' + 'executable=/usr/bin/ruby'
    ansible_api.run_script(cmds=cmds, hosts='all', group=group, script=script_file)


@app.task()
def task_run_playbook(hosts, group, data, user, user_agent, client, issuperuser=False):
    host_data = list()
    _hosts = ''
    for host in hosts:
        _hosts += '{}_{}_{}\n'.format(host['hostname'], host['ip'], host['username'])
        hostinfo = dict()
        hostinfo['hostname'] = host['hostname']
        hostinfo['ip'] = host['ip']
        hostinfo['port'] = host['port']
        hostinfo['username'] = host['username']
        hostinfo['password'] = host['password']
        hostinfo['groups'] = host['groups'] if host['groups'] else None
        if issuperuser:
            if host['superusername']:
                hostinfo['become'] = {
                    'method': 'su',
                    'user': host['superusername'],
                    'pass': host['superpassword']
                }
        host_data.append(hostinfo)
    inventory = BaseInventory(host_data)
    callback = PlayBookCallbackModule(group, playbook=data['playbook_name'], user=user, user_agent=user_agent,
                                      client=client, _hosts=_hosts)
    ansible_api = AnsibleAPI(
        dynamic_inventory=inventory,
        callback=callback
    )
    playbook_name = data.get('playbook_name', '')
    playbook = data.get('playbook', '')
    now = time.time()
    tmp_date = time.strftime("%Y-%m-%d", time.localtime(int(now)))
    if not os.path.isdir(os.path.join(settings.SCRIPT_ROOT, tmp_date)):
        os.makedirs(os.path.join(settings.SCRIPT_ROOT, tmp_date))
    script_file = settings.SCRIPT_DIR + '/' + tmp_date + '/' + gen_rand_char(16) + '_' + playbook_name
    playbook_file = settings.MEDIA_ROOT + '/' + script_file
    with open(playbook_file, 'w+') as f:
        f.write(playbook)
    ansible_api.run_playbook(playbook_yml=playbook_file, group=group, script=script_file)


@app.task()
def task_run_module(hosts, group, data, user, user_agent, client, issuperuser=False):
    host_data = list()
    _hosts = ''
    for host in hosts:
        _hosts += '{}_{}_{}\n'.format(host['hostname'], host['ip'], host['username'])
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
    module = data.get('module', 'command')
    args = data.get('args', '')
    cmd = 'module: {0} args: {1}'.format(module, args)
    callback = ModuleCallbackModule(group, cmd=cmd, user=user, user_agent=user_agent, client=client, _hosts=_hosts)
    ansible_api = AnsibleAPI(
        dynamic_inventory=inventory,
        callback=callback
    )
    ansible_api.run_modules(cmds=args, module=module, hosts='all', group=group)


@app.task()
def task_run_file(hosts, group, data, user, user_agent, client, issuperuser=False):
    host_data = list()
    _hosts = ''
    for host in hosts:
        _hosts += '{}_{}_{}\n'.format(host['hostname'], host['ip'], host['username'])
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
    src = data.get('src')
    dst = data.get('dst', '/tmp')
    if dst == '':
        dst = '/tmp'
    backup = data.get('backup', True)
    cmds = 'src={} dest={} backup={} decrypt=False'.format(src, dst, backup)
    inventory = BaseInventory(host_data)
    callback = CopyCallbackModule(group, src=src, dst=dst, user=user, user_agent=user_agent, client=client, _hosts=_hosts)
    ansible_api = AnsibleAPI(
        dynamic_inventory=inventory,
        callback=callback
    )
    ansible_api.run_copy(cmds=cmds, hosts='all', group=group)


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
def task_check_scheduler(id=None, retry=2, timeout=5):
    if id:
        scheduler_hosts = SchedulerHost.objects.filter(id=id)
    else:
        scheduler_hosts = SchedulerHost.objects.all()
    headers = dict()
    headers['user-agent'] = 'requests/devops'
    for scheduler_host in scheduler_hosts:
        headers['AUTHORIZATION'] = scheduler_host.token
        attempts = 0
        success = False
        while attempts <= retry and not success:
            try:
                url = '{protocol}://{ip}:{port}{url}'.format(
                    protocol=scheduler_host.get_protocol_display(), ip=scheduler_host.ip,
                    port=scheduler_host.port, url='/'
                )
                res = requests.get(
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    allow_redirects=True,
                    verify=False,
                )
                if res.status_code == 200:
                    scheduler_host.status = True
                    scheduler_host.save()
                    success = True
                else:
                    attempts += 1
            except Exception as e:
                print(str(e))
                # print(traceback.format_exc())
                attempts += 1
        if not success:
            scheduler_host.status = False
            scheduler_host.save()


@app.task()
def task_cls_terminalsession():
    try:
        TerminalSession.objects.all().delete()
    except Exception:
        print(traceback.format_exc())


@app.task()
def task_cls_user_logs(keep_days=365):
    try:
        LoginLog.objects.filter(create_time__lt=datetime.now() - timedelta(days=keep_days)).delete()
    except Exception:
        print(traceback.format_exc())


@app.task()
def task_cls_terminal_logs(keep_days=365):
    try:
        TerminalLog.objects.filter(create_time__lt=datetime.now() - timedelta(days=keep_days)).delete()
    except Exception:
        print(traceback.format_exc())


@app.task()
def task_cls_batch_logs(keep_days=365):
    try:
        BatchCmdLog.objects.filter(create_time__lt=datetime.now() - timedelta(days=keep_days)).delete()
    except Exception:
        print(traceback.format_exc())


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
