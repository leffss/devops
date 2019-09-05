from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import TerminalSession
from user.models import LoginLog
from util.tool import login_required, post_required, admin_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache
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
@admin_required
@post_required
def session_close(request):
    pk = request.POST.get('id', None)
    group = request.POST.get('group', None)
    if not pk or not group:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.send)(terminalsession.name, {
        #     "type": "chat.message",
        #     "text": '{"status":2, "message":"\\n\\rAdministrator forcibly interrupts your connection"}',
        # })
        async_to_sync(channel_layer.group_send)(group, {
            "type": "chat.message",
            "text": '{"status":2, "message":"\\n\\r当前会话已被管理员关闭"}',
        })
        try:
            terminalsession.delete()
        except BaseException:
            pass
        login_event_log(request.session.get('username'), 18, '会话 [{}] 强制停止成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except BaseException:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@login_required
@admin_required
@post_required
def session_lock(request):
    pk = request.POST.get('id', None)
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(terminalsession.name, {
            "type": "lock.message",
            "text": request.session.get('username'),
        })
        try:
            TerminalSession.objects.filter(pk=pk).update(locked=True)
        except BaseException:
            pass
        login_event_log(request.session.get('username'), 19, '会话 [{}] 锁定成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except BaseException:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@login_required
@admin_required
@post_required
def session_unlock(request):
    pk = request.POST.get('id', None)
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(terminalsession.name, {
            "type": "unlock.message",
            "text": request.session.get('username'),
        })
        try:
            TerminalSession.objects.filter(pk=pk).update(locked=False)
        except BaseException:
            pass
        login_event_log(request.session.get('username'), 20, '会话 [{}] 解锁成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except BaseException:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@login_required
@admin_required
@post_required
def session_rdp_close(request):
    pk = request.POST.get('id', None)
    group = request.POST.get('group', None)
    if not pk or not group:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group, {
            "type": "close.message",
            "text": request.session.get('username'),
        })
        try:
            terminalsession.delete()
        except BaseException:
            pass
        login_event_log(request.session.get('username'), 18, '会话 [{}] 强制停止成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except BaseException:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@login_required
@admin_required
@post_required
def session_clissh_close(request):
    pk = request.POST.get('id', None)
    name = request.POST.get('session', None)
    if not pk or not name:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    name = name.strip()
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    if terminalsession.name != name:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    try:
        cache.delete(name)
        try:
            terminalsession.delete()
        except BaseException:
            pass
        login_event_log(request.session.get('username'), 18, '会话 [{}] 强制停止成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except BaseException:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@login_required
@admin_required
@post_required
def session_clissh_lock(request):
    pk = request.POST.get('id', None)
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        # 锁定会话
        cache.set(terminalsession.name + '_lock', True, timeout=60 * 60 * 24 * 30)
        try:
            TerminalSession.objects.filter(pk=pk).update(locked=True)
        except BaseException:
            pass
        login_event_log(request.session.get('username'), 19, '会话 [{}] 锁定成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except BaseException:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@login_required
@admin_required
@post_required
def session_clissh_unlock(request):
    pk = request.POST.get('id', None)
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        # 解锁会话
        cache.delete(terminalsession.name + '_lock')
        try:
            TerminalSession.objects.filter(pk=pk).update(locked=False)
        except BaseException:
            pass
        login_event_log(request.session.get('username'), 20, '会话 [{}] 解锁成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except BaseException:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})

