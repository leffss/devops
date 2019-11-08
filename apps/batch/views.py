from django.shortcuts import render
from util.tool import login_required
from .models import BatchCmdLog
from server.models import HostGroup
from user.models import User
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def cmd(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/cmd.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def script(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/script.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def file(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/file.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def playbook(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/playbook.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def module(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/module.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def logs(request):
    logs = BatchCmdLog.objects.all()
    return render(request, 'batch/logs.html', locals())
