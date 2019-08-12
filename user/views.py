from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from .models import User, LoginLog, Group
from server.models import RemoteUserBindHost
from .forms import LoginForm, ChangePasswdForm, ChangeUserProfileForm, ChangeUserForm
from util.tool import login_required, hash_code, post_required, admin_required
import django.utils.timezone as timezone
from django.db.models import Q
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


def login(request):
    if request.session.get('islogin', None):  # 不允许重复登录
        return redirect(reverse('server:index'))
    if request.method == "POST":        
        login_form = LoginForm(request.POST)
        error_message = '请检查填写的内容!'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = User.objects.get(username=username)
                if not user.enabled:
                    error_message = '用户已禁用!'                    
                    login_event_log(user, 3, '用户 [{}] 已禁用'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                    return render(request, 'user/login.html', locals())
            except BaseException:
                error_message = '用户不存在!'                
                login_event_log(None, 3, '用户 [{}] 不存在'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return render(request, 'user/login.html', locals())
            # if user.password == password:
            if user.password == hash_code(password):
                data = {'last_login_time': timezone.now()}
                User.objects.filter(username=username).update(**data)
                request.session.set_expiry(0)
                request.session['issuperuser'] = False
                if user.role == 1:      # 超级管理员
                    request.session['issuperuser'] = True
                request.session['islogin'] = True
                request.session['userid'] = user.id
                request.session['username'] = user.username
                request.session['nickname'] = user.nickname
                now = int(time.time())
                request.session['logintime'] = now
                request.session['lasttime'] = now                
                login_event_log(user, 1, '用户 [{}] 登陆成功'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return redirect(reverse('server:index'))
            else:
                error_message = '密码错误!'
                login_event_log(user, 3, '用户 [{}] 密码错误'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return render(request, 'user/login.html', locals())
        else:
            login_event_log(None, 3, '登陆表单验证错误', request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return render(request, 'user/login.html', locals())
    return render(request, 'user/login.html')


def logout(request):
    if not request.session.get('islogin', None):
        return redirect(reverse('user:login'))
    user = User.objects.get(id=int(request.session.get('userid')))
    # request.session.flush()     # 清除所有后包括django-admin登陆状态也会被清除
    # 或者使用下面的方法
    try:
        del request.session['issuperuser']
        del request.session['islogin']
        del request.session['userid']
        del request.session['username']
        del request.session['nickname']
        del request.session['logintime']
        del request.session['lasttime']
    except BaseException:
        pass
    login_event_log(user, 2, '用户 [{}] 退出'.format(user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
    return redirect(reverse('user:login'))


@login_required
@admin_required
def users(request):
    users = User.objects.exclude(pk=request.session['userid'])  # exclude 排除当前登陆用户
    return render(request, 'user/users.html', locals())

    
@login_required
@admin_required
def groups(request):
    groups = Group.objects.all()
    return render(request, 'user/groups.html', locals())


@login_required
@admin_required
def logs(request):
    logs = LoginLog.objects.all()
    return render(request, 'user/logs.html', locals())


@login_required
def profile(request):
    user = get_object_or_404(User, pk=request.session.get('userid'))
    return render(request, 'user/profile.html', locals())


@login_required
def profile_edit(request):
    user = get_object_or_404(User, pk=request.session.get('userid'))
    sex_choices = (
        ('male', "男"),
        ('female', "女"),
    )
    return render(request, 'user/profile_edit.html', locals())


@login_required
@admin_required
def user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'user/user.html', locals())


@login_required
@admin_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    other_groups = Group.objects.filter(    # 查询当前用户不属于的组
        ~Q(user__id=user_id),
    )
    other_hosts = RemoteUserBindHost.objects.filter(
        ~Q(user__id=user_id),
    )
    sex_choices = (
        ('male', "男"),
        ('female', "女"),
    )
    role_choices = (
        (2, '普通用户'),
        (1, '超级管理员'),
    )
    return render(request, 'user/user_edit.html', locals())

    
@login_required
@admin_required
def user_add(request):
    all_groups = Group.objects.all()
    all_hosts = RemoteUserBindHost.objects.all()
    sex_choices = (
        ('male', "男"),
        ('female', "女"),
    )
    role_choices = (
        (2, '普通用户'),
        (1, '超级管理员'),
    )
    return render(request, 'user/user_add.html', locals())
    

@login_required
@admin_required
def group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    return render(request, 'user/group.html', locals())


@login_required
@admin_required
def group_edit(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    other_users = User.objects.filter(    # 查询当前组不包含的用户
        ~Q(groups__id=group_id),
        ~Q(id=request.session['userid']),
    )
    other_hosts = RemoteUserBindHost.objects.filter(
        ~Q(group__id=group_id),
    )
    return render(request, 'user/group_edit.html', locals())


@login_required
@admin_required
def group_add(request):
    all_users = User.objects.exclude(pk=request.session['userid'])
    all_hosts = RemoteUserBindHost.objects.all()
    return render(request, 'user/group_add.html', locals())

