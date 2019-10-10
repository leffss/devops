from django.shortcuts import render
from server.models import RemoteUserBindHost
from util.tool import login_required, post_required
from django.http import JsonResponse
from .forms import HostForm
# Create your views here.
# Create your views here.


@login_required
@post_required
# @post_required
def terminal(request):
    host_form = HostForm(request.POST)
    error_message = '请检查填写的内容!'
    if host_form.is_valid():
        host_id = host_form.cleaned_data.get('hostid')
        host = RemoteUserBindHost.objects.get(id=host_id)
        return render(request, 'webguacamole/guacamole.html', locals())
    return JsonResponse({"code": 406, "err": error_message})

