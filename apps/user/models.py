from django.db import models
from server.models import RemoteUserBindHost
import json
# Create your models here.


class Permission(models.Model):
    """
    权限
    """
    title = models.CharField(max_length=128, unique=True, verbose_name="标题")
    url = models.CharField(max_length=256, blank=True, null=True, verbose_name='含正则的URL')
    icon = models.CharField(max_length=128, blank=True, null=True, verbose_name='图标')
    # 如果 menu 为空，则本身就是一级菜单，比如仪表盘；不为空则是二级菜单或者按钮
    menu = models.CharField(max_length=128, blank=True, null=True, verbose_name='一级菜单')
    men_icon = models.CharField(max_length=128, blank=True, null=True, verbose_name='一级菜单图标')
    # 当为 True 时，是一个按钮，不是菜单
    is_button = models.BooleanField(default=False, verbose_name='是否为按钮')
    # 排序，菜单显示排序
    # SmallIntegerField 在使用 sqlite3 时字段为 smallint，范围从 -2^15 (-32,768) 到 2^15 - 1 (32,767) 的整型数据。
    # 存储大小为 2 个字节。unsigned 是从 0 到 65535 的整型数据。但是使用 mysql 时就变为 tinyint，范围从 -2^7 (-128) 到
    # 2^7 - 1 (123) 的整型数据。存储大小为 1 个字节。unsigned 是从 0 到 255 的整型数据。所以默认值设置大小要考虑到兼容性。
    # order = models.SmallIntegerField(default=99999, verbose_name='排序')
    order = models.SmallIntegerField(default=123, verbose_name='排序')

    def __str__(self):
        if self.menu:
            return self.menu + '-' + self.title
        return self.title

    class Meta:
        ordering = ["id"]
        verbose_name = "权限"
        verbose_name_plural = "权限"


class User(models.Model):
    SEX_CHOICES = (
        ('male', "男"),
        ('female', "女"),
    )
    ROLE_CHOICES = (
        (1, '超级管理员'),
        (2, '普通用户'),
    )
    username = models.CharField(max_length=64, unique=True, verbose_name='用户名')
    nickname = models.CharField(max_length=64, verbose_name='昵称')
    password = models.CharField(max_length=256, verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱')
    sex = models.CharField(max_length=32, choices=SEX_CHOICES, default="male", verbose_name='性别')
    remote_user_bind_hosts = models.ManyToManyField(RemoteUserBindHost, blank=True, verbose_name="用户关联的远程主机")
    permission = models.ManyToManyField(Permission, blank=True, verbose_name="用户关联的权限")
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    role = models.SmallIntegerField(default=2, choices=ROLE_CHOICES, verbose_name='角色')
    groups = models.ManyToManyField('Group', blank=True, verbose_name="所属组")
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="手机")
    weixin = models.CharField(max_length=64, blank=True, null=True, verbose_name="微信")
    qq = models.CharField(max_length=24, blank=True, null=True, verbose_name="QQ")
    setting_default = {
        'clissh': [
            {
                'name': 'securecrt',
                'path': 'C:\\Program Files (x86)\\VanDyke Software\\Clients\\SecureCRT.exe',
                'args': '/T /N "{username}@{host}-{hostname}" /SSH2 /L {login_user} /PASSWORD {login_passwd} {login_host} /P {port}',
                'enable': True
            },
            {
                'name': 'xshell',
                'path': 'C:\\Program Files (x86)\\NetSarang\\Xmanager Enterprise 5\\Xshell.exe',
                 'args': '-newtab "{username}@{host}-{hostname}" -url ssh://{login_user}:{login_passwd}@{login_host}:{port}',
                 'enable': False
            },
            {
                'name': 'putty',
                'path': 'C:\\Program Files (x86)\\putty\\putty.exe',
                'args': '-l {login_user} -pw {login_passwd} {login_host} -P {port}',
                'enable': False
            },
            {
                'name': 'custom',
                'path': '',
                'args': '',
                'enable': False
            }
        ],
        'clisftp': [
            {
                'name': 'winscp',
                'path': 'C:\\Program Files (x86)\\winscp\\WinSCP.exe',
                'args': '/sessionname="{username}@{host}-{hostname}" {login_user}:{login_passwd}@{login_host}:{port}',
                'enable': True
            },
            {
                'name': 'custom',
                'path': '',
                'args': '',
                'enable': False
            }
        ]
    }
    setting = models.TextField(default=json.dumps(setting_default), blank=True, null=True, verbose_name="设置")
    memo = models.TextField(blank=True, null=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


class Group(models.Model):
    group_name = models.CharField(max_length=128, unique=True, verbose_name="组名")
    remote_user_bind_hosts = models.ManyToManyField(RemoteUserBindHost, blank=True, verbose_name="组关联的远程主机")
    permission = models.ManyToManyField(Permission, blank=True, verbose_name="组关联的权限")
    memo = models.TextField(blank=True, null=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.group_name

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "用户组"
        verbose_name_plural = "用户组"


class LoginLog(models.Model):
    event_type_choice = (
        (1, '登陆'),
        (2, '退出'),
        (3, '登陆错误'),
        (4, '修改密码失败'),
        (5, '修改密码成功'),
        (6, '添加用户'),
        (7, '删除用户'),
        (8, '添加组'),
        (9, '删除组'),
        (10, '更新用户'),
        (11, '更新组'),
        (12, '添加主机'),
        (13, '删除主机'),
        (14, '更新主机'),
        (15, '添加主机用户'),
        (16, '删除主机用户'),
        (17, '更新主机用户'),
        (18, '停止在线会话'),
        (19, '锁定在线会话'),
        (20, '解锁在线会话'),
        (21, '添加主机组'),
        (22, '删除主机组'),
        (23, '更新主机组'),
        (24, '自动添加调度主机'),
    )
    # 当用户被删除后，相关的登陆日志user字段设置为NULL
    # user = models.ForeignKey('User', blank=True, null=True, on_delete=models.PROTECT, verbose_name='用户')
    user = models.CharField(max_length=64, blank=True, null=True, verbose_name="用户")
    event_type = models.SmallIntegerField('事件类型', choices=event_type_choice, default=1)
    detail = models.TextField('事件详情', default='登陆成功')
    address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    create_time = models.DateTimeField('事件时间', auto_now_add=True)

    def __str__(self):
        return self.get_event_type_display()

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '用户日志'
        verbose_name_plural = '用户日志'
