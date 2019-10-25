from django import template
from ..models import RemoteUserBindHost
from django.db.models import Sum, Count
import random


register = template.Library()


def get_field_display(klass, field, value):
    f = klass._meta.get_field(field)
    return dict(f.flatchoices).get(value, value)


@register.simple_tag
def get_recent_hosts(num=5):
    hosts = RemoteUserBindHost.objects.all()[:num]
    return hosts


@register.simple_tag
def get_host_types():
    result = RemoteUserBindHost.objects.values("type").annotate(total=Count("type")).order_by()
    # result = RemoteUserBindHost.objects.all().annotate(total_id=Count("type")).order_by('type')
    res = dict()
    types = []
    for i in result:
        i['type'] = get_field_display(RemoteUserBindHost, 'type', i['type'])
        types.append(i)
    result = RemoteUserBindHost.objects.values("env").annotate(total=Count("env")).order_by()
    envs = []
    for i in result:
        i['env'] = get_field_display(RemoteUserBindHost, 'env', i['env'])
        envs.append(i)
    res['types'] = types
    res['envs'] = envs
    return res


@register.filter()
def convert_byte(byte, arg=2):     # 过滤器, 系统自带的过滤器 filesizeformat 可以到达类似效果，但是系统的只能保留1为小数
    byte = int(byte)
    if byte <= 1024:
        return '{} B'.format(byte)
    elif 1024 < byte <= 1048576:
        return '{} KB'.format('%.{}f'.format(int(arg)) % (byte / 1024))
    elif 1048576 < byte <= 1073741824:
        return '{} MB'.format('%.{}f'.format(int(arg)) % (byte / 1024 / 1024))
    elif 1073741824 < byte <= 1099511627776:
        return '{} GB'.format('%.{}f'.format(int(arg)) % (byte / 1024 / 1024 / 1024))
    elif byte > 1099511627776:
        return '{} TB'.format('%.{}f'.format(int(arg)) % (byte / 1024 / 1024 / 1024 / 1024))


@register.filter()
def minus(total, free):
    total = int(total)
    free = int(free)
    return total - free


@register.filter()
def precent(free, total):    # 过滤器最多2个参数
    free = int(free)
    total = int(total)
    if total == 0:
        return '0 %'
    else:
        return '{} %'.format('%.{}f'.format(0) % (free / total * 100))

