from django.db import models
# Create your models here.


class HostGroup(models.Model):
    group_name = models.CharField(max_length=128, verbose_name="组名")
    # 用户删除时，相关的主机组也删除
    user = models.ForeignKey('user.User', on_delete=models.CASCADE, verbose_name="归属用户")
    memo = models.TextField(blank=True, null=True, verbose_name="备注")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    def __str__(self):
        return self.group_name

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '主机组'
        verbose_name_plural = "主机组"
        unique_together = ('group_name', 'user')  # 同一用户下，主机组必须唯一


class RemoteUser(models.Model):
    """
    名称唯一，用户名可以重复，不同主机登陆用户名相同，密码不同
    """
    name = models.CharField(unique=True, max_length=128, verbose_name="名称")
    username = models.CharField(max_length=128, verbose_name="用户名")
    password = models.CharField(max_length=512, verbose_name="密码")
    domain = models.CharField(blank=True, null=True, max_length=256, verbose_name='AD域验证服务器')
    enabled = models.BooleanField(default=False, verbose_name='登陆后是否su跳转超级用户')
    superusername = models.CharField(max_length=128, blank=True, null=True, verbose_name="超级用户")
    superpassword = models.CharField(max_length=512, blank=True, null=True, verbose_name="超级密码")
    memo = models.TextField(blank=True, null=True, verbose_name='备注')
    create_time = models.DateTimeField('添加时间', auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "主机账户"
        verbose_name_plural = "主机账户"


class RemoteUserBindHost(models.Model):
    PROTOCOL_CHOICES = (    # 目前支持ssh, telnet
        (1, 'ssh'),
        (2, 'telnet'),
        (3, 'rdp'),
        (4, 'vnc'),
        (5, 'sftp'),
        (6, 'ftp'),
    )
    TYPE_CHOICES = (
        (1, '服务器'),
        (2, '防火墙'),
        (3, '路由器'),
        (4, '二层交换机'),
        (5, '三层交换机'),
        (6, '虚拟机'),
        (7, 'PC机'),
    )
    ENV_CHOICES = (
        (1, '正式环境'),
        (2, '测试环境'),
    )
    PLATFORM_CHOICES = (
        (1, 'linux'),
        (2, 'windows'),
        (3, 'unix'),
    )
    hostname = models.CharField(max_length=128, unique=True, verbose_name='主机名')
    type = models.SmallIntegerField(default=1, choices=TYPE_CHOICES, verbose_name='类型')
    ip = models.GenericIPAddressField(verbose_name='主机IP')  # 做了ip映射，ip可能重复，ip:port 不会重复
    wip = models.GenericIPAddressField(verbose_name='公网IP', blank=True, null=True)
    protocol = models.SmallIntegerField(default=1, choices=PROTOCOL_CHOICES, verbose_name='协议')
    env = models.SmallIntegerField(default=1, choices=ENV_CHOICES, verbose_name='环境')
    host_group = models.ManyToManyField('HostGroup', blank=True, verbose_name="主机组")
    port = models.SmallIntegerField(default=22, verbose_name='端口')
    release = models.CharField(max_length=255, default='CentOS', verbose_name='系统/型号')
    platform = models.SmallIntegerField(default=1, choices=PLATFORM_CHOICES, verbose_name='平台')
    # rdp 验证方式，可选项：rdp，tls，nla，nla-ext
    security = models.CharField(blank=True, null=True, max_length=32, verbose_name='rdp验证方式')
    memo = models.TextField(blank=True, null=True, verbose_name='备注')
    # on_delete 当 RemoteUser 记录被删时，阻止其操作
    remote_user = models.ForeignKey('RemoteUser', blank=True, null=True, on_delete=models.PROTECT)
    enabled = models.BooleanField(default=True, verbose_name='是否启用')
    create_time = models.DateTimeField('添加时间', auto_now_add=True)

    def __str__(self):
        return self.hostname

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '远程主机'
        verbose_name_plural = '远程主机'
        unique_together = ('ip', 'protocol', 'port', 'remote_user')
        # 一个用户下，只能绑定同一个主机一次，不能一个用户下绑定两个相同主机


class ServerDetail(models.Model):
    # 远程主机删除此，serverdetail 相关数据也删除
    server = models.OneToOneField('RemoteUserBindHost', on_delete=models.CASCADE)
    cpu_model = models.CharField(max_length=128, blank=True, null=True, verbose_name='CPU型号')
    cpu_number = models.SmallIntegerField(blank=True, null=True, verbose_name='物理CPU个数')
    vcpu_number = models.SmallIntegerField(blank=True, null=True, verbose_name='逻辑CPU个数')
    disk_total = models.CharField(max_length=16, blank=True, null=True, verbose_name='磁盘空间')
    ram_total = models.SmallIntegerField(blank=True, null=True, verbose_name='内存容量')
    swap_total = models.SmallIntegerField(blank=True, null=True, verbose_name='交换空间容量')
    kernel = models.CharField(max_length=128, blank=True, null=True, verbose_name='内核版本')
    system = models.CharField(max_length=128, blank=True, null=True, verbose_name='操作系统')
    filesystems = models.TextField(blank=True, null=True, verbose_name='文件系统')
    interfaces = models.TextField(blank=True, null=True, verbose_name='网卡信息')
    server_model = models.CharField(max_length=128, blank=True, null=True, verbose_name='型号')

    class Meta:
        verbose_name = '主机详细'
        verbose_name_plural = '主机详细'
