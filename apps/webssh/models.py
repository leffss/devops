from django.db import models
# Create your models here.


class TerminalLog(models.Model):
    user = models.CharField(max_length=64, verbose_name='操作人')
    hostname = models.CharField(max_length=128, verbose_name='主机名')
    ip = models.GenericIPAddressField(verbose_name='主机IP')
    protocol = models.CharField(max_length=64, default='ssh', verbose_name="协议")
    port = models.SmallIntegerField(default=22, verbose_name='端口')
    username = models.CharField(max_length=128, verbose_name="用户名")
    cmd = models.TextField('命令详情', blank=True, null=True)
    detail = models.CharField(max_length=128, blank=True, null=True, verbose_name="结果详情(文件名)")
    address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    start_time = models.DateTimeField('会话开始时间')
    create_time = models.DateTimeField('事件时间', auto_now_add=True)

    def __str__(self):
        return self.user

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '在线会话日志'
        verbose_name_plural = '在线会话日志'


class TerminalSession(models.Model):
    PROTOCOL_CHOICES = (    # 目前支持ssh, telnet
        (1, 'ssh'),
        (2, 'telnet'),
        (3, 'rdp'),
        (4, 'vnc'),
        (5, 'sftp'),
        (6, 'ftp'),
    )

    TYPE_CHOICES = (
        (1, 'webssh'),
        (2, 'websftp'),
        (3, 'clissh'),
        (4, 'clisftp'),
        (5, 'webtelnet'),
        (6, 'clitelnet'),
        (7, 'webrdp'),
        (8, 'webvnc'),
    )

    name = models.CharField(max_length=512, verbose_name='会话名称')
    group = models.CharField(default='chat_default', max_length=512, verbose_name='会话组')
    type = models.SmallIntegerField(default=1, choices=TYPE_CHOICES, verbose_name='类型')
    user = models.CharField(max_length=128, verbose_name='用户')
    host = models.GenericIPAddressField(verbose_name='主机')
    port = models.SmallIntegerField(default=22, verbose_name='端口')
    username = models.CharField(max_length=128, verbose_name='账号')
    protocol = models.SmallIntegerField(default=1, choices=PROTOCOL_CHOICES, verbose_name='协议')
    address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    locked = models.BooleanField(default=False, verbose_name='会话状态')
    create_time = models.DateTimeField('会话时间', auto_now_add=True)
    # 主要用于查看 rdp 会话
    connect_info = models.CharField(max_length=128, blank=True, null=True, verbose_name='连接信息')

    def __str__(self):
        return '{0}'.format(self.name)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '在线会话'
        verbose_name_plural = '在线会话'
