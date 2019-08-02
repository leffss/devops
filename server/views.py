from django.shortcuts import render
from util.tool import login_required, admin_required
from .models import RemoteUserBindHost, RemoteUser
from user.models import User, Group
from django.db.models import Q
# Create your views here.


@login_required
def index(request):
    host_count = RemoteUserBindHost.objects.all().count()
    user_count = User.objects.all().count()
    group_count = Group.objects.all().count()
    return render(request, 'server/index.html', locals())


@login_required
def hosts(request):
    if request.session['issuperuser']:
        hosts = RemoteUserBindHost.objects.all()
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username = request.session['username']) | Q(group__user__username = request.session['username'])
        ).distinct()
    return render(request, 'server/hosts.html', locals())


@login_required
@admin_required
def users(request):
    users = RemoteUser.objects.all()
    return render(request, 'server/users.html', locals())

