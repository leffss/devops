from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import User, LoginLog, Group, Permission
from server.models import RemoteUserBindHost
from .forms import LoginForm
from util.tool import login_required, hash_code, event_log
import django.utils.timezone as timezone
from django.db.models import Q
from django.conf import settings
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
from util.permission import init_permission
from django.http import Http404
from collections import OrderedDict
import time
import json
import traceback
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
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
                    event_log(user, 3, '用户 [{}] 已禁用'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                    return render(request, 'user/login.html', locals())
            except Exception:
                error_message = '用户不存在!'
                event_log(None, 3, '用户 [{}] 不存在'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
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
                request.session['locked'] = False   # 锁定屏幕
                now = int(time.time())
                request.session['logintime'] = now
                request.session['lasttime'] = now
                if user.username == 'admin' and user.role == 1:  # admin 为系统特殊超级管理员，拥有所有权限
                    permission_dict, menu_list = init_permission(user.username, is_super=True)
                else:
                    permission_dict, menu_list = init_permission(user.username)     # 初始化权限和菜单
                request.session[settings.INIT_PERMISSION] = permission_dict
                request.session[settings.INIT_MENU] = menu_list
                event_log(user, 1, '用户 [{}] 登陆成功'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return redirect(reverse('server:index'))
            else:
                error_message = '密码错误!'
                event_log(user, 3, '用户 [{}] 密码错误'.format(username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
                return render(request, 'user/login.html', locals())
        else:
            event_log(None, 3, '登陆表单验证错误', request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
            return render(request, 'user/login.html', locals())
    return render(request, 'user/login.html')


@ratelimit(key=key, rate=rate, method=ALL, block=True)
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
        del request.session['locked']
        del request.session['logintime']
        del request.session['lasttime']
        del request.session['referer_url']
        del request.session[settings.INIT_PERMISSION]
        del request.session[settings.INIT_MENU]
    except Exception:
        pass
    event_log(user, 2, '用户 [{}] 退出'.format(user.username), request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
    return redirect(reverse('user:login'))


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def lockscreen(request):
    if request.method == 'GET':
        try:
            request.session['locked'] = True  # 锁定屏幕
            if 'referer_url' not in request.session:
                referer_url = request.META.get('HTTP_REFERER', reverse('server:index'))
                request.session['referer_url'] = referer_url
        except Exception:
            pass
        return render(request, 'user/lockscreen.html')
    elif request.method == 'POST':
        try:
            password = request.POST.get('password', None)
            if password:
                user = User.objects.get(pk=request.session['userid'])
                if user.password == hash_code(password):
                    request.session['locked'] = False
                    return_url = request.session.get('referer_url', reverse('server:index'))
                    try:
                        del request.session['referer_url']
                    except Exception:
                        pass
                    return redirect(return_url)
                else:
                    return render(request, 'user/lockscreen.html', {'error_message': '请输入正确的密码'})
            else:
                return render(request, 'user/lockscreen.html', {'error_message': '请输入密码'})
        except Exception:
            pass
        return redirect(reverse('user:lockscreen'))


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def users(request):
    users = User.objects.exclude(pk=request.session['userid']).exclude(username='admin')  # exclude 排除当前登陆用户
    return render(request, 'user/users.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def groups(request):
    groups = Group.objects.all()
    return render(request, 'user/groups.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def logs(request):
    logs = LoginLog.objects.all()
    return render(request, 'user/logs.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def profile(request):
    user = get_object_or_404(User, pk=request.session.get('userid'))
    clissh = json.loads(user.setting)['clissh']
    ssh_app = None
    for i in clissh:
        if i['enable']:
            ssh_app = i
            break
    clisftp = json.loads(user.setting)['clisftp']
    sftp_app = None
    for i in clisftp:
        if i['enable']:
            sftp_app = i
            break
    return render(request, 'user/profile.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def profile_edit(request):
    user = get_object_or_404(User, pk=request.session.get('userid'))
    clissh = json.loads(user.setting)['clissh']
    clisftp = json.loads(user.setting)['clisftp']
    sex_choices = (
        ('male', "男"),
        ('female', "女"),
    )
    return render(request, 'user/profile_edit.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.id == request.session['userid'] or (user.username == 'admin' and user.role == 1):
        raise Http404('Not found')
    return render(request, 'user/user.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if user.id == request.session['userid'] or (user.username == 'admin' and user.role == 1):
        raise Http404('Not found')
    other_groups = Group.objects.filter(    # 查询当前用户不属于的组
        ~Q(user__id=user_id),
    )
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        other_hosts = RemoteUserBindHost.objects.filter(
            ~Q(user__id=user_id),
        )
    else:
        other_hosts = RemoteUserBindHost.objects.filter(
            ~Q(user__id=user_id),
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
        ).distinct()

    sex_choices = (
        ('male', "男"),
        ('female', "女"),
    )
    role_choices = (
        (2, '普通用户'),
        (1, '超级管理员'),
    )

    include_permission_ids = [ x.id for x in user.permission.all() ]
    # 特殊管理员 admin 可以分配所有权限，其他用户只能分配自己的权限
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        all_permissions = Permission.objects.all()
    else:
        all_permissions = Permission.objects.filter(
                Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
        ).distinct()

    # 转换为前端 ztree 数据类型
    permissions = OrderedDict()
    for permission in all_permissions:
        if not permission.menu:
            permissions[permission.title] = {
                'name': permission.title,
                'value': permission.id,
                'checked': True if permission.id in include_permission_ids else False
            }
        else:
            if permission.menu in permissions:
                permissions[permission.menu]['children'].append({
                    'name': permission.title,
                    'value': permission.id,
                    'checked': True if permission.id in include_permission_ids else False
                })
            else:
                permissions[permission.menu] = {
                    'name': permission.menu,
                    'children': [
                        {
                            'name': permission.title,
                            'value': permission.id,
                            'checked': True if permission.id in include_permission_ids else False
                        }
                    ]
                }
            for x in permissions[permission.menu]['children']:
                if x['checked']:
                    permissions[permission.menu]['open'] = True
                    break
            else:
                permissions[permission.menu]['open'] = False
    ztree_permissions = [ permissions[x] for x in permissions ]
    ztree_permissions = json.dumps(ztree_permissions, ensure_ascii=True)

    return render(request, 'user/user_edit.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def user_add(request):
    all_groups = Group.objects.all()
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        all_hosts = RemoteUserBindHost.objects.all()
    else:
        all_hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
        ).distinct()
    sex_choices = (
        ('male', "男"),
        ('female', "女"),
    )
    role_choices = (
        (2, '普通用户'),
        (1, '超级管理员'),
    )

    # 特殊管理员 admin 可以分配所有权限，其他用户只能分配自己的权限
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        all_permissions = Permission.objects.all()
    else:
        all_permissions = Permission.objects.filter(
                Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
        ).distinct()

    # 转换为前端 ztree 数据类型
    permissions = OrderedDict()
    for permission in all_permissions:
        if not permission.menu:
            permissions[permission.title] = {
                'name': permission.title,
                'value': permission.id
            }
        else:
            if permission.menu in permissions:
                permissions[permission.menu]['children'].append({
                    'name': permission.title,
                    'value': permission.id
                })
            else:
                permissions[permission.menu] = {
                    'name': permission.menu,
                    'open': False,
                    'children': [
                        {'name': permission.title, 'value': permission.id}
                    ]
                }
    ztree_permissions = [ permissions[x] for x in permissions ]
    ztree_permissions = json.dumps(ztree_permissions, ensure_ascii=True)

    return render(request, 'user/user_add.html', locals())
    

@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    return render(request, 'user/group.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def group_edit(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    other_users = User.objects.filter(    # 查询当前组不包含的用户
        ~Q(groups__id=group_id),
        ~Q(id=request.session['userid']),
        ~Q(username='admin'),
    )
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        other_hosts = RemoteUserBindHost.objects.filter(
            ~Q(group__id=group_id)
        )
    else:
        other_hosts = RemoteUserBindHost.objects.filter(
            ~Q(group__id=group_id),
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username'])
        ).distinct()

    # 特殊管理员 admin 可以分配所有权限，其他用户只能分配自己的权限
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        all_permissions = Permission.objects.all()
    else:
        all_permissions = Permission.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
        ).distinct()

    include_permission_ids = [x.id for x in group.permission.all()]
    # 转换为前端 ztree 数据类型
    permissions = OrderedDict()
    for permission in all_permissions:
        if not permission.menu:
            permissions[permission.title] = {
                'name': permission.title,
                'value': permission.id,
                'checked': True if permission.id in include_permission_ids else False
            }
        else:
            if permission.menu in permissions:
                permissions[permission.menu]['children'].append({
                    'name': permission.title,
                    'value': permission.id,
                    'checked': True if permission.id in include_permission_ids else False
                })
            else:
                permissions[permission.menu] = {
                    'name': permission.menu,
                    'children': [
                        {
                            'name': permission.title,
                            'value': permission.id,
                            'checked': True if permission.id in include_permission_ids else False
                        }
                    ]
                }
            for x in permissions[permission.menu]['children']:
                if x['checked']:
                    permissions[permission.menu]['open'] = True
                    break
            else:
                permissions[permission.menu]['open'] = False
    ztree_permissions = [ permissions[x] for x in permissions ]
    ztree_permissions = json.dumps(ztree_permissions, ensure_ascii=True)
    return render(request, 'user/group_edit.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def group_add(request):
    all_users = User.objects.exclude(pk=request.session['userid']).exclude(username='admin')
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        all_hosts = RemoteUserBindHost.objects.all()
    else:
        all_hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username'])
        ).distinct()

    # 特殊管理员 admin 可以分配所有权限，其他用户只能分配自己的权限
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        all_permissions = Permission.objects.all()
    else:
        all_permissions = Permission.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
        ).distinct()

    # 转换为前端 ztree 数据类型
    permissions = OrderedDict()
    for permission in all_permissions:
        if not permission.menu:
            permissions[permission.title] = {
                'name': permission.title,
                'value': permission.id
            }
        else:
            if permission.menu in permissions:
                permissions[permission.menu]['children'].append({
                    'name': permission.title,
                    'value': permission.id
                })
            else:
                permissions[permission.menu] = {
                    'name': permission.menu,
                    'open': False,
                    'children': [
                        {'name': permission.title, 'value': permission.id}
                    ]
                }
    ztree_permissions = [ permissions[x] for x in permissions ]
    ztree_permissions = json.dumps(ztree_permissions, ensure_ascii=True)

    return render(request, 'user/group_add.html', locals())
