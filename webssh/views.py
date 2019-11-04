from django.shortcuts import render, HttpResponse, get_object_or_404
from server.models import RemoteUserBindHost
from .models import TerminalLog, TerminalSession
from user.models import User
from util.tool import login_required, post_required, admin_required, gen_rand_char
from django.http import JsonResponse
from django.db.models import Q
from .forms import HostForm, SessionViewForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache
from django.conf import settings
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
import json
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def hosts(request):
    if request.session['issuperuser']:
        hosts = RemoteUserBindHost.objects.all()
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username'])
        ).distinct()
    return render(request, 'webssh/hosts.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def terminal(request):
    host_form = HostForm(request.POST)
    error_message = '请检查填写的内容!'
    if host_form.is_valid():
        host_id = host_form.cleaned_data.get('hostid')
        # host = RemoteUserBindHost.objects.get(id=host_id, enabled=True)
        # host = get_object_or_404(RemoteUserBindHost, id=host_id, enabled=True)
        username = request.session.get('username')
        if not request.session['issuperuser']:
            hosts = RemoteUserBindHost.objects.filter(
                Q(pk=host_id),
                Q(enabled=True),
                Q(user__username=username) | Q(group__user__username=username),
            ).distinct()
        else:
            hosts = RemoteUserBindHost.objects.filter(
                Q(pk=host_id),
                Q(enabled=True),
            ).distinct()
        if not hosts:
            error_message = '不存在的主机!'
            return JsonResponse({"code": 400, "error": error_message})
        else:
            host = hosts[0]
            return render(request, 'webssh/terminal.html', locals())

    return JsonResponse({"code": 406, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def terminal_cli(request):
    host_id = request.POST.get('hostid', None)
    username = request.session.get('username')
    # host = RemoteUserBindHost.objects.get(pk=host_id, enabled=True)
    # host = get_object_or_404(RemoteUserBindHost, id=host_id, enabled=True)
    if not request.session['issuperuser']:
        hosts = RemoteUserBindHost.objects.filter(
            Q(pk=host_id),
            Q(enabled=True),
            Q(user__username=username) | Q(group__user__username=username),
        ).distinct()
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(pk=host_id),
            Q(enabled=True),
        ).distinct()
    if not hosts:
        error_message = '不存在的主机!'
        return JsonResponse({"code": 400, "error": error_message})
    else:
        host = hosts[0]
    password = gen_rand_char(16)    # 生成随机密码
    terminal_type = 'ssh'
    key = '%s_%s_%s' % (terminal_type, username, password)
    key_ssh = '%s_%s_%s_ssh_count' % (terminal_type, username, password)
    key_sftp = '%s_%s_%s_sftp_count' % (terminal_type, username, password)

    # cache.set(key, host_id, timeout=60 * 60 * 24)  # 写入 redis 缓存以便 proxy_sshd 读取
    cache.set(key, {'host_id': host_id, 'issuperuser': request.session['issuperuser']}, timeout=60 * 60 * 24)

    # 用于限制随机密码ssh和sftp登陆次数
    cache.set(key_ssh, 1, timeout=60 * 60 * 24)  # 写入 redis 缓存以便 proxy_sshd 读取
    cache.set(key_sftp, 1, timeout=60 * 60 * 24)  # 写入 redis 缓存以便 proxy_sshd 读取
    user = User.objects.get(username=username)
    clissh = json.loads(user.setting)['clissh']
    ssh_app = None
    for i in clissh:
        if i['enable']:
            ssh_app = i
            break
    link_ssh = '{scheme}://%s %s' % (ssh_app['path'], ssh_app['args'])
    return HttpResponse(link_ssh.format(
        scheme='apploader',
        login_host=request.META['HTTP_HOST'].split(':')[0],
        port=settings.PROXY_SSHD.get('listen_port', 2222),
        login_user=username,
        login_passwd=password,
        host=host.ip,
        username=host.remote_user.username,
        hostname=host.hostname,
    ))


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def terminal_cli_sftp(request):
    username = request.session.get('username')
    host_id = request.POST.get('hostid', None)
    # host = RemoteUserBindHost.objects.get(pk=host_id, enabled=True)
    # host = get_object_or_404(RemoteUserBindHost, id=host_id, enabled=True)
    if not request.session['issuperuser']:
        hosts = RemoteUserBindHost.objects.filter(
            Q(pk=host_id),
            Q(enabled=True),
            Q(user__username=username) | Q(group__user__username=username),
        ).distinct()
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(pk=host_id),
            Q(enabled=True),
        ).distinct()
    if not hosts:
        error_message = '不存在的主机!'
        return JsonResponse({"code": 400, "error": error_message})
    else:
        host = hosts[0]
    password = gen_rand_char(16)    # 生成随机密码
    terminal_type = 'ssh'
    key = '%s_%s_%s' % (terminal_type, username, password)
    key_sftp = '%s_%s_%s_sftp_count' % (terminal_type, username, password)

    # cache.set(key, host_id, timeout=60 * 60 * 24)  # 写入 redis 缓存以便 proxy_sshd 读取
    cache.set(key, {'host_id': host_id, 'issuperuser': request.session['issuperuser']}, timeout=60 * 60 * 24)

    # 用于限制随机密码sftp登陆次数
    cache.set(key_sftp, 1, timeout=60 * 60 * 24)  # 写入 redis 缓存以便 proxy_sshd 读取
    user = User.objects.get(username=username)
    clisftp = json.loads(user.setting)['clisftp']
    sftp_app = None
    for i in clisftp:
        if i['enable']:
            sftp_app = i
            break
    link_sftp = '{scheme}://%s %s' % (sftp_app['path'], sftp_app['args'])
    return HttpResponse(link_sftp.format(
        scheme='apploader',
        login_host=request.META['HTTP_HOST'].split(':')[0],
        port=settings.PROXY_SSHD.get('listen_port', 2222),
        login_user=username,
        login_passwd=password,
        host=host.ip,
        username=host.remote_user.username,
        hostname=host.hostname,
    ))


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@admin_required
def logs(request):
    logs = TerminalLog.objects.all()
    return render(request, 'webssh/logs.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@admin_required
def sessions(request):
    sessions = TerminalSession.objects.all()
    return render(request, 'webssh/sessions.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
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


@ratelimit(key=key, rate=rate, method=ALL, block=True)
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


# 每次重启时清空在线会话表，好像使用 gunicorn 会多次加载
def cls_terminalsession():
    try:
        TerminalSession.objects.all().delete()
        logger.info('开始清空 TerminalSession 表')
    except Exception:
        pass


# cls_terminalsession()

