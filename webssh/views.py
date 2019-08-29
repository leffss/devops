from django.shortcuts import render, HttpResponse
from server.models import RemoteUserBindHost
from .models import TerminalLog, TerminalSession
from util.tool import login_required, post_required, admin_required
from django.http import JsonResponse
from django.db.models import Q
from .forms import HostForm, SessionViewForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from util.tool import gen_rand_char
from django.core.cache import cache
from django.conf import settings
# Create your views here.


@login_required
def hosts(request):
    if request.session['issuperuser']:
        hosts = RemoteUserBindHost.objects.all()
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username'])
        ).distinct()
    return render(request, 'webssh/hosts.html', locals())


@login_required
@post_required
def terminal(request):
    host_form = HostForm(request.POST)
    error_message = '请检查填写的内容!'
    if host_form.is_valid():
        host_id = host_form.cleaned_data.get('hostid')
        host = RemoteUserBindHost.objects.get(id=host_id)
        return render(request, 'webssh/terminal.html', locals())

    return JsonResponse({"code": 406, "err": error_message})


@login_required
@post_required
def terminal_cli(request):
    host_id = request.POST.get('hostid', None)
    username = request.session.get('username')
    password = gen_rand_char(16)    # 生成随机密码
    terminal_type = 'ssh'
    key = '%s_%s_%s' % (terminal_type, username, password)
    key_ssh = '%s_%s_%s_ssh_count' % (terminal_type, username, password)
    key_sftp = '%s_%s_%s_sftp_count' % (terminal_type, username, password)
    cache.set(key, host_id, timeout=60 * 60 * 24)  # 写入 redis 缓存以便 proxy_sshd 读取
    # 用于限制随机密码ssh和sftp登陆次数
    cache.set(key_ssh, 1, timeout=60 * 60 * 24)  # 写入 redis 缓存以便 proxy_sshd 读取
    cache.set(key_sftp, 1, timeout=60 * 60 * 24)  # 写入 redis 缓存以便 proxy_sshd 读取
    # Xshell.exe" ssh://网站用户:临时密码@堡垒机:端口 -newtab SSH用户/SSH主机
    # link = '{scheme}://{user}:{passwd}@{cmdb}:{port}\\" \\"-newtab\\" \\"{username}/{host}\\"'
    host = RemoteUserBindHost.objects.get(pk=host_id)

    link_crt_ssh = '{scheme}://C:\\Program Files\\VanDyke Software\\Clients\\SecureCRT.exe /T /N "{username}@{host}" /SSH2 /L {user} /PASSWORD {passwd} {cmdb} /P {port}'
    link_xshell_ssh = '{scheme}://C:\\Program Files (x86)\\NetSarang\\Xmanager Enterprise 5\\Xshell.exe -newtab "{username}@{host}" -url ssh://{user}:{passwd}@{cmdb}:{port}'
    link_putty_ssh = '{scheme}://C:\\Users\\xx\\AppData\\Roaming\\TP4A\\Teleport-Assist\\tools\\putty\\putty.exe -l {user} -pw {passwd} {cmdb} -P {port}'
    link_winscp_sftp = '{scheme}://C:\\Users\\xx\\AppData\\Roaming\\TP4A\\Teleport-Assist\\tools\\winscp\\WinSCP.exe /sessionname="{username}@{host}" {user}:{passwd}@{cmdb}:{port}'

    clissh = 'link_xshell_ssh'

    if clissh == 'link_crt_ssh':
        return HttpResponse(link_crt_ssh.format(
            scheme='apploader',
            cmdb=request.META['HTTP_HOST'].split(':')[0],
            port=settings.PROXY_SSHD.get('listen_port', 2222),
            user=username,
            passwd=password,
            host=host.ip,
            username=host.remote_user.username,
        ))
    elif clissh == 'link_xshell_ssh':
        return HttpResponse(link_xshell_ssh.format(
            scheme='apploader',     # 自定义的网页调用外部软件(xshell)协议
            cmdb=request.META['HTTP_HOST'].split(':')[0],  # xshell连接主机(cmdb堡垒机代理)
            port=settings.PROXY_SSHD.get('listen_port', 2222),
            user=username,  # xshell连接主机的用户(cmdb堡垒机代理)
            passwd=password,
            host=host.ip,  # xshell标签显示连接的主机(后端SSH实际主机)
            username=host.remote_user.username,  # xshell标签显示连接的用户(后端SSH实际用户)
        ))
    elif clissh == 'link_winscp_sftp':
        return HttpResponse(link_winscp_sftp.format(
            scheme='apploader',
            cmdb=request.META['HTTP_HOST'].split(':')[0],
            port=settings.PROXY_SSHD.get('listen_port', 2222),
            user=username,
            passwd=password,
            host=host.ip,
            username=host.remote_user.username,
        ))
    elif clissh in ('link_putty_ssh'):
        return HttpResponse(link_putty_ssh.format(
            scheme='apploader',
            cmdb=request.META['HTTP_HOST'].split(':')[0],
            port=settings.PROXY_SSHD.get('listen_port', 2222),
            user=username,
            passwd=password,
            host=host.ip,
            username=host.remote_user.username,
        ))


@login_required
@admin_required
def logs(request):
    logs = TerminalLog.objects.all()
    return render(request, 'webssh/logs.html', locals())


@login_required
@admin_required
def test(request):
    log = TerminalLog.objects.get(pk=219)
    return render(request, 'webssh/test.html', locals())


@login_required
@admin_required
def sessions(request):
    sessions = TerminalSession.objects.all()
    return render(request, 'webssh/sessions.html', locals())


@login_required
@admin_required
@post_required
def terminal_view(request):
    sessionview_form = SessionViewForm(request.POST)
    error_message = '请检查填写的内容!'
    if sessionview_form.is_valid():
        name = sessionview_form.cleaned_data.get('sessionname')
        group = sessionview_form.cleaned_data.get('group')
        session = TerminalSession.objects.get(name=name, group=group)
        return render(request, 'webssh/terminal_view.html', locals())

    return JsonResponse({"code": 406, "err": error_message})


@login_required
@admin_required
@post_required
def terminal_clissh_view(request):
    sessionview_form = SessionViewForm(request.POST)
    error_message = '请检查填写的内容!'
    if sessionview_form.is_valid():
        name = sessionview_form.cleaned_data.get('sessionname')
        group = sessionview_form.cleaned_data.get('group')
        session = TerminalSession.objects.get(name=name, group=group)
        return render(request, 'webssh/terminal_clissh_view.html', locals())

    return JsonResponse({"code": 406, "err": error_message})


# 每次重启时清空在线会话表
def cls_terminalsession():
    try:
        TerminalSession.objects.all().delete()
    except:
        pass
    

cls_terminalsession()
