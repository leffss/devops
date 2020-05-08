from webssh.models import TerminalSession
from django.http import JsonResponse
from django.conf import settings
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
from util.tool import login_required, post_required, file_combine
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os
import hashlib
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_upload(request):
    username = request.session.get('username')
    group = request.POST.get('group')
    if not group:
        error_message = '错误的请求参数!'
        return JsonResponse({"code": 400, "error": error_message})
    session = TerminalSession.objects.filter(
        user=username,
        group=group,
    )
    if not session:
        error_message = '不存在的会话!'
        return JsonResponse({"code": 400, "error": error_message})
    try:
        # upload_file = request.FILES.get('upload_file')
        upload_file = request.FILES.get('fileBlob')
        file_name = request.POST.get('fileName')
        # 使用md5后的文件名保存分段，防止合并时因为文件名的原因出错
        file_name_md5 = hashlib.md5(file_name.encode(encoding='UTF-8')).hexdigest()
        file_chunk_count = request.POST.get('chunkCount')
        file_chunk_index = request.POST.get('chunkIndex')
        file_size = request.POST.get('fileSize')
        upload_file_path = os.path.join(settings.GUACD_ROOT, group)
        if not os.path.exists(upload_file_path):
            os.makedirs(upload_file_path, exist_ok=True)
        local_file = '{}/{}'.format(upload_file_path, '{}_{}_{}'.format(
            file_name_md5, file_chunk_count, int(file_chunk_index) + 1)
        )
        with open(local_file, 'wb') as f:
            for chunk in upload_file.chunks():
                f.write(chunk)
        complete = file_combine(int(file_size), int(file_chunk_count), upload_file_path, file_name, file_name_md5)
        mess = {
            "code": 200,
            "chunkIndex": file_chunk_index,
            "filename": file_name,
            "complete": complete,
        }
        if complete:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(group, {
                "type": "upload.message",
                "text": file_name,
            })

        return JsonResponse(mess)      # fileinput 分片上传
    except Exception:
        error_message = '上传文件错误!'
        return JsonResponse({"code": 401, "error": error_message})
