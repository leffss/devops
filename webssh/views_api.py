from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import TerminalSession
from user.models import LoginLog
from util.tool import login_required, post_required, admin_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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
            "text": '{"status":2, "message":"\\n\\rAdministrator forcibly interrupts your connection"}',
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

