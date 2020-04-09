from django.shortcuts import render, get_object_or_404
from util.tool import login_required
from .models import SchedulerHost
from django.db.models import Q
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
import requests
import urllib3
import json
import traceback
urllib3.disable_warnings()
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def hosts(request):
    hosts = SchedulerHost.objects.all()
    return render(request, 'scheduler/hosts.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def host(request, host_id):
    host = get_object_or_404(
        SchedulerHost,
        pk=host_id,
    )
    return render(request, 'scheduler/host.html', locals())


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
def jobs(request, host_id):
    host = get_object_or_404(
        SchedulerHost,
        pk=host_id,
    )
    retry = 2
    timeout = 5
    attempts = 0
    success = False
    jobs = []
    while attempts <= retry and not success:
        try:
            headers = dict()
            headers['AUTHORIZATION'] = host.token
            headers['user-agent'] = 'requests/devops'
            url = '{protocol}://{ip}:{port}{url}'.format(
                protocol=host.get_protocol_display(), ip=host.ip, port=host.port, url='/api/job/lists'
            )
            res = requests.get(
                url=url,
                headers=headers,
                timeout=timeout,
                allow_redirects=True,
                verify=False,
            )
            if res.status_code == 200:
                r = json.loads(res.text)
                if r['status'] == 0:
                    jobs = r['data']
                    success = True
                else:
                    attempts += 1
            else:
                attempts += 1
        except Exception as e:
            print(traceback.format_exc())
            attempts += 1
    return render(request, 'scheduler/jobs.html', {'host': host, 'jobs': jobs})
