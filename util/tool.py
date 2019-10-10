from django.shortcuts import redirect
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from functools import wraps
import hashlib
import time
import random
from webssh.models import TerminalLog
from user.models import LoginLog
from tasks.tasks import task_save_event_log, task_save_terminal_log, task_save_res
import platform
import glob
import os
import traceback


try:
    session_exipry_time = settings.CUSTOM_SESSION_EXIPRY_TIME
except Exception:
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
            return redirect(reverse('server:hosts'))
            # return JsonResponse({"code": 403, "err": "无权限"})
        return func(request, *args, **kwargs)
    return wrapper


# 生成随机字符串
def gen_rand_char(length=10, chars='0123456789zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA'):
    return ''.join(random.sample(chars, length))


def terminal_log(user, hostname, ip, protocol, port, username, cmd, detail, address, useragent, start_time):
    username = ''
    try:
        username = user.username
    except Exception:
        username = user
    if platform.system().lower() in ['linux', 'unix']:
        task_save_terminal_log.delay(username, hostname, ip, protocol, port, username, cmd, detail, address, useragent, start_time)
    else:
        event = TerminalLog()
        event.user = username
        event.hostname = hostname
        event.ip = ip
        event.protocol = protocol
        event.port = port
        event.username = username
        event.cmd = cmd
        event.detail = detail
        event.address = address
        event.useragent = useragent
        event.start_time = start_time
        event.save()


def res(res_file, res, enter=True):
    if platform.system().lower() in ['linux', 'unix']:
        task_save_res.delay(res_file, res, enter)
    else:
        if enter:
            with open(res_file, 'a+') as f:
                for line in res:
                    f.write('{}\n'.format(line))
        else:
            with open(res_file, 'a+') as f:
                for line in res:
                    f.write('{}'.format(line))


def event_log(user, event_type, detail, address, useragent):
    username = ''
    try:
        username = user.username
    except Exception:
        username = user
    if platform.system().lower() in ['linux', 'unix']:
        task_save_event_log.delay(username, event_type, detail, address, useragent)
    else:
        event = LoginLog()
        event.user = username
        event.event_type = event_type
        event.detail = detail
        event.address = address
        event.useragent = useragent
        event.save()


def file_combine(file_size, file_count, file_path, file_name, file_name_md5):
    """
    使用fileinput分段上传过来的数据
    验证分段数量和分段总大小正确后才合并
    """
    try:
        file_lists = glob.glob(r'{}/{}_{}_*'.format(file_path, file_name_md5, file_count))
        if len(file_lists) != file_count:
            return False
        else:
            total_size = 0
            for file in file_lists:
                total_size += os.path.getsize(file)
            if total_size == file_size:
                with open('{}/{}'.format(file_path, file_name), 'wb') as f:
                    for i in range(1, file_count + 1):
                        with open('{}/{}_{}_{}'.format(file_path, file_name_md5, file_count, i), 'rb') as chunk:
                            f.write(chunk.read())
                        os.remove('{}/{}_{}_{}'.format(file_path, file_name_md5, file_count, i))
                return True
            else:
                return False
    except Exception:
        return False

