from util.tool import login_required, post_required
from django.http import JsonResponse
from server.models import HostGroup, RemoteUserBindHost
from user.models import User
from django.db.models import Q
# Create your views here.


@login_required
@post_required
def get_hosts(request):
    all = request.POST.get('all', False)
    if all:
        if request.session['issuperuser']:
            hosts = RemoteUserBindHost.objects.all()
        else:
            hosts = RemoteUserBindHost.objects.filter(
                Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
            ).distinct()
    else:
        groups = request.POST.get('groups', None)
        if not groups:
            error_message = '请检查填写的内容!'
            return JsonResponse({"code": 400, "err": error_message})
        try:
            groups = [int(group) for group in groups.split(',')]
        except Exception:
            error_message = '请检查填写的内容!'
            return JsonResponse({"code": 401, "err": error_message})

        user = User.objects.get(id=int(request.session.get('userid')))
        groups = HostGroup.objects.filter(id__in=groups, user=user)

        if request.session['issuperuser']:
            hosts = RemoteUserBindHost.objects.filter(
                Q(host_group__in=groups),
            ).distinct()
        else:
            hosts = RemoteUserBindHost.objects.filter(
                Q(user__username=request.session['username']) | Q(group__user__username=request.session['username']),
                Q(host_group__in=groups),
            ).distinct()
    hosts = [
        {
            'host_id': host.id,
            'host_hostname': host.hostname,
            'host_ip': host.ip,
            'host_username': host.remote_user.username
        } for host in hosts
    ]
    return JsonResponse({'code': 200, 'hosts': hosts})

