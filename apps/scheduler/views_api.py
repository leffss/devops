from util.tool import post_required, event_log
from django.http import JsonResponse
from django.conf import settings
from .models import SchedulerHost
from util.rate import key
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from django.views.decorators.csrf import csrf_exempt
import traceback
import json
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Create your views here.


@ratelimit(key=key, rate=settings.RATELIMIT_LOGIN, method=ALL, block=True)
@post_required
@csrf_exempt
def client_upload(request):
    response = {'status': '-1'}
    try:
        data = json.loads(json.loads(request.body.decode()))
        protocol_choice = {
            'http': 1,
            'https': 2
        }
        scheduler_host = SchedulerHost.objects.filter(ip=request.META['REMOTE_ADDR'], port=data['port'], token=data['token'])
        if not scheduler_host:
            SchedulerHost.objects.create(
                hostname=data['hostname'],
                ip=request.META['REMOTE_ADDR'],
                protocol=protocol_choice[data['protocol']],
                port=data['port'],
                token=data['token'],
                status=True,
                cron=data['cron'],
                interval=data['interval'],
                date=data['date'],
                executed=data['executed'],
                failed=data['failed']
            )
            event_log(None, 24, '自动添加调度主机 [{}_{}_{}_{}] 成功'.format(data['hostname'],
                      request.META['REMOTE_ADDR'], data['protocol'], data['port']),
                      request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        else:
            scheduler_host[0].status = True
            scheduler_host[0].cron = data['cron']
            scheduler_host[0].interval = data['interval']
            scheduler_host[0].date = data['date']
            scheduler_host[0].executed = data['executed']
            scheduler_host[0].failed = data['failed']
            scheduler_host[0].save()
    except Exception as e:
        print(traceback.format_exc())
        response['msg'] = str(e)
    else:
        response['status'] = 0
        response['msg'] = ''
    return JsonResponse(response)
