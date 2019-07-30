from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from functools import wraps
import hashlib
import time


try:
    session_exipry_time = settings.CUSTOM_SESSION_EXIPRY_TIME
except BaseException:
    session_exipry_time = 60 * 30


# 登陆装饰器
def login_required(func):
    @wraps(func)    # 保留原函数信息，重要
    def wrapper(request, *args, **kwargs):
        if not request.session.get('islogin', None):
            return redirect(reverse('user:login'))
        lasttime = int(request.session.get('lasttime'))
        now = int(time.time())
        if now - lasttime > session_exipry_time:
            return redirect(reverse('user:logout'))
        else:
            request.session['lasttime'] = now
        return func(request, *args, **kwargs)
    return wrapper


# 必须 POST 方式装饰器
def post_required(func):
    @wraps(func)    # 保留原函数信息，重要
    def wrapper(request, *args, **kwargs):
        if request.method != 'POST':
            return JsonResponse({"code": 405, "err": "方法不允许"})
        return func(request, *args, **kwargs)
    return wrapper


# 用户密码加密
def hash_code(s, token='__leffss__qaz__devops'):
    h = hashlib.sha256()
    s += token
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


# 超级管理员才能访问的视图装饰器
def admin_required(func):
    @wraps(func)    # 保留原函数信息，重要
    def wrapper(request, *args, **kwargs):
        if not request.session['issuperuser']:
            return JsonResponse({"code": 403, "err": "无权限"})
        return func(request, *args, **kwargs)
    return wrapper

