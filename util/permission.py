from user.models import Permission
from django.db.models import Q


def init_permission(username, is_super=False):
    """
    提取用户权限与菜单
    :param request:
    :return:
    """
    if is_super:
        permissions = Permission.objects.all()
    else:
        permissions = Permission.objects.filter(
            Q(user__username=username) | Q(group__user__username=username)
        ).distinct()
    permission_dict = dict()
    permission_dict['titles'] = []
    permission_dict['urls'] = []
    for permission in permissions:
        permission_dict['titles'].append(permission.title)
        if permission.url:
            permission_dict['urls'].extend(permission.url.split(','))
    if permission_dict['urls']:
        permission_dict['urls'] = list(set(permission_dict['urls']))      # 去重

    menu_list = list()
    menus = permissions.filter(is_button=False).order_by('order', 'id')
    for menu in menus:
        menu_list.append(
            {
                "title": menu.title,
                "url": menu.url.split(',')[0],
                "icon": menu.icon,
                "menu": menu.menu,
                "menu_icon": menu.men_icon,
            }
        )
    return permission_dict, menu_list
