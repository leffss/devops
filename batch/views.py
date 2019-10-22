from django.shortcuts import render
from util.tool import login_required, admin_required
from .models import BatchCmdLog
from server.models import HostGroup
from user.models import User
# Create your views here.


@login_required
def cmd(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/cmd.html', locals())


@login_required
def script(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/script.html', locals())


@login_required
def file(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/file.html', locals())


@login_required
@admin_required
def logs(request):
    logs = BatchCmdLog.objects.all()
    return render(request, 'batch/logs.html', locals())

