from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from .models import TerminalSession, TerminalLog
from server.models import RemoteUserBindHost
from util.tool import login_required, post_required, file_combine, terminal_log, event_log
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.cache import cache
from django.db.models import Q
from django.conf import settings
from .sftp import SFTP
from django.utils.http import urlquote
import os
import time
import hashlib
import django.utils.timezone as timezone
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
from util.rate import rate, key
from util.crypto import decrypt
import traceback
# Create your views here.
from django.contrib import auth


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_close(request):
    pk = request.POST.get('id', None)
    group = request.POST.get('group', None)
    if not pk or not group:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.send)(terminalsession.name, {
        #     "type": "chat.message",
        #     "text": '{"status":2, "message":"\\n\\rAdministrator forcibly interrupts your connection"}',
        # })
        async_to_sync(channel_layer.group_send)(group, {
            "type": "chat.message",
            "text": '{"status":2, "message":"\\n\\r当前会话已被管理员关闭"}',
        })
        try:
            terminalsession.delete()
        except Exception:
            pass
        event_log(request.session.get('username'), 18, '会话 [{}] 强制停止成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except Exception:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_lock(request):
    pk = request.POST.get('id', None)
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(terminalsession.name, {
            "type": "lock.message",
            "text": request.session.get('username'),
        })
        try:
            TerminalSession.objects.filter(pk=pk).update(locked=True)
        except Exception:
            pass
        event_log(request.session.get('username'), 19, '会话 [{}] 锁定成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except Exception:
        print(traceback.format_exc())
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_unlock(request):
    pk = request.POST.get('id', None)
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(terminalsession.name, {
            "type": "unlock.message",
            "text": request.session.get('username'),
        })
        try:
            TerminalSession.objects.filter(pk=pk).update(locked=False)
        except Exception:
            pass
        event_log(request.session.get('username'), 20, '会话 [{}] 解锁成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except Exception:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_rdp_close(request):
    pk = request.POST.get('id', None)
    group = request.POST.get('group', None)
    if not pk or not group:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group, {
            "type": "close.message",
            "text": request.session.get('username'),
        })
        try:
            terminalsession.delete()
        except Exception:
            pass
        event_log(request.session.get('username'), 18, '会话 [{}] 强制停止成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except Exception:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_clissh_close(request):
    pk = request.POST.get('id', None)
    name = request.POST.get('session', None)
    if not pk or not name:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    name = name.strip()
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    if terminalsession.name != name:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    try:
        cache.delete(name)
        try:
            terminalsession.delete()
        except Exception:
            pass
        event_log(request.session.get('username'), 18, '会话 [{}] 强制停止成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except Exception:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_clissh_lock(request):
    pk = request.POST.get('id', None)
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        # 锁定会话
        cache.set(terminalsession.name + '_lock', True, timeout=60 * 60 * 24 * 30)
        try:
            TerminalSession.objects.filter(pk=pk).update(locked=True)
        except Exception:
            pass
        event_log(request.session.get('username'), 19, '会话 [{}] 锁定成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except Exception:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_clissh_unlock(request):
    pk = request.POST.get('id', None)
    if not pk:
        error_message = '不合法的请求参数!'
        return JsonResponse({"code": 400, "err": error_message})
    terminalsession = get_object_or_404(TerminalSession, pk=pk)
    try:
        # 解锁会话
        cache.delete(terminalsession.name + '_lock')
        try:
            TerminalSession.objects.filter(pk=pk).update(locked=False)
        except Exception:
            pass
        event_log(request.session.get('username'), 20, '会话 [{}] 解锁成功'.format(terminalsession.name),
                        request.META.get('REMOTE_ADDR', None), request.META.get('HTTP_USER_AGENT', None))
        return JsonResponse({"code": 200, "err": ""})
    except Exception:
        error_message = '未知错误!'
        return JsonResponse({"code": 401, "err": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_upload(request, pk):
    username = request.session.get('username')
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        hosts = RemoteUserBindHost.objects.filter(pk=pk, enabled=True)
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=username) | Q(group__user__username=username),
            pk=pk,
            enabled=True
        ).distinct()
    if not hosts:
        error_message = '不存在的主机!'
        return JsonResponse({"code": 400, "error": error_message})
    try:
        remote_host = hosts[0]
        # upload_file = request.FILES.get('upload_file')
        upload_file = request.FILES.get('fileBlob')
        file_name = request.POST.get('fileName')
        # 使用md5后的文件名保存分段，防止合并时因为文件名的原因出错
        file_name_md5 = hashlib.md5(file_name.encode(encoding='UTF-8')).hexdigest()
        file_chunk_count = request.POST.get('chunkCount')
        file_chunk_index = request.POST.get('chunkIndex')
        file_size = request.POST.get('fileSize')
        upload_file_path = os.path.join(settings.MEDIA_ROOT, username, 'upload', remote_host.ip)
        if not os.path.exists(upload_file_path):
            os.makedirs(upload_file_path, exist_ok=True)
        local_file = '{}/{}'.format(upload_file_path, '{}_{}_{}'.format(
            file_name_md5, file_chunk_count, int(file_chunk_index) + 1)
        )
        with open(local_file, 'wb') as f:
            for chunk in upload_file.chunks():
                f.write(chunk)
        complete = file_combine(int(file_size), int(file_chunk_count), upload_file_path, file_name, file_name_md5)
        uploaded = False
        remote_path = None
        if complete:
            start_time = timezone.now()
            cmd_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
            sftp = SFTP(
                remote_host.ip, remote_host.port, remote_host.remote_user.username, decrypt(remote_host.remote_user.password)
            )
            uploaded, remote_path = sftp.upload_file(file_name, upload_file_path)
            os.remove('{}/{}'.format(upload_file_path, file_name))
            terminal_log(
                username,
                remote_host.hostname,
                remote_host.ip,
                'sftp',
                remote_host.port,
                remote_host.remote_user.username,
                cmd_time + '\t' + '上传文件 {}/{}'.format(remote_path, file_name),
                'nothing',
                request.META.get('REMOTE_ADDR', None),  # 客户端 ip
                request.META.get('HTTP_USER_AGENT', None),
                start_time,
            )
        mess = {
            "code": 200,
            "chunkIndex": file_chunk_index,
            "filename": file_name,
            "complete": complete,
            "uploaded": uploaded,
            "remote_path": remote_path
        }
        return JsonResponse(mess)      # fileinput 分片上传
    except Exception:
        error_message = '上传文件错误!'
        return JsonResponse({"code": 401, "error": error_message})


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def session_download(request, pk):
    def file_iterator(file_name, chunk_size=8192):
        with open(file_name, 'rb') as f:
            while 1:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
        os.remove(file_name)
        cmd_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
        terminal_log(
            username,
            remote_host.hostname,
            remote_host.ip,
            'sftp',
            remote_host.port,
            remote_host.remote_user.username,
            cmd_time + '\t' + '下载文件 {}'.format(download_file),
            'nothing',
            request.META.get('REMOTE_ADDR', None),  # 客户端 ip
            request.META.get('HTTP_USER_AGENT', None),
            start_time,
        )

    download_file = request.POST.get('real_download_file', None)
    if not download_file:
        error_message = '参数不正确!'
        return HttpResponse(error_message)
    username = request.session.get('username')
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        hosts = RemoteUserBindHost.objects.filter(pk=pk, enabled=True)
    else:
        hosts = RemoteUserBindHost.objects.filter(
            Q(user__username=username) | Q(group__user__username=username),
            pk=pk,
            enabled=True
        ).distinct()
    if not hosts:
        error_message = '不存在的主机!'
        return JsonResponse({"code": 400, "error": error_message})
    try:
        start_time = timezone.now()
        remote_host = hosts[0]
        download_file_path = os.path.join(settings.MEDIA_ROOT, username, 'download', remote_host.ip)
        if not os.path.exists(download_file_path):
            os.makedirs(download_file_path, exist_ok=True)
        file_path, file_name = os.path.split(download_file)
        local_file = '{}/{}'.format(download_file_path, file_name)
        sftp = SFTP(
            remote_host.ip, remote_host.port, remote_host.remote_user.username, decrypt(remote_host.remote_user.password)
        )
        downloaded = sftp.download_file(download_file, local_file)
        if not downloaded:
            error_message = '下载文件错误!'
            return HttpResponse(error_message)
        if os.path.getsize(local_file) == 0:
            os.remove(local_file)
            error_message = '下载文件错误!'
            return HttpResponse(error_message)
        # response = FileResponse(open(local_file, 'rb'))  # 使用FileResponse，会占用大内存
        response = FileResponse(file_iterator(local_file))  # 使用FileResponse, 并且使用迭代器，不占内存，还可以根据chunk_size控制带宽
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(urlquote(file_name))    # url 编码中文
        return response
    except Exception:
        error_message = '下载文件错误!'
        return HttpResponse(error_message)


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def logs(request):
    """
    配合前端 datatables
    """
    draw = int(request.POST.get('draw', 1))
    start = int(request.POST.get('start', 0))
    length = int(request.POST.get('length', 5))
    search_value = request.POST.get('search[value]', '')
    search_regex = request.POST.get('search[regex]', False)
    search_regex = True if search_regex == 'true' else False
    orders = [
        'user',
        'hostname',
        'username_ip_port',
        'protocol',
        'cmd',
        'address',
        'useragent',
        'start_time',
        'create_time',
    ]
    order_column = orders[int(request.POST.get('order[0][column]', 0))]
    order_dir = request.POST.get('order[0][dir]', '')
    records_total = TerminalLog.objects.all().count()
    if search_value:
        records_filtered = TerminalLog.objects.filter(
            Q(user__icontains=search_value) |
            Q(hostname__icontains=search_value) |
            Q(username__icontains=search_value) |
            Q(ip__icontains=search_value) |
            Q(port__icontains=search_value) |
            Q(cmd__icontains=search_value) |
            Q(address__icontains=search_value) |
            Q(useragent__icontains=search_value)
        ).count()
    else:
        records_filtered = records_total
    res = dict()
    res['draw'] = draw
    res['recordsTotal'] = records_total
    res['recordsFiltered'] = records_filtered
    if length <= 0:
        length = 5
    elif length > 100:
        length = 100
    if search_value:
        if order_dir and order_dir == 'desc':
            if order_column == 'username_ip_port':
                datas = TerminalLog.objects.filter(
                    Q(user__icontains=search_value) |
                    Q(hostname__icontains=search_value) |
                    Q(username__icontains=search_value) |
                    Q(ip__icontains=search_value) |
                    Q(port__icontains=search_value) |
                    Q(cmd__icontains=search_value) |
                    Q(address__icontains=search_value) |
                    Q(useragent__icontains=search_value)
                ).order_by('-username', '-ip', '-port')[start:start + length]
            else:
                datas = TerminalLog.objects.filter(
                    Q(user__icontains=search_value) |
                    Q(hostname__icontains=search_value) |
                    Q(username__icontains=search_value) |
                    Q(ip__icontains=search_value) |
                    Q(port__icontains=search_value) |
                    Q(cmd__icontains=search_value) |
                    Q(address__icontains=search_value) |
                    Q(useragent__icontains=search_value)
                ).order_by('-' + order_column)[start:start + length]
        elif order_dir and order_dir == 'asc':
            if order_column == 'username_ip_port':
                datas = TerminalLog.objects.filter(
                    Q(user__icontains=search_value) |
                    Q(hostname__icontains=search_value) |
                    Q(username__icontains=search_value) |
                    Q(ip__icontains=search_value) |
                    Q(port__icontains=search_value) |
                    Q(cmd__icontains=search_value) |
                    Q(address__icontains=search_value) |
                    Q(useragent__icontains=search_value)
                ).order_by('username', 'ip', 'port')[start:start + length]
            else:
                datas = TerminalLog.objects.filter(
                    Q(user__icontains=search_value) |
                    Q(hostname__icontains=search_value) |
                    Q(username__icontains=search_value) |
                    Q(ip__icontains=search_value) |
                    Q(port__icontains=search_value) |
                    Q(cmd__icontains=search_value) |
                    Q(address__icontains=search_value) |
                    Q(useragent__icontains=search_value)
                ).order_by(order_column)[start:start + length]
        else:
            datas = TerminalLog.objects.filter(
                Q(user__icontains=search_value) |
                Q(hostname__icontains=search_value) |
                Q(username__icontains=search_value) |
                Q(ip__icontains=search_value) |
                Q(port__icontains=search_value) |
                Q(cmd__icontains=search_value) |
                Q(address__icontains=search_value) |
                Q(useragent__icontains=search_value)
            )[start:start + length]
    else:
        if order_dir and order_dir == 'desc':
            if order_column == 'username_ip_port':
                datas = TerminalLog.objects.all().order_by('-username', '-ip', '-port')[start:start + length]
            else:
                datas = TerminalLog.objects.all().order_by('-' + order_column)[start:start + length]
        elif order_dir and order_dir == 'asc':
            if order_column == 'username_ip_port':
                datas = TerminalLog.objects.all().order_by('username', 'ip', 'port')[start:start + length]
            else:
                datas = TerminalLog.objects.all().order_by(order_column)[start:start + length]
        else:
            datas = TerminalLog.objects.all()[start:start + length]
    data = []
    for i in datas:
        tmp = list()
        tmp.append(i.user)
        tmp.append(i.hostname)
        tmp.append('{}@{}:{}'.format(i.username, i.ip, i.port))
        if i.protocol == 'ssh':
            protocol = '<span class="badge badge-success">ssh</span>'
        elif i.protocol == 'sftp':
            protocol = '<span class="badge badge-info">sftp</span>'
        elif i.protocol == 'telnet':
            protocol = '<span class="badge badge-primary">telnet</span>'
        else:
            protocol = '<span class="badge badge-secondary">{0}</span>'.format(i.protocol)
        tmp.append(protocol)
        cmd = i.cmd[0:30] + '...' if len(i.cmd) > 30 else i.cmd
        tmp.append(cmd.replace('\n\r', '<br>').replace('\r\n', '<br>').replace('\n', '<br>'))
        tmp.append(i.address if i.address else '')
        tmp.append(i.useragent[0:30] + '...' if len(i.useragent) > 30 else i.useragent)
        tmp.append(i.start_time.strftime('%Y/%m/%d %H:%M:%S'))
        tmp.append(i.create_time.strftime('%Y/%m/%d %H:%M:%S'))

        control_display = ''
        if i.protocol == 'ssh' or i.protocol == 'telnet':
            control_display = '<a href="javascript:void(0)" class="btn btn-primary btn-sm mb-1" ' \
                              'info="{user}-{hostname}-{username}@{ip}:{port}" ' \
                              'type="{protocol}" onclick="viewcmd(this);"><cmd hidden>{cmd}</cmd>' \
                              '<i class="fas fa-list"></i> 命令详情</a>&nbsp;&nbsp;<a href="javascript:void(0)" ' \
                              'class="btn btn-info btn-sm mb-1" id="{detail}" ' \
                              'info="{user}-{hostname}-{username}@{ip}:{port}" ' \
                              'onclick="viewsshvideo(this);">' \
                              '<i class="fas fa-video"></i> 回放</a>'.format(
                                                                            user=i.user,
                                                                            hostname=i.hostname,
                                                                            username=i.username,
                                                                            ip=i.ip,
                                                                            port=i.port,
                                                                            protocol=i.protocol,
                                                                            cmd=i.cmd,
                                                                            detail=i.detail,
                                                                            )
        elif i.protocol == 'sftp':
            control_display = '<a href="javascript:void(0)" class="btn btn-primary btn-sm mb-1" ' \
                              'info="{user}-{hostname}-{username}@{ip}:{port}" type="{protocol}" ' \
                              'onclick="viewcmd(this);"><cmd hidden>{cmd}</cmd><i class="fas fa-list">' \
                              '</i> 命令详情</a>&nbsp;&nbsp;'.format(
                                                                    user=i.user,
                                                                    hostname=i.hostname,
                                                                    username=i.username,
                                                                    ip=i.ip,
                                                                    port=i.port,
                                                                    protocol=i.protocol,
                                                                    cmd=i.cmd,
                                                                    )
        elif i.protocol == 'rdp' or i.protocol == 'vnc':
            control_display = '<a href="javascript:void(0)" class="btn btn-primary btn-sm mb-1" ' \
                              'info="{user}-{hostname}-{username}@{ip}:{port}" ' \
                              'type="{protocol}" onclick="viewcmd(this);"><cmd hidden>{cmd}</cmd>' \
                              '<i class="fas fa-list"></i> 命令详情</a>&nbsp;&nbsp;' \
                              '<a href="javascript:void(0)" class="btn btn-info btn-sm mb-1" ' \
                              'id="{detail}" info="{user}-{hostname}-{username}@{ip}:{port}" ' \
                              'onclick="viewrdpvideo(this);">' \
                              '<i class="fas fa-video"></i> 回放</a>'.format(
                                                                            user=i.user,
                                                                            hostname=i.hostname,
                                                                            username=i.username,
                                                                            ip=i.ip,
                                                                            port=i.port,
                                                                            protocol=i.protocol,
                                                                            cmd=i.cmd,
                                                                            detail=i.detail,
                                                                            )
        tmp.append(control_display)
        data.append(tmp)
    res['data'] = data
    return JsonResponse(res)

