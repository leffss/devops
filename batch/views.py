from django.shortcuts import render
from util.tool import login_required
from server.models import HostGroup
from user.models import User
# Create your views here.


@login_required
def cmd(request):
    user = User.objects.get(id=int(request.session.get('userid')))
    groups = HostGroup.objects.filter(user=user)
    return render(request, 'batch/cmd.html', locals())

