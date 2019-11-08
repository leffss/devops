from django.shortcuts import render, get_object_or_404
from server.models import RemoteUserBindHost
from webssh.models import TerminalLog
from util.tool import login_required, post_required
from django.http import JsonResponse
from .forms import HostForm
from django.db.models import Q
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def terminal(request):
    host_form = HostForm(request.POST)
    error_message = '请检查填写的内容!'
    if host_form.is_valid():
        host_id = host_form.cleaned_data.get('hostid')
        # host = RemoteUserBindHost.objects.get(id=host_id, enabled=True)
        # host = get_object_or_404(RemoteUserBindHost, id=host_id, enabled=True)
        username = request.session.get('username')
        if request.session['issuperuser'] and request.session['username'] == 'admin':
            hosts = RemoteUserBindHost.objects.filter(
                Q(pk=host_id),
                Q(enabled=True),
            )
        else:
            hosts = RemoteUserBindHost.objects.filter(
                Q(pk=host_id),
                Q(enabled=True),
                Q(user__username=username) | Q(group__user__username=username),
            ).distinct()
        if not hosts:
            error_message = '不存在的主机!'
            return JsonResponse({"code": 400, "error": error_message})
        else:
            host = hosts[0]
            return render(request, 'webtelnet/terminal.html', locals())

    return JsonResponse({"code": 406, "err": error_message})
