from django.db import models

# Create your models here.


class BatchCmdLog(models.Model):
    TYPE_CHOICES = (
        (1, '命令'),
        (2, '脚本'),
        (3, '上传文件'),
        (4, 'playbook'),
        (5, 'module'),
    )
    user = models.CharField(max_length=64, verbose_name='操作人')
    hosts = models.TextField(verbose_name='主机信息')
    cmd = models.TextField('命令详情/脚本', blank=True, null=True)
    type = models.SmallIntegerField(default=1, choices=TYPE_CHOICES, verbose_name='类型')
    script = models.CharField(max_length=128, blank=True, null=True, verbose_name="脚本(文件名)")
    detail = models.CharField(max_length=128, blank=True, null=True, verbose_name="结果详情(文件名)")
    address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    useragent = models.CharField(max_length=512, blank=True, null=True, verbose_name='User_Agent')
    start_time = models.DateTimeField('会话开始时间')
    create_time = models.DateTimeField('事件时间', auto_now_add=True)

    def __str__(self):
        return self.user

    class Meta:
        ordering = ["-create_time"]
        verbose_name = '批量日志'
        verbose_name_plural = '批量日志'
