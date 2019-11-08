from util.tool import login_required, post_required, file_combine
from django.http import JsonResponse
from .models import BatchCmdLog
from server.models import HostGroup, RemoteUserBindHost
from user.models import User
from django.db.models import Q
from django.conf import settings
import traceback
from util.rate import rate, key
from ratelimit.decorators import ratelimit      # 限速
from ratelimit import ALL
import hashlib
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Create your views here.


@ratelimit(key=key, rate=rate, method=ALL, block=True)
@login_required
@post_required
def get_hosts(request):
    all = request.POST.get('all', False)
    if all:
        if request.session['issuperuser'] and request.session['username'] == 'admin':
            hosts = RemoteUserBindHost.objects.filter(
                Q(enabled=True)
            )
        else:
            hosts = RemoteUserBindHost.objects.filter(
                Q(enabled=True),
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

        if request.session['issuperuser'] and request.session['username'] == 'admin':
            hosts = RemoteUserBindHost.objects.filter(
                Q(enabled=True),
                Q(host_group__in=groups),
            ).distinct()
        else:
            hosts = RemoteUserBindHost.objects.filter(
                Q(enabled=True),
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


@ratelimit(key=key, rate=rate, method=ALL, block=True)
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
        'hosts',
        'type',
        'cmd',
        'address',
        'useragent',
        'start_time',
        'create_time',
    ]
    order_column = orders[int(request.POST.get('order[0][column]', 0))]
    order_dir = request.POST.get('order[0][dir]', '')
    records_total = BatchCmdLog.objects.all().count()
    if search_value:
        records_filtered = BatchCmdLog.objects.filter(
            Q(user__icontains=search_value) |
            Q(hosts__icontains=search_value) |
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
            datas = BatchCmdLog.objects.filter(
                Q(user__icontains=search_value) |
                Q(hosts__icontains=search_value) |
                Q(cmd__icontains=search_value) |
                Q(address__icontains=search_value) |
                Q(useragent__icontains=search_value)
            ).order_by('-' + order_column)[start:start + length]
        elif order_dir and order_dir == 'asc':
            datas = BatchCmdLog.objects.filter(
                Q(user__icontains=search_value) |
                Q(hosts__icontains=search_value) |
                Q(cmd__icontains=search_value) |
                Q(address__icontains=search_value) |
                Q(useragent__icontains=search_value)
            ).order_by(order_column)[start:start + length]
        else:
            datas = BatchCmdLog.objects.filter(
                Q(user__icontains=search_value) |
                Q(hosts__icontains=search_value) |
                Q(cmd__icontains=search_value) |
                Q(address__icontains=search_value) |
                Q(useragent__icontains=search_value)
            )[start:start + length]
    else:
        if order_dir and order_dir == 'desc':
            datas = BatchCmdLog.objects.all().order_by('-' + order_column)[start:start + length]
        elif order_dir and order_dir == 'asc':
            datas = BatchCmdLog.objects.all().order_by(order_column)[start:start + length]
        else:
            datas = BatchCmdLog.objects.all()[start:start + length]

    data = []
    for i in datas:
        tmp = list()
        tmp.append(i.user)
        hosts = i.hosts[0:255] + '...' if len(i.hosts) > 255 else i.hosts
        tmp.append(hosts.replace('\n\r', '<br>').replace('\r\n', '<br>').replace('\n', '<br>'))
        if i.get_type_display() == '命令':
            type_display = '<span class="badge badge-success">命令</span>'
        elif i.get_type_display() == '脚本':
            type_display = '<span class="badge badge-info">脚本</span>'
        elif i.get_type_display() == '上传文件':
            type_display = '<span class="badge badge-primary">上传文件</span>'
        else:
            type_display = '<span class="badge badge-secondary">{0}</span>'.format(i.get_type_display())
        tmp.append(type_display)
        tmp.append(i.cmd[0:30] + '...' if len(i.cmd) > 30 else i.cmd)
        tmp.append(i.address if i.address else '')
        tmp.append(i.useragent[0:30] + '...' if len(i.useragent) > 30 else i.useragent)
        tmp.append(i.start_time.strftime('%Y/%m/%d %H:%M:%S'))
        tmp.append(i.create_time.strftime('%Y/%m/%d %H:%M:%S'))
        control_display = ''
        if i.get_type_display() == '命令':
            control_display = '<a href="javascript:void(0)" class="btn btn-success btn-sm mb-1" ' \
                              'info="{user}-{address}" type="{type_display}" onclick="viewcmd(this);">' \
                              '<cmd hidden>{cmd}</cmd><i class="fas fa-list"></i> 命令详情</a>' \
                              '&nbsp;&nbsp;'.format(
                                                    user=i.user,
                                                    address=i.address if i.address else '',
                                                    type_display=i.get_type_display(),
                                                    cmd=i.cmd,
                                                    )
        elif i.get_type_display() == '上传文件':
            control_display = '<a href="javascript:void(0)" class="btn btn-secondary btn-sm mb-1" ' \
                              'info="{user}-{address}" type="{type_display}" onclick="viewcmd(this);">' \
                              '<cmd hidden>{cmd}</cmd><i class="fas fa-list"></i> 上传详情</a>' \
                              '&nbsp;&nbsp;'.format(
                                                    user=i.user,
                                                    address=i.address if i.address else '',
                                                    type_display=i.get_type_display(),
                                                    cmd=i.cmd,
                                                    )
        elif i.get_type_display() == '脚本':
            control_display = '<a href="javascript:void(0)" class="btn btn-primary btn-sm mb-1" ' \
                              'info="{user}-{address}" type="{type_display}" onclick="viewcmd(this);">' \
                              '<cmd hidden>/media/{script}</cmd><i class="fas fa-list"></i> 脚本详情</a>' \
                              '&nbsp;&nbsp;'.format(
                                                    user=i.user,
                                                    address=i.address if i.address else '',
                                                    type_display=i.get_type_display(),
                                                    script=i.script,
                                                    )
        elif i.get_type_display() == 'playbook':
            control_display = '<a href="javascript:void(0)" class="btn btn-primary btn-sm mb-1" ' \
                              'info="{user}-{address}" type="{type_display}" onclick="viewcmd(this);">' \
                              '<cmd hidden>/media/{script}</cmd><i class="fas fa-list"></i> playbook详情</a>' \
                              '&nbsp;&nbsp;'.format(
                                                    user=i.user,
                                                    address=i.address if i.address else '',
                                                    type_display=i.get_type_display(),
                                                    script=i.script,
                                                    )
        elif i.get_type_display() == 'module':
            control_display = '<a href="javascript:void(0)" class="btn btn-primary btn-sm mb-1" ' \
                              'info="{user}-{address}" type="{type_display}" onclick="viewcmd(this);">' \
                              '<cmd hidden>{cmd}</cmd><i class="fas fa-list"></i> module详情</a>' \
                              '&nbsp;&nbsp;'.format(
                                                    user=i.user,
                                                    address=i.address if i.address else '',
                                                    type_display=i.get_type_display(),
                                                    cmd=i.cmd,
                                                    )

        control_display = control_display + '<a href="javascript:void(0)" class="btn btn-info btn-sm mb-1" ' \
                                            'id="{detail}" info="{user}-{address}" onclick="viewsshvideo(this);">' \
                                            '<i class="fas fa-video"></i> 回放</a>'.format(
                                                    user=i.user,
                                                    address=i.address if i.address else '',
                                                    detail=i.detail,
                                            )
        tmp.append(control_display)
        data.append(tmp)
    res['data'] = data
    return JsonResponse(res)
