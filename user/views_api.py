from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import User, LoginLog, Group
from server.models import RemoteUserBindHost
from .forms import ChangePasswdForm, ChangeUserProfileForm, ChangeUserForm, ChangeGroupForm, AddGroupForm, AddUserForm
from util.tool import login_required, hash_code, post_required, admin_required, event_log
import traceback
import json
# Create your views here.


@login_required
@post_required
def password_update(request):
    changepasswd_form = ChangePasswdForm(request.POST)
    if changepasswd_form.is_valid():
        username = request.session.get('username')
        oldpassword = changepasswd_form.cleaned_data.get('oldpasswd')
        newpasswd = changepasswd_form.cleaned_data.get('newpasswd')
        newpasswdagain = changepasswd_form.cleaned_data.get('newpasswdagain')
        try:
            user = User.objects.get(username=username)
            if not user.enabled:
                error_message = '用户已禁用!'
                event_log(user, 4, '用户 [{}] 已禁用'.format(user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return JsonResponse({"code": 401, "err": error_message})
            if newpasswd != newpasswdagain:
                error_message = '两次输入的新密码不一致'
                event_log(user, 4, '两次输入的新密码不一致', request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return JsonResponse({"code": 400, "err": error_message})
        except Exception:
            error_message = '用户不存在!'
            event_log(None, 4, '用户 [{}] 不存在'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 403, "err": error_message})
        if user.password == hash_code(oldpassword):
            data = {'password': hash_code(newpasswd)}
            User.objects.filter(username=username).update(**data)
            event_log(user, 5, '用户 [{}] 修改密码成功'.format(user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        else:
            error_message = '当前密码错误!'
            event_log(user, 4, '用户 [{}] 当前密码错误'.format(user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 404, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        user = User.objects.get(username=request.session.get('username'))
        event_log(user, 4, '修改密码表单验证错误', request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 406, "err": error_message})


@login_required
@post_required
def profile_update(request):
    changeuserprofile_form = ChangeUserProfileForm(request.POST)
    if changeuserprofile_form.is_valid():
        userid = request.session.get('userid')
        username = request.session.get('username')
        nickname = changeuserprofile_form.cleaned_data.get('nickname')
        email = changeuserprofile_form.cleaned_data.get('email')
        phone = changeuserprofile_form.cleaned_data.get('phone')
        weixin = changeuserprofile_form.cleaned_data.get('weixin')
        qq = changeuserprofile_form.cleaned_data.get('qq')
        sex = changeuserprofile_form.cleaned_data.get('sex')
        memo = changeuserprofile_form.cleaned_data.get('memo')

        clissh_name = changeuserprofile_form.cleaned_data.get('clissh_name')
        clissh_path = changeuserprofile_form.cleaned_data.get('clissh_path')
        clissh_args = changeuserprofile_form.cleaned_data.get('clissh_args')
        clisftp_name = changeuserprofile_form.cleaned_data.get('clisftp_name')
        clisftp_path = changeuserprofile_form.cleaned_data.get('clisftp_path')
        clisftp_args = changeuserprofile_form.cleaned_data.get('clisftp_args')

        data = {
            'nickname': nickname,
            'email': email,
            'phone': phone,
            'weixin': weixin,
            'qq': qq,
            'sex': sex,
            'memo': memo,
        }
        try:
            user = User.objects.get(username=username)
            if not user.enabled:
                error_message = '用户已禁用!'
                return JsonResponse({"code": 401, "err": error_message})

            setting = json.loads(user.setting)
            k = 0
            for i in setting['clissh']:
                if i['name'] == clissh_name:
                    setting['clissh'][k]['path'] = clissh_path
                    setting['clissh'][k]['args'] = clissh_args
                    setting['clissh'][k]['enable'] = True
                else:
                    setting['clissh'][k]['enable'] = False
                k += 1

            k = 0
            for i in setting['clisftp']:
                if i['name'] == clisftp_name:
                    setting['clisftp'][k]['path'] = clisftp_path
                    setting['clisftp'][k]['args'] = clisftp_args
                    setting['clisftp'][k]['enable'] = True
                else:
                    setting['clisftp'][k]['enable'] = False
                k += 1

            data['setting'] = json.dumps(setting)

            User.objects.filter(pk=userid, username=username).update(**data)
            request.session['nickname'] = nickname
            event_log(user, 10, '用户 [{}] 更新个人信息成功'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            error_message = '用户不存在!'
            return JsonResponse({"code": 402, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 403, "err": error_message})


@login_required
@admin_required
@post_required
def user_update(request):
    changeuser_form = ChangeUserForm(request.POST)
    if changeuser_form.is_valid():
        log_user = request.session.get('username')
        userid = changeuser_form.cleaned_data.get('userid')
        nickname = changeuser_form.cleaned_data.get('nickname')
        email = changeuser_form.cleaned_data.get('email')
        phone = changeuser_form.cleaned_data.get('phone')
        weixin = changeuser_form.cleaned_data.get('weixin')
        qq = changeuser_form.cleaned_data.get('qq')
        sex = changeuser_form.cleaned_data.get('sex')
        memo = changeuser_form.cleaned_data.get('memo')
        enabled = changeuser_form.cleaned_data.get('enabled')
        role = changeuser_form.cleaned_data.get('role')
        groups = changeuser_form.cleaned_data.get('groups')
        if groups:
            try:
                groups = [int(group) for group in groups.split(',')]
            except Exception:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            groups = None

        hosts = changeuser_form.cleaned_data.get('hosts')
        if hosts:
            try:
                hosts = [int(host) for host in hosts.split(',')]
            except Exception:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            hosts = None
            
        data = {
            'nickname': nickname,
            'email': email,
            'phone': phone,
            'weixin': weixin,
            'qq': qq,
            'sex': sex,
            'memo': memo,
            'enabled': enabled,
            'role': role,
        }
        try:
            user = User.objects.get(username=log_user)
            User.objects.filter(id=userid).update(**data)
            update_user = User.objects.get(id=userid)
            if groups:  # 更新组多对多字段
                update_groups = Group.objects.filter(id__in=groups)
                update_user.groups.set(update_groups)
            else:
                update_user.groups.clear()
            
            if hosts:  # 更新主机多对多字段
                update_hosts = RemoteUserBindHost.objects.filter(id__in=hosts)
                update_user.remote_user_bind_hosts.set(update_hosts)
            else:
                update_user.remote_user_bind_hosts.clear()
            
            update_user.save()
            event_log(user, 10, '用户 [{}] 更新信息成功'.format(update_user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '用户不存在!'
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
    if pk == request.session.get('userid'):
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    user = get_object_or_404(User, pk=pk)
    if user.groups.all().count() != 0 or user.remote_user_bind_hosts.all().count() != 0:
        error_message = '用户下存在主机或者属于其他组!'
        return JsonResponse({"code": 401, "err": error_message})
    user.delete()
    event_log(loguser, 7, '用户 [{}] 删除成功'.format(user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
    return JsonResponse({"code": 200, "err": ""})


@login_required
@admin_required
@post_required
def user_add(request):
    adduser_form = AddUserForm(request.POST)
    if adduser_form.is_valid():
        log_user = request.session.get('username')
        username = adduser_form.cleaned_data.get('username')
        newpasswd = adduser_form.cleaned_data.get('newpasswd')
        newpasswdagain = adduser_form.cleaned_data.get('newpasswdagain')
        if newpasswd != newpasswdagain:
            error_message = '两次密码不一致!'
            return JsonResponse({"code": 400, "err": error_message})
        nickname = adduser_form.cleaned_data.get('nickname')
        email = adduser_form.cleaned_data.get('email')
        phone = adduser_form.cleaned_data.get('phone')
        weixin = adduser_form.cleaned_data.get('weixin')
        qq = adduser_form.cleaned_data.get('qq')
        sex = adduser_form.cleaned_data.get('sex')
        memo = adduser_form.cleaned_data.get('memo')
        enabled = adduser_form.cleaned_data.get('enabled')
        role = adduser_form.cleaned_data.get('role')
        groups = adduser_form.cleaned_data.get('groups')
        if groups:
            try:
                groups = [int(group) for group in groups.split(',')]
            except Exception:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            groups = None

        hosts = adduser_form.cleaned_data.get('hosts')
        if hosts:
            try:
                hosts = [int(host) for host in hosts.split(',')]
            except Exception:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            hosts = None
            
        data = {
            'username': username,
            'password': hash_code(newpasswd),
            'nickname': nickname,
            'email': email,
            'phone': phone,
            'weixin': weixin,
            'qq': qq,
            'sex': sex,
            'memo': memo,
            'enabled': enabled,
            'role': role,
        }
        try:
            if User.objects.filter(username=username).count() > 0:
                error_message = '用户名已存在'
                return JsonResponse({"code": 402, "err": error_message})
            user = User.objects.get(username=log_user)
            update_user = User.objects.create(**data)
            if groups:  # 更新组多对多字段
                update_groups = Group.objects.filter(id__in=groups)
                update_user.groups.set(update_groups)
            else:
                update_user.groups.clear()
            
            if hosts:  # 更新主机多对多字段
                update_hosts = RemoteUserBindHost.objects.filter(id__in=hosts)
                update_user.remote_user_bind_hosts.set(update_hosts)
            else:
                update_user.remote_user_bind_hosts.clear()
            
            update_user.save()
            event_log(user, 6, '用户 [{}] 添加成功'.format(update_user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '未知错误!'
            return JsonResponse({"code": 403, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 404, "err": error_message})
        
        
@login_required
@admin_required
@post_required
def group_update(request):
    changegroup_form = ChangeGroupForm(request.POST)
    if changegroup_form.is_valid():
        log_user = request.session.get('username')
        groupid = changegroup_form.cleaned_data.get('groupid')
        memo = changegroup_form.cleaned_data.get('memo')
        users = changegroup_form.cleaned_data.get('users')
        if users:
            try:
                users = [int(user) for user in users.split(',')]
            except Exception:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            users = None
        
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
            Group.objects.filter(id=groupid).update(**data)
            update_group = Group.objects.get(id=groupid)
            if users:  # 更新用户组
                update_users = User.objects.filter(id__in=users)
                update_group.user_set.set(update_users)
            else:
                update_group.user_set.clear()
                
            if hosts:  # 更新主机多对多字段
                update_hosts = RemoteUserBindHost.objects.filter(id__in=hosts)
                update_group.remote_user_bind_hosts.set(update_hosts)
            else:
                update_group.remote_user_bind_hosts.clear()
                
            update_group.save()
            event_log(user, 11, '组 [{}] 更新信息成功'.format(update_group.group_name), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '组不存在!'
            return JsonResponse({"code": 402, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 403, "err": error_message})


@login_required
@admin_required
@post_required
def group_delete(request):
    pk = request.POST.get('id', None)
    user = User.objects.get(username=request.session.get('username'))
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    group = get_object_or_404(Group, pk=pk)
    if group.user_set.all().count() != 0 or group.remote_user_bind_hosts.all().count() != 0:
        error_message = '组内存在用户或者主机!'
        return JsonResponse({"code": 401, "err": error_message})
    group.delete()
    event_log(user, 9, '组 [{}] 删除成功'.format(group.group_name), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
    return JsonResponse({"code": 200, "err": ""})

    
@login_required
@admin_required
@post_required
def group_add(request):
    addgroup_form = AddGroupForm(request.POST)
    if addgroup_form.is_valid():
        log_user = request.session.get('username')
        groupname = addgroup_form.cleaned_data.get('groupname')
        memo = addgroup_form.cleaned_data.get('memo')
        users = addgroup_form.cleaned_data.get('users')
        if users:
            try:
                users = [int(user) for user in users.split(',')]
            except Exception:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            users = None
        
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
            if Group.objects.filter(group_name=groupname).count() > 0:
                error_message = '组名已存在'
                return JsonResponse({"code": 402, "err": error_message})
            user = User.objects.get(username=log_user)
            update_group = Group.objects.create(**data)
            if users:  # 更新用户组
                update_users = User.objects.filter(id__in=users)
                update_group.user_set.set(update_users)
            else:
                update_group.user_set.clear()
                
            if hosts:  # 更新主机多对多字段
                update_hosts = RemoteUserBindHost.objects.filter(id__in=hosts)
                update_group.remote_user_bind_hosts.set(update_hosts)
            else:
                update_group.remote_user_bind_hosts.clear()
                
            update_group.save()
            event_log(user, 8, '组 [{}] 添加成功'.format(update_group.group_name), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except Exception:
            # print(traceback.format_exc())
            error_message = '未知错误!'
            return JsonResponse({"code": 403, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 404, "err": error_message})

