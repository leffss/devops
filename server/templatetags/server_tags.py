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

