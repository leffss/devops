from django.db import models


# Create your models here.
class Host(models.Model):
    hostname = models.CharField(max_length=128, unique=True, verbose_name='主机名')
    ip = models.GenericIPAddressField(verbose_name='主机IP')  # 做了ip映射，ip可能重复，ip:port 不会重复
    wip = models.GenericIPAddressField(verbose_name='公网IP', blank=True, null=True)
    port = models.SmallIntegerField(default=22, verbose_name='端口')
    release = models.CharField(max_length=255, default='CentOS', verbose_name='发行版本')
    memo = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField('添加时间', auto_now_add=True)

    def __str__(self):
        return '[%s] <%s:%s>' % (self.hostname, self.ip, self.port)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '主机'
        verbose_name_plural = '主机'
        unique_together = ('ip', 'port')


class RemoteUser(models.Model):
    """
    名称唯一，用户名可以重复，不同主机登陆用户名相同，密码不同
    """
    name = models.CharField(unique=True, max_length=128, verbose_name="名称")
    username = models.CharField(max_length=128, verbose_name="用户名")
    password = models.CharField(max_length=512, verbose_name="密码")
    enabled = models.BooleanField(default=False, verbose_name='登陆后是否su跳转超级用户')
    superusername = models.CharField(max_length=128, blank=True, null=True, verbose_name="超级用户")
    superpassword = models.CharField(max_length=512, blank=True, null=True, verbose_name="超级密码")
    memo = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField('添加时间', auto_now_add=True)

    def __str__(self):
        return '[%s] <%s>' % (self.name, self.username)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "主机账户"
        verbose_name_plural = "主机账户"


class RemoteUserBindHost(models.Model):
    # on_delete当RemoteUser记录被删时，本表的对应记录也会被删除或者设置为NULL
    remote_user = models.ForeignKey('RemoteUser', blank=True, null=True, on_delete=models.SET_NULL)
    host = models.ForeignKey('Host', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField('添加时间', auto_now_add=True)

    def __str__(self):
        if self.remote_user:
            return '[%s] <%s>' % (self.host.hostname, self.remote_user.username)
        return '[%s]' % (self.host.hostname)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '远程主机'
        verbose_name_plural = '远程主机'
        unique_together = ('host', 'remote_user')
        # 一个用户下，只能绑定同一个主机一次，不能一个用户下绑定两个相同主机
