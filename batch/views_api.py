from util.tool import login_required, post_required, file_combine
from django.http import JsonResponse
from server.models import HostGroup, RemoteUserBindHost
from user.models import User
from django.db.models import Q
from django.conf import settings
import traceback
import os
import hashlib
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
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


@login_required
@post_required
def upload(request):
    try:
        upload_file = request.FILES.get('fileBlob')
        file_name = request.POST.get('fileName')
        # 使用md5后的文件名保存分段，防止合并时因为文件名的原因出错
        file_name_md5 = hashlib.md5(file_name.encode(encoding='UTF-8')).hexdigest()
        file_chunk_count = request.POST.get('chunkCount')
        file_chunk_index = request.POST.get('chunkIndex')
        file_size = request.POST.get('fileSize')
        if int(file_size) > 5 * 1024 * 1024 * 1024:
            error_message = '文件过大!'
            return JsonResponse({"code": 400, "error": error_message})
        local_file_path = settings.TMP_ROOT
        local_file = '{}/{}'.format(local_file_path, '{}_{}_{}'.format(
            file_name_md5, file_chunk_count, int(file_chunk_index) + 1)
        )
        with open(local_file, 'wb') as f:
            for chunk in upload_file.chunks():
                f.write(chunk)
        complete = file_combine(int(file_size), int(file_chunk_count), local_file_path, file_name, file_name_md5)
        mess = {
            "code": 200,
            "chunkIndex": file_chunk_index,
            "filename": '{}/{}'.format(local_file_path, file_name),
            "complete": complete,
        }
        return JsonResponse(mess)      # fileinput 分片上传
    except Exception:
        logger.error(traceback.format_exc())
        error_message = '上传文件错误!'
        return JsonResponse({"code": 401, "error": error_message})

