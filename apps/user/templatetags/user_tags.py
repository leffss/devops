from django import template
from django.db.models import Q
from django.conf import settings
from server.models import RemoteUserBindHost
from user.models import Permission

register = template.Library()


@register.simple_tag
def count_user_hosts(username):
    hosts = RemoteUserBindHost.objects.filter(
        Q(user__username = username) | Q(group__user__username = username)
    ).distinct().count()
    return hosts


@register.inclusion_tag('menu.html')
def gen_menu(request):
    """
    根据权限动态生成左侧菜单
    :param request:
    :return:
    """
    menus = dict()
    current_url = request.path_info
    for i in request.session[settings.INIT_MENU]:
        if not i['menu']:
            menus[i['title']] = {
                'menu_name': i['title'],
                'menu_icon': i['icon'],
                'menu_url': i['url']
            }
            if i['url'] == current_url:
                menus[i['title']]['active'] = True
            else:
                menus[i['title']]['active'] = False
        else:
            if i['menu'] in menus:
                if i['url'] == current_url:
                    menus[i['menu']]['children'].append({'title': i['title'], 'url': i['url'], 'active': True})
                else:
                    menus[i['menu']]['children'].append({'title': i['title'], 'url': i['url'], 'active': False})
            else:
                if i['url'] == current_url:
                    menus[i['menu']] = {
                        'menu_name': i['menu'],
                        'menu_icon': i['menu_icon'],
                        'children': [
                            {'title': i['title'], 'url': i['url'], 'active': True}
                        ]
                    }
                else:
                    menus[i['menu']] = {
                        'menu_name': i['menu'],
                        'menu_icon': i['menu_icon'],
                        'children': [
                            {'title': i['title'], 'url': i['url'], 'active': False}
                        ]
                    }
            for x in menus[i['menu']]['children']:
                if x['active']:
                    menus[i['menu']]['active'] = True
                    break
            else:
                menus[i['menu']]['active'] = False
    return {'menus': menus}


@register.filter()
def has_permission(request, name):
    """
    粒度按钮控制，判断是否存在此权限
    :param request: request参数
    :param name: url别名
    :return:
    """
    if name in request.session[settings.INIT_PERMISSION]['titles']:
        return True
    return False


@register.filter()
def get_all_permission(request):
    if request.session['issuperuser'] and request.session['username'] == 'admin':
        permissions = Permission.objects.all()
    else:
        permissions = Permission.objects.filter(
            Q(user__username=request.session['username']) | Q(group__user__username=request.session['username'])
        ).distinct()
    return permissions
