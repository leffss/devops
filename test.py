#!/usr/bin/env python
import os
from datetime import timedelta


if __name__ == '__main__':

    # 使用django配置文件进行设置
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')
    # 让django初始化
    import django
    django.setup()

    from redismultibeat import RedisMultiScheduler
    from devops.celery import app

    schduler = RedisMultiScheduler(app=app)
    for task in schduler.iter_tasks():
        print(task)

    # print('remove----------------------', end='')
    # print(schduler.remove('task_check_scheduler'))
    # for task in schduler.iter_tasks():
    #     print(task)
    #
    # print(schduler.remove('task_check_scheduler'))
    #
    # print('add----------------------', end='')
    # print(schduler.add(**{
    #     'name': 'task_check_scheduler_cron_2',
    #     'task': 'tasks.tasks.task_check_scheduler',
    #     'schedule': timedelta(seconds=7200),
    #     "args": (None, 1, 3),
    # }))
    # for task in schduler.iter_tasks():
    #     print(task)
    #
    # print('modify----------------------', end='')
    # print(schduler.modify(**{
    #     'name': 'task_check_scheduler_cron_2',
    #     'task': 'tasks.tasks.task_check_scheduler',
    #     'schedule': timedelta(seconds=1600),
    #     "args": (None, 1, 3),
    # }))
    # for task in schduler.iter_tasks():
    #     print(task)
    #
    # print(schduler.task('task_check_scheduler'))
    #
    # print(schduler.remove_all())
    #
    # for task in schduler.iter_tasks():
    #     print(task)
    #
    print(schduler.remove_all())
