from django.db import models
from server.models import RemoteUserBindHost

# Create your models here.


class User(models.Model):
    SEX_CHOICES = (
        ('male', "男"),
        ('female', "女"),
    )
    ROLE_CHOICES = (
        (0, '其他'),
        (1, '超级管理员'),
        (2, '普通用户'),
    )
    username = models.CharField(max_length=64, unique=True, verbose_name='用户名')
    nickname = models.CharField(max_length=64, blank=True, null=True, verbose_name='昵称')
    password = models.CharField(max_length=256, verbose_name='密码')
    email = models.EmailField(verbose_name='邮箱')
    sex = models.CharField(max_length=32, choices=SEX_CHOICES, default="male", verbose_name='性别')
    remote_user_bind_hosts = models.ManyToManyField(RemoteUserBindHost, blank=True, verbose_name="用户关联的远程主机")
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    role = models.SmallIntegerField(default=2, choices=ROLE_CHOICES, verbose_name='角色')
    groups = models.ManyToManyField('Group', blank=True, verbose_name="所属组")
    memo = models.TextField(blank=True, null=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')

    def __str__(self):
        return '[%s] <%s>' % (self.username, self.nickname)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


class Group(models.Model):
    group_name = models.CharField(max_length=128, unique=True, verbose_name="组名")
    remote_user_bind_hosts = models.ManyToManyField(RemoteUserBindHost, blank=True, verbose_name="组内关联的远程主机")
    memo = models.TextField(blank=True, null=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return '[%s]' % (self.group_name)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "用户组"
        verbose_name_plural = "用户组"


class LoginLog(models.Model):
    event_type_choice = (
        (0, '其他'),
        (1, '登陆'),
        (2, '退出'),
        (3, '登陆错误'),
        (4, '修改密码失败'),
        (5, '修改密码成功'),
        (6, '添加用户'),
        (7, '删除用户'),
        (8, '添加用户组'),
        (9, '删除用户组'),
        (10, '更新用户'),
        (11, '更新用户组'),
    )
    user = models.ForeignKey('User', blank=True, null=True, on_delete=models.SET_NULL, verbose_name='用户')
    event_type = models.SmallIntegerField('事件类型', choices=event_type_choice, default=1)
    detail = models.TextField('事件详情', default='登陆成功')
    address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    create_time = models.DateTimeField('事件时间', auto_now_add=True)

    def __str__(self):
        if self.user:
            return '[%s] <%s:%s>' % (self.event_type, self.user.username, self.user.nickname)
        return '[%s]' % (self.event_type)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '用户日志'
        verbose_name_plural = '用户日志'

