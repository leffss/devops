from django.db import models

# Create your models here.


class SchedulerHost(models.Model):
    PROTOCOL_CHOICES = (
        (1, 'http'),
        (2, 'https'),
    )
    hostname = models.CharField(max_length=128, blank=True, null=True, verbose_name='主机名')
    ip = models.GenericIPAddressField(verbose_name='主机IP')
    protocol = models.SmallIntegerField(default=2, choices=PROTOCOL_CHOICES, verbose_name='协议')
    port = models.SmallIntegerField(default=443, verbose_name='端口')
    token = models.CharField(max_length=512, verbose_name='token')
    status = models.BooleanField(default=False, verbose_name='状态')
    cron = models.IntegerField(default=0, verbose_name='cron任务数')
    interval = models.IntegerField(default=0, verbose_name='interval任务数')
    date = models.IntegerField(default=0, verbose_name='date任务数')
    executed = models.IntegerField(default=0, verbose_name='总共执行任务数')
    failed = models.IntegerField(default=0, verbose_name='总共失败任务数')
    memo = models.TextField(blank=True, null=True, verbose_name='备注')
    update_time = models.DateTimeField('更新时间', blank=True, null=True, auto_now=True)
    create_time = models.DateTimeField('添加时间', auto_now_add=True)

    def __str__(self):
        return self.hostname

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '调度主机'
        verbose_name_plural = '调度主机'
        unique_together = ('ip', 'port')
