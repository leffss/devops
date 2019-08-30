from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.http import JsonResponse
from util.tool import login_required, admin_required, post_required
from .models import RemoteUser, RemoteUserBindHost
from user.models import User, LoginLog
from .forms import ChangeUserForm, AddUserForm, ChangeHostForm, AddHostForm
import traceback
# Create your views here.


def login_event_log(user, event_type, detail, address, useragent):
    event = LoginLog()
    event.user = user
    event.event_type = event_type
    event.detail = detail
    event.address = address
    event.useragent = useragent
    event.save()


@login_required
@admin_required
@post_required
def user_update(request):
    changeuser_form = ChangeUserForm(request.POST)
    if changeuser_form.is_valid():
        log_user = request.session.get('username')
        userid = changeuser_form.cleaned_data.get('userid')
        username = changeuser_form.cleaned_data.get('username')
        password = changeuser_form.cleaned_data.get('password')
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
            'password': password,
            'memo': memo,
            'enabled': enabled,
            'superusername': superusername,
            'superpassword': superpassword,
        }
        try:
            user = User.objects.get(username=log_user)
            RemoteUser.objects.filter(id=userid).update(**data)
            login_event_log(user, 17, '主机用户 [{}] 更新成功'.format(RemoteUser.objects.get(id=userid).name), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except:
            # print(traceback.format_exc())
            error_message = '主机用户不存在!'
            return JsonResponse({"code": 401, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 402, "err": error_message})

        
@login_required
@admin_required
@post_required
def user_add(request):
    adduser_form = AddUserForm(request.POST)
    if adduser_form.is_valid():
        log_user = request.session.get('username')
        name = adduser_form.cleaned_data.get('name')
        username = adduser_form.cleaned_data.get('username')
        password = adduser_form.cleaned_data.get('password')
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
            'password': password,
            'memo': memo,
            'enabled': enabled,
            'superusername': superusername,
            'superpassword': superpassword,
        }
        try:
            if RemoteUser.objects.filter(name=name).count() > 0:
                error_message = '主机用户已存在'
                return JsonResponse({"code": 401, "err": error_message})
            user = User.objects.get(username=log_user)
            update_user = RemoteUser.objects.create(**data)
            login_event_log(user, 15, '主机用户 [{}] 添加成功'.format(update_user.name), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except:
            # print(traceback.format_exc())
            error_message = '未知错误!'
            return JsonResponse({"code": 402, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 403, "err": error_message})
        
        
@login_required
@admin_required
@post_required
def user_delete(request):
    pk = request.POST.get('id', None)
    loguser = User.objects.get(username=request.session.get('username'))
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    remoteuser = get_object_or_404(RemoteUser, pk=pk)
    if remoteuser.remoteuserbindhost_set.all().count() != 0:
        error_message = '用户已绑定主机!'
        return JsonResponse({"code": 401, "err": error_message})
    remoteuser.delete()
    login_event_log(loguser, 16, '主机用户 [{}] 删除成功'.format(remoteuser.name), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
    return JsonResponse({"code": 200, "err": ""})


@login_required
@admin_required
@post_required
def host_delete(request):
    pk = request.POST.get('id', None)
    loguser = User.objects.get(username=request.session.get('username'))
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    host = get_object_or_404(RemoteUserBindHost, pk=pk)
    host.delete()
    login_event_log(loguser, 13, '主机 [{}] 删除成功'.format(host.hostname), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
    return JsonResponse({"code": 200, "err": ""})


@login_required
@admin_required
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
        env = changehost_form.cleaned_data.get('env')
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
            'env': env,
            'port': port,
            'release': release,
            'memo': memo,
            'enabled': enabled,
        }
        try:
            user = User.objects.get(username=log_user)
            remoteuser = RemoteUser.objects.get(id=binduserid)
            data['remote_user'] = remoteuser
            RemoteUserBindHost.objects.filter(id=hostid).update(**data)
            login_event_log(user, 14, '主机 [{}] 更新成功'.format(RemoteUserBindHost.objects.get(id=hostid).hostname),
                            request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except:
            # print(traceback.format_exc())
            error_message = '未知错误!'
            return JsonResponse({"code": 400, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})


@login_required
@admin_required
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
        env = addhost_form.cleaned_data.get('env')
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
            'env': env,
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
            login_event_log(user, 12, '主机 [{}] 添加成功'.format(remoteuserbindhost.hostname),
                            request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except:
            # print(traceback.format_exc())
            error_message = '未知错误!'
            return JsonResponse({"code": 400, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 401, "err": error_message})

