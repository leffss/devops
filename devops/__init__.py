from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

# from .job import scheduler    # 第一个获取到文件锁的进程执行任务后，如果在运行中途进程关闭重新启动了一个新的，则依然会多次执行

__all__ = ['celery_app']
# __all__ = ['celery_app', 'scheduler']

# import pymysql

# pymysql.install_as_MySQLdb()
