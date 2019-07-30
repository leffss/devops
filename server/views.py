from django.shortcuts import render
from util.tool import login_required, admin_required
from .models import RemoteUserBindHost, RemoteUser
# Create your views here.


@login_required
def index(request):
    return render(request, 'server/index.html', locals())


@login_required
def lists(request):
    hosts = RemoteUserBindHost.objects.all()
    return render(request, 'server/host_lists.html', locals())

    
@login_required
@admin_required
def users(request):
    users = RemoteUser.objects.all()
    return render(request, 'server/user_lists.html', locals())
