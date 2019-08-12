from django import template
from django.db.models import Q
from server.models import RemoteUserBindHost

register = template.Library()


@register.simple_tag
def count_user_hosts(username):
    hosts = RemoteUserBindHost.objects.filter(
        Q(user__username = username) | Q(group__user__username = username)
    ).distinct().count()
    return hosts

