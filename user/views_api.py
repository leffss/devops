from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import User, LoginLog, Group
from .forms import LoginForm, ChangePasswdForm, ChangeUserProfileForm, ChangeUserForm
from util.tool import login_required, hash_code, post_required, admin_required
import django.utils.timezone as timezone
import time
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
                login_event_log(user, 4, '用户 {} 已禁用'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return JsonResponse({"code": 401, "err": error_message})
            if newpasswd != newpasswdagain:
                error_message = '两次输入的新密码不一致'
                login_event_log(user, 4, '两次输入的新密码不一致', request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return JsonResponse({"code": 400, "err": error_message})
        except:
            error_message = '用户不存在!'
            login_event_log(None, 4, '用户 {} 不存在'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 403, "err": error_message})
        if user.password == hash_code(oldpassword):
            data = {'password': hash_code(newpasswd)}
            User.objects.filter(username=username).update(**data)
            login_event_log(user, 5, '用户 {} 修改密码成功'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        else:
            error_message = '当前密码错误!'
            login_event_log(user, 4, '用户 {} 当前密码错误'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 404, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        user = User.objects.get(username=request.session.get('username'))
        login_event_log(user, 4, '修改密码表单验证错误', request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 406, "err": error_message})


@login_required
@post_required
def profile_update(request):
    changeuserprofile_form = ChangeUserProfileForm(request.POST)
    if changeuserprofile_form.is_valid():
        username = request.session.get('username')
        nickname = changeuserprofile_form.cleaned_data.get('nickname')
        email = changeuserprofile_form.cleaned_data.get('email')
        phone = changeuserprofile_form.cleaned_data.get('phone')
        weixin = changeuserprofile_form.cleaned_data.get('weixin')
        qq = changeuserprofile_form.cleaned_data.get('qq')
        sex = changeuserprofile_form.cleaned_data.get('sex')
        memo = changeuserprofile_form.cleaned_data.get('memo')
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
            User.objects.filter(username=username).update(**data)
            request.session['nickname'] = nickname
            login_event_log(user, 10, '用户 {} 更新个人信息成功'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except:
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
        username = changeuser_form.cleaned_data.get('username')
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
            except:
                error_message = '请检查填写的内容!'
                return JsonResponse({"code": 401, "err": error_message})
        else:
            groups = None
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
            User.objects.filter(username=username).update(**data)
            update_user = User.objects.get(username=username)
            if groups:  # 更新多对多字段
                update_groups = Group.objects.filter(id__in=groups)
                update_user.groups.set(update_groups)
            else:
                update_user.groups.set(None)
            update_user.save()
            login_event_log(user, 10, '用户 {} 更新信息成功'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return JsonResponse({"code": 200, "err": ""})
        except:
            # print(traceback.format_exc())
            error_message = '用户不存在!'
            return JsonResponse({"code": 402, "err": error_message})
    else:
        error_message = '请检查填写的内容!'
        return JsonResponse({"code": 403, "err": error_message})

