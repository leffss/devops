from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.http import JsonResponse
from util.tool import login_required, post_required, event_log
from .models import RemoteUser, RemoteUserBindHost, HostGroup
from user.models import User
from .forms import ChangeUserForm, AddUserForm, ChangeHostForm, AddHostForm, AddGroupForm, ChangeGroupForm
from tasks.tasks import task_host_update_info
from django.db.models import Q
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
from util.crypto import encrypt
import traceback
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def user_update(request):
    changeuser_form = ChangeUserForm(request.POST)
    if changeuser_form.is_valid():
        log_user = request.session.get('username')
        userid = changeuser_form.cleaned_data.get('userid')
        username = changeuser_form.cleaned_data.get('username')
        password = changeuser_form.cleaned_data.get('password')
        domain = changeuser_form.cleaned_data.get('domain', None)
        memo = changeuser_form.cleaned_data.get('memo')
        enabled = changeuser_form.cleaned_data.get('enabled')
        superusername = changeuser_form.cleaned_data.get('superusername', None)
        superpassword = changeuser_form.cleaned_data.get('superpassword', None)
        if enabled:
            if not superusername or not superpassword:
                error_message = '超级用户或者超级密码不能为空!'
                return JsonResponse({"code": 400, "err": error_message})
            
        data = {
            'username': username,
            'password': encrypt(password),
            'domain': domain,
            'memo': memo,
            'enabled': enabled,
            'superusername': superusername,
            'superpassword': encrypt(superpassword) if superpassword else superpassword,
        }
        try:
            user = User.objects.get(username=log_user)
            RemoteUser.objects.filter(id=userid).update(**data)
            event_log(user, 17, '主机用户 [{}] 更新成功'.format(RemoteUser.objects.get(id=userid).name), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '主机用户不存在!'
            return JsonResponse({"code": 401, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 402, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def user_add(request):
    adduser_form = AddUserForm(request.POST)
    if adduser_form.is_valid():
        log_user = request.session.get('username')
        name = adduser_form.cleaned_data.get('name')
        username = adduser_form.cleaned_data.get('username')
        password = adduser_form.cleaned_data.get('password')
        domain = adduser_form.cleaned_data.get('domain', None)
        memo = adduser_form.cleaned_data.get('memo')
        enabled = adduser_form.cleaned_data.get('enabled')
        superusername = adduser_form.cleaned_data.get('superusername', None)
        superpassword = adduser_form.cleaned_data.get('superpassword', None)
        if enabled:
            if not superusername or not superpassword:
                error_message = '超级用户或者超级密码不能为空!'
                return JsonResponse({"code": 400, "err": error_message})
            
        data = {
            'name': name,
            'username': username,
            'password': encrypt(password),
            'domain': domain,
            'memo': memo,
            'enabled': enabled,
            'superusername': superusername,
            'superpassword': encrypt(superpassword) if superpassword else superpassword,
        }
        try:
            if RemoteUser.objects.filter(name=name).count() > 0:
                error_message = '主机用户已存在'
                return JsonResponse({"code": 401, "err": error_message})
            user = User.objects.get(username=log_user)
            update_user = RemoteUser.objects.create(**data)
            event_log(user, 15, '主机用户 [{}] 添加成功'.format(update_user.name), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '未知错误!'
            return JsonResponse({"code": 402, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 403, "err": error_message})
        

@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def user_delete(request):
    pk = request.POST.get('id', None)
    try:
        ids = [ int(x) for x in pk.split(',')]
    except Exception:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 401, "err": error_message})
    if not ids:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 402, "err": error_message})
    remoteusers = RemoteUser.objects.filter(pk__in=ids)
    if not remoteusers:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 403, "err": error_message})
    remoteusernames = list()
    for remoteuser in remoteusers:
        if remoteuser.remoteuserbindhost_set.all().count() != 0:
            continue
        remoteuser.delete()
        remoteusernames.append(remoteuser.name)
    loguser = User.objects.get(username=request.session.get('username'))
    event_log(
        loguser, 16, '主机用户 [{}] 删除成功'.format(','.join(remoteusernames)),
        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None)
    )
    return JsonResponse({"code": 200, "err": ""})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def host_delete(request):
    pk = request.POST.get('id', None)
    try:
        ids = [ int(x) for x in pk.split(',')]
    except Exception:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 401, "err": error_message})
    if not ids:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 402, "err": error_message})
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        hosts = RemoteUserBindHost.objects.filter(pk__in=ids)
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            pk__in=ids
        )
    if not hosts:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 403, "err": error_message})
    hostnames = list()
    for host in hosts:
        host.delete()
        hostnames.append(host.hostname)
    loguser = User.objects.get(username=request.session.get('username'))
    event_log(
        loguser, 13, '主机 [{}] 删除成功'.format(','.join(hostnames)),
        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None)
    )
    return JsonResponse({"code": 200, "err": ""})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def host_update(request):
    changehost_form = ChangeHostForm(request.POST)
    if changehost_form.is_valid():
        log_user = request.session.get('username')
        hostid = changehost_form.cleaned_data.get('hostid')
        type = changehost_form.cleaned_data.get('type')
        ip = changehost_form.cleaned_data.get('ip')
        wip = changehost_form.cleaned_data.get('wip')
        protocol = changehost_form.cleaned_data.get('protocol')
        security = changehost_form.cleaned_data.get('security', None)
        env = changehost_form.cleaned_data.get('env')
        platform = changehost_form.cleaned_data.get('platform')
        port = changehost_form.cleaned_data.get('port')
        release = changehost_form.cleaned_data.get('release')
        memo = changehost_form.cleaned_data.get('memo')
        enabled = changehost_form.cleaned_data.get('enabled')
        binduserid = changehost_form.cleaned_data.get('binduserid')
        data = {
            'type': type,
            'ip': ip,
            'wip': wip,
            'protocol': protocol,
            'security': security,
            'env': env,
            'platform': platform,
            'port': port,
            'release': release,
            'memo': memo,
            'enabled': enabled,
        }
        try:
            user = User.objects.get(username=log_user)
            remoteuser = RemoteUser.objects.get(id=binduserid)
            data['remote_user'] = remoteuser
            if request.session['issuperuser'] and request.session['username'] == 'admin':
                RemoteUserBindHost.objects.filter(id=hostid).update(**data)
            else:
                RemoteUserBindHost.objects.filter(
                    Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
                    id=hostid
                ).update(**data)
            event_log(user, 14, '主机 [{}] 更新成功'.format(RemoteUserBindHost.objects.get(id=hostid).hostname),
                            request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '未知错误!'
            return JsonResponse({"code": 400, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def host_add(request):
    addhost_form = AddHostForm(request.POST)
    if addhost_form.is_valid():
        log_user = request.session.get('username')
        hostname = addhost_form.cleaned_data.get('hostname')
        type = addhost_form.cleaned_data.get('type')
        ip = addhost_form.cleaned_data.get('ip')
        wip = addhost_form.cleaned_data.get('wip')
        protocol = addhost_form.cleaned_data.get('protocol')
        security = addhost_form.cleaned_data.get('security', None)
        env = addhost_form.cleaned_data.get('env')
        platform = addhost_form.cleaned_data.get('platform')
        port = addhost_form.cleaned_data.get('port')
        release = addhost_form.cleaned_data.get('release')
        memo = addhost_form.cleaned_data.get('memo')
        enabled = addhost_form.cleaned_data.get('enabled')
        binduserid = addhost_form.cleaned_data.get('binduserid')
        data = {
            'hostname': hostname,
            'type': type,
            'ip': ip,
            'wip': wip,
            'protocol': protocol,
            'security': security,
            'env': env,
            'platform': platform,
            'port': port,
            'release': release,
            'memo': memo,
            'enabled': enabled,
        }
        try:
            user = User.objects.get(username=log_user)
            remoteuser = RemoteUser.objects.get(id=binduserid)
            data['remote_user'] = remoteuser
            remoteuserbindhost = RemoteUserBindHost.objects.create(**data)
            if not request.session['issuperuser'] or request.session['username'] != 'admin':
                user.remote_user_bind_hosts.add(remoteuserbindhost)     # 非 admin 添加的主机分配给自己
            event_log(user, 12, '主机 [{}] 添加成功'.format(remoteuserbindhost.hostname),
                            request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            hostinfo = dict()
            hostinfo['id'] = remoteuserbindhost.id
            hostinfo['hostname'] = remoteuserbindhost.hostname
            hostinfo['ip'] = remoteuserbindhost.ip
            hostinfo['port'] = remoteuserbindhost.port
            hostinfo['platform'] = remoteuserbindhost.get_platform_display()
            hostinfo['username'] = remoteuserbindhost.remote_user.username
            hostinfo['password'] = remoteuserbindhost.remote_user.password
            if remoteuserbindhost.remote_user.enabled:
                hostinfo['superusername'] = remoteuserbindhost.remote_user.superusername
                hostinfo['superpassword'] = remoteuserbindhost.remote_user.superpassword
            else:
                hostinfo['superusername'] = None
            task_host_update_info.delay(hostinfo=hostinfo)
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '未知错误!'
            return JsonResponse({"code": 400, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def host_update_info(request):
    hostid = request.POST.get('id', None)

    try:
        ids = [int(x) for x in hostid.split(',')]
    except Exception:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 401, "err": error_message})
    if not ids:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 402, "err": error_message})
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        hosts = RemoteUserBindHost.objects.filter(pk__in=ids, platform__in=[1, 3])
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            pk__in=ids,
            platform__in=[1, 3]
        )
    if not hosts:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 403, "err": error_message})
    for host in hosts:
        hostinfo = dict()
        hostinfo['id'] = host.id
        hostinfo['hostname'] = host.hostname
        hostinfo['ip'] = host.ip
        hostinfo['port'] = host.port
        hostinfo['platform'] = host.get_platform_display()
        hostinfo['username'] = host.remote_user.username
        hostinfo['password'] = host.remote_user.password
        if host.remote_user.enabled:
            hostinfo['superusername'] = host.remote_user.superusername
            hostinfo['superpassword'] = host.remote_user.superpassword
        else:
            hostinfo['superusername'] = None
        task_host_update_info.delay(hostinfo=hostinfo)
    return JsonResponse({"code": 200, "err": ""})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def group_delete(request):
    pk = request.POST.get('id', None)
    try:
        ids = [ int(x) for x in pk.split(',')]
    except Exception:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 401, "err": error_message})
    if not ids:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 402, "err": error_message})
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(pk__in=ids, user=user)
    if not groups:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 403, "err": error_message})
    groupnames = list()
    for group in groups:
        group.delete()
        groupnames.append(group.group_name)
    event_log(
        user, 22, '主机组 [{}] 删除成功'.format(','.join(groupnames)),
        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None)
    )
    return JsonResponse({"code": 200, "err": ""})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def group_update(request):
    changegroup_form = ChangeGroupForm(request.POST)
    if changegroup_form.is_valid():
        log_user = request.session.get('username')
        groupid = changegroup_form.cleaned_data.get('groupid')
        memo = changegroup_form.cleaned_data.get('memo')
        hosts = changegroup_form.cleaned_data.get('hosts')
        if hosts:
            try:
                hosts = [int(host) for host in hosts.split(',')]
            except Exception:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            hosts = None

        data = {
            'memo': memo,
        }

        try:
            user = User.objects.get(username=log_user)
            HostGroup.objects.filter(id=groupid, user=user).update(**data)
            update_group = HostGroup.objects.get(id=groupid, user=user)
            if hosts:  # 更新主机多对多字段
                if request.session['issuperuser']:
                    update_hosts = RemoteUserBindHost.objects.filter(id__in=hosts)
                else:
                    update_hosts = RemoteUserBindHost.objects.filter(
                        Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
                        Q(id__in=hosts),
                    )
                update_group.remoteuserbindhost_set.set(update_hosts)
            else:
                update_group.remoteuserbindhost_set.clear()

            update_group.save()
            event_log(user, 23, '主机组 [{}] 更新信息成功'.format(update_group.group_name), request.META.get('REMOTE_ADDR', None),
                      request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '主机组不存在!'
            return JsonResponse({"code": 402, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 403, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def group_add(request):
    addgroup_form = AddGroupForm(request.POST)
    if addgroup_form.is_valid():
        log_user = request.session.get('username')
        groupname = addgroup_form.cleaned_data.get('groupname')
        memo = addgroup_form.cleaned_data.get('memo')
        hosts = addgroup_form.cleaned_data.get('hosts')
        if hosts:
            try:
                hosts = [int(host) for host in hosts.split(',')]
            except Exception:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            hosts = None

        data = {
            'group_name': groupname,
            'memo': memo,
        }

        try:
            user = User.objects.get(username=log_user)
            if HostGroup.objects.filter(group_name=groupname,  user=user).count() > 0:
                error_message = '主机组已存在'
                return JsonResponse({"code": 402, "err": error_message})
            data['user'] = user
            update_group = HostGroup.objects.create(**data)

            if hosts:  # 更新主机多对多字段
                if request.session['issuperuser'] and request.session['username'] == 'admin':
                    update_hosts = RemoteUserBindHost.objects.filter(id__in=hosts, enabled=True)
                else:
                    update_hosts = RemoteUserBindHost.objects.filter(
                        Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
                        Q(id__in=hosts),
                        enabled=True
                    )
                update_group.remoteuserbindhost_set.set(update_hosts)
            else:
                update_group.remoteuserbindhost_set.clear()

            update_group.save()
            event_log(user, 21, '主机组 [{}] 添加成功'.format(update_group.group_name), request.META.get('REMOTE_ADDR', None),
                      request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '主机组添加错误!'
            return JsonResponse({"code": 403, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 404, "err": error_message})
