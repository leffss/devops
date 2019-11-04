from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
 
# 为celery程序设置默认的Django设置模块。
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'devops.settings')
 
# 注册Celery的APP
app = Celery('devops')

# 绑定配置文件
app.config_from_object('django.conf.settings', namespace='CELERY')
 
# 自动发现各个app下的tasks.py文件
app.autodiscover_tasks()
