from django.db import models
# Create your models here.


class TerminalLog(models.Model):
    user = models.CharField(max_length=64, verbose_name='操作人')
    hostname = models.CharField(max_length=128, verbose_name='主机名')
    ip = models.GenericIPAddressField(verbose_name='主机IP')
    port = models.SmallIntegerField(default=22, verbose_name='端口')
    username = models.CharField(max_length=128, verbose_name="用户名")
    cmd = models.TextField('命令详情')
    address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    start_time = models.DateTimeField('会话开始时间')
    create_time = models.DateTimeField('事件时间', auto_now_add=True)

    def __str__(self):
        return '[%s]' % (self.user)

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '在线会话日志'
        verbose_name_plural = '在线会话日志'


class TerminalLogDetail(models.Model):
    """
    结果详情单独以一对一的关系表存储，提高查询速度
    """
    terminallog = models.OneToOneField('TerminalLog', on_delete=models.CASCADE)
    res = models.TextField('结果详情', default='未记录')

    def __str__(self):
        return '{0}'.format(self.terminallog.user)

    class Meta:
        verbose_name = '在线会话日志结果详情'
        verbose_name_plural = '在线会话日志结果详情'
