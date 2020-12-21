"""
废弃，已使用 celery beat 任务替代
"""
from __future__ import absolute_import, unicode_literals
import os
# 设置默认的Django设置模块。
os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'devops.settings')
# 让django初始化
import django
django.setup()
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.gevent import GeventScheduler
# from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from webssh.views import cls_terminalsession
from django.core.cache import cache
import datetime
import time
import fcntl
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def myfunc():
    with open('/tmp/ap.txt', 'a+') as f:
        f.write('ap\n')


# scheduler = BackgroundScheduler()
# scheduler = GeventScheduler()     # 使用 GeventScheduler 无法正常工作
# scheduler.add_jobstore(DjangoJobStore(), "default")
# scheduler.start()
# register_events(scheduler)
# if scheduler.get_job('my_job_id'):
#     print('my_job_id 存在')
# else:
#     scheduler.add_job(myfunc, 'interval', minutes=1, id='my_job_id')
#     print('添加 my_job_id')
# job = scheduler.add_job(myfunc, 'interval', minutes=5)
# print(job)


"""
使用 redis 防止 apscheduler 多次执行
"""
# is_cls_terminalsession = cache.get('is_cls_terminalsession')
# if is_cls_terminalsession:
#     logger.info('清空 TerminalSession 表任务已存在，关闭 apscheduler')
#     scheduler.shutdown()
# else:
#     logger.info('创建清空 TerminalSession 表任务')
#     cache.set('is_cls_terminalsession', True, 30)
#     scheduler.add_job(
#         cls_terminalsession,
#         trigger='date',
#         run_date=datetime.datetime.now() + datetime.timedelta(seconds=3),
#         args=[scheduler],
#         # id='cls_terminalsession'
#     )


"""
使用文件锁防止 apscheduler 多次执行， 只支持 unix/linux 系统
"""
executors = {
    'default': ThreadPoolExecutor(1)
}
scheduler = BackgroundScheduler(executors=executors)
scheduler.start()
f = None
try:
    f = open("scheduler.lock", "wb")
    # 这里必须使用 lockf, 因为 gunicorn 的 worker 进程都是 master 进程 fork 出来的
    # flock 会使子进程拥有父进程的锁
    # fcntl.flock(flock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    logger.info("pid: %s 获取文件锁成功" % os.getpid())
except BaseException as exc:
    logger.warning("pid: %s 获取文件锁失败: %s 关闭 apscheduler" % (os.getpid(), str(exc)))
    scheduler.shutdown()
    try:
        if f:
            f.close()
    except BaseException:
        pass
else:
    logger.info('创建清空 TerminalSession 表任务')
    scheduler.add_job(
        cls_terminalsession,
        trigger='date',
        run_date=datetime.datetime.now() + datetime.timedelta(seconds=3),
        id='cls_terminalsession'
    )
