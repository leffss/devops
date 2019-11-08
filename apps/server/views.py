from django.shortcuts import render, get_object_or_404
from util.tool import login_required
from .models import RemoteUserBindHost, RemoteUser, HostGroup
from user.models import User, Group
from webssh.models import TerminalSession
from django.db.models import Q
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
import json
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def index(request):
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        host_count = RemoteUserBindHost.objects.all().count()
        user_count = User.objects.all().count()
        group_count = Group.objects.all().count()
        session_count = TerminalSession.objects.all().count()
    else:
        host_count = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username'])
        ).distinct().count()
        user_count = User.objects.all().count()
        group_count = Group.objects.all().count()
        session_count = TerminalSession.objects.filter(user=request.session['username']).count()
    return render(request, 'server/index.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def hosts(request):
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        hosts = RemoteUserBindHost.objects.all()
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username'])
        ).distinct()
    return render(request, 'server/hosts.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def host(request, host_id):
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        host = get_object_or_404(
            RemoteUserBindHost,
            pk=host_id,
        )
    else:
        host = get_object_or_404(
            RemoteUserBindHost,
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            pk=host_id
        )
    try:
        host.serverdetail.filesystems = json.loads(host.serverdetail.filesystems)
        host.serverdetail.interfaces = json.loads(host.serverdetail.interfaces)
    except Exception:
        pass
    return render(request, 'server/host.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def host_edit(request, host_id):
    protocol_choices = (
        (1, 'ssh'),
        (2, 'telnet'),
        (3, 'rdp'),
        (4, 'vnc'),
        (5, 'sftp'),
        (6, 'ftp'),
    )
    type_choices = (
        (1, '服务器'),
        (2, '防火墙'),
        (3, '路由器'),
        (4, '二层交换机'),
        (5, '三层交换机'),
        (6, '虚拟机'),
        (7, 'PC机'),
    )
    env_choices = (
        (1, '正式环境'),
        (2, '测试环境'),
    )

    platform_choices = (
        (1, 'linux'),
        (2, 'windows'),
        (3, 'unix'),
    )
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        host = get_object_or_404(
            RemoteUserBindHost,
            pk=host_id
        )
    else:
        host = get_object_or_404(
            RemoteUserBindHost,
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            pk=host_id
        )
    other_users = RemoteUser.objects.exclude(pk=host.remote_user.id).exclude(
        remoteuserbindhost__ip=host.ip,
        remoteuserbindhost__protocol=host.protocol,
        remoteuserbindhost__port=host.port,
    )
    return render(request, 'server/host_edit.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def host_add(request):
    protocol_choices = (
        (1, 'ssh'),
        (2, 'telnet'),
        (3, 'rdp'),
        (4, 'vnc'),
        (5, 'sftp'),
        (6, 'ftp'),
    )
    type_choices = (
        (1, '服务器'),
        (2, '防火墙'),
        (3, '路由器'),
        (4, '二层交换机'),
        (5, '三层交换机'),
        (6, '虚拟机'),
        (7, 'PC机'),
    )
    env_choices = (
        (1, '正式环境'),
        (2, '测试环境'),
    )

    platform_choices = (
        (1, 'linux'),
        (2, 'windows'),
        (3, 'unix'),
    )

    all_users = RemoteUser.objects.all()
    return render(request, 'server/host_add.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def users(request):
    users = RemoteUser.objects.all()
    return render(request, 'server/users.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def user(request, user_id):
    user = get_object_or_404(RemoteUser, pk=user_id)
    return render(request, 'server/user.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def user_edit(request, user_id):
    user = get_object_or_404(RemoteUser, pk=user_id)
    return render(request, 'server/user_edit.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def user_add(request):
    return render(request, 'server/user_add.html')


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def groups(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    for group in groups:
        if request.session['issuperuser'] and request.session['username'] == 'admin':
            group.hosts = RemoteUserBindHost.objects.filter(
                Q(host_group__id=group.id),
                enabled=True
            ).distinct()
        else:
            group.hosts = RemoteUserBindHost.objects.filter(
                Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
                Q(host_group__id=group.id),
                enabled=True
            ).distinct()

    return render(request, 'server/groups.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def group(request, group_id):
    user = User.objects.get(id=int(request.session.get('userid')))
    group = get_object_or_404(HostGroup, pk=group_id, user=user)
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        group.hosts = RemoteUserBindHost.objects.filter(
            Q(host_group__id=group.id),
            enabled=True
        ).distinct()
    else:
        group.hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            Q(host_group__id=group.id),
            enabled=True
        ).distinct()
    return render(request, 'server/group.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def group_edit(request, group_id):
    user = User.objects.get(id=int(request.session.get('userid')))
    group = get_object_or_404(HostGroup, pk=group_id, user=user)
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        group.hosts = RemoteUserBindHost.objects.filter(
            Q(host_group__id=group.id),
            enabled=True
        ).distinct()
    else:
        group.hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            Q(host_group__id=group.id),
            enabled=True
        ).distinct()
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        other_hosts = RemoteUserBindHost.objects.filter(
            ~Q(host_group__id=group_id),
            enabled=True
        ).distinct()
    else:
        other_hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            ~Q(host_group__id=group_id),
            enabled=True
        ).distinct()
    return render(request, 'server/group_edit.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def group_add(request):
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        all_hosts = RemoteUserBindHost.objects.filter(enabled=True)
    else:
        all_hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            enabled=True
        ).distinct()
    return render(request, 'server/group_add.html', locals())
