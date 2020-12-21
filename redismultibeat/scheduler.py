# -*- coding: utf-8 -*-
"""
基于：https://github.com/liuliqiang/celerybeatredis
重写优化逻辑、完善功能等，只测试过 celery 4.3.0 版本
启动后会读取 celery 配置中的任务，类似：
CELERY_BEAT_SCHEDULE = {    # celery 定时任务, 会覆盖 redis 当中相同任务名任务
    'task_check_scheduler_interval': {  # 任务名(随意起)
        'task': 'tasks.tasks.task_check_scheduler',  # 定时任务函数路径
        'schedule': timedelta(seconds=30),  # 任务循环时间
        # "args": None,  # 参数
        "args": (None, 0, 3),  # 参数
        "limit_run_time": 5,    # 限制运行次数
    },
    'task_check_scheduler_cron': {
        'task': 'tasks.tasks.task_check_scheduler',
        'schedule': crontab(minute='*/1', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'),  # cron 任务
        # "args": None,  # 参数
        "args": (None, 0, 3),  # 参数
    }
}

动态添加任务：
from redismultibeat import RedisMultiScheduler
from devops.celery import app

schduler = RedisMultiScheduler(app=app)

schduler.add(**{
    'name': 'task_check_scheduler_cron_2',
    'task': 'tasks.tasks.task_check_scheduler',
    'schedule': timedelta(seconds=7200),
    "args": (None, 1, 3),
})

动态删除任务：
schduler.remove('task_check_scheduler')

动态修改任务：
schduler.modify(**{
    'name': 'task_check_scheduler_cron_2',
    'task': 'tasks.tasks.task_check_scheduler',
    'schedule': timedelta(seconds=1600),
    "args": (None, 1, 3),
    "limit_run_time": 5,    # 限制运行次数
})

"""
import random
import traceback
import sys
from time import mktime
from functools import partial
import jsonpickle
from celery.beat import Scheduler, ScheduleEntry
from redis import Redis
from redis.sentinel import Sentinel
from celery import current_app
from celery.utils.log import get_logger
from redis.exceptions import LockError
import urllib.parse as urlparse

logger = get_logger(__name__)
debug, info, error, warning = (logger.debug, logger.info, logger.error, logger.warning)
MAXINT = sys.maxsize    # 最大整数，用于提取 redis 中所有任务
DEFAULT_CELERY_BEAT_REDIS_SCHEDULER_URL = 'redis://127.0.0.1:6379/0'
DEFAULT_CELERY_BEAT_REDIS_SCHEDULER_KEY = 'celery:beat:tasks'
DEFAULT_CELERY_BROKER_TRANSPORT_OPTIONS = {"master_name": "master"}
DEFAULT_CELERY_BEAT_MAX_LOOP_INTERVAL = 300
DEFAULT_CELERY_BEAT_REDIS_MULTI_NODE_MODE = False
DEFAULT_CELERY_BEAT_REDIS_LOCK_KEY = 'celery:beat:lock'
DEFAULT_CELERY_BEAT_REDIS_LOCK_TTL = 60
DEFAULT_CELERY_BEAT_REDIS_LOCK_SLEEP = None
DEFAULT_CELERY_BEAT_FLUSH_TASKS = False


class CustomScheduleEntry(ScheduleEntry):
    """
    重写官方 ScheduleEntry 以支持 limit_run_time 设置
    Arguments:
        name (str): 参考 celery 官方文档
        schedule (~celery.schedules.schedule): 参考 celery 官方文档
        args (Tuple): 参考 celery 官方文档
        kwargs (Dict): 参考 celery 官方文档
        options (Dict): 参考 celery 官方文档
        last_run_at (~datetime.datetime): 参考 celery 官方文档
        total_run_count (int): 参考 celery 官方文档
        relative (bool): 参考 celery 官方文档
        limit_run_time (int): 限制任务执行次数，>=0, 0 为不限制
    """

    limit_run_time = 0

    def __init__(self, limit_run_time=None, *args, **kwargs):
        self.limit_run_time = limit_run_time or 0
        ScheduleEntry.__init__(self, *args, **kwargs)

    def __reduce__(self):
        return self.__class__, (
            self.limit_run_time,
            self.name, self.task, self.last_run_at, self.total_run_count,
            self.schedule, self.args, self.kwargs, self.options,
        )


class RedisMultiScheduler(Scheduler):
    Entry = CustomScheduleEntry

    def __init__(self, *args, **kwargs):
        app = kwargs['app']
        self.flush_tasks = app.conf.get("CELERY_BEAT_FLUSH_TASKS", DEFAULT_CELERY_BEAT_FLUSH_TASKS)
        self.schedule_url = app.conf.get("CELERY_BEAT_REDIS_SCHEDULER_URL", DEFAULT_CELERY_BEAT_REDIS_SCHEDULER_URL)
        self.key = app.conf.get("CELERY_BEAT_REDIS_SCHEDULER_KEY", DEFAULT_CELERY_BEAT_REDIS_SCHEDULER_KEY)
        # redis 哨兵模式 sentinels 支持
        if self.schedule_url.startswith('sentinel://'):
            self.broker_transport_options = app.conf.get("CELERY_BROKER_TRANSPORT_OPTIONS", DEFAULT_CELERY_BROKER_TRANSPORT_OPTIONS)
            self.rdb = self.sentinel_connect(self.broker_transport_options['master_name'])
        else:
            self.rdb = Redis.from_url(self.schedule_url)
        Scheduler.__init__(self, *args, **kwargs)
        self.max_interval = app.conf.get("CELERY_BEAT_MAX_LOOP_INTERVAL", DEFAULT_CELERY_BEAT_MAX_LOOP_INTERVAL)
        app.add_task = partial(self.add, self)
        # 多实例模式锁
        self.multi_mode = app.conf.get("CELERY_BEAT_REDIS_MULTI_NODE_MODE", DEFAULT_CELERY_BEAT_REDIS_MULTI_NODE_MODE)
        if self.multi_mode:
            self.lock_key = app.conf.get("CELERY_BEAT_REDIS_LOCK_KEY", DEFAULT_CELERY_BEAT_REDIS_LOCK_KEY)
            self.lock_ttl = app.conf.get("CELERY_BEAT_REDIS_LOCK_TTL", DEFAULT_CELERY_BEAT_REDIS_LOCK_TTL)
            self.lock_sleep = app.conf.get("CELERY_BEAT_REDIS_LOCK_SLEEP", DEFAULT_CELERY_BEAT_REDIS_LOCK_SLEEP)
            self.lock = self.rdb.lock(self.lock_key, timeout=self.lock_ttl)

    def _when(self, entry, next_time_to_run, **kwargs):
        return mktime(entry.schedule.now().timetuple()) + (self.adjust(next_time_to_run) or 0)

    def setup_schedule(self):
        # if self.flush_tasks:
        #     self.remove_all()

        # init entries
        self.merge_inplace(self.app.conf.CELERY_BEAT_SCHEDULE)
        tasks = [jsonpickle.decode(entry) for entry in self.rdb.zrange(self.key, 0, -1)]    # -1 表示取所有
        for entry in tasks:
            if hasattr(entry.schedule, 'human_seconds'):
                info('add task: ' + str('name: ' + entry.name + '; func: ' + entry.task + '; args: ' +
                     entry.args.__str__() + '; each: ' + entry.schedule.human_seconds) + '; limit_run_time: ' + str(entry.limit_run_time)
                     )
            else:
                cron = '{minute} {hour} {day_of_month} {month_of_year} {day_of_week} ' \
                       '(minute/hour/day_of_month/month_of_year/day_of_week)'.format(
                    minute=entry.schedule._orig_minute,
                    hour=entry.schedule._orig_hour,
                    day_of_month=entry.schedule._orig_day_of_month,
                    month_of_year=entry.schedule._orig_month_of_year,
                    day_of_week=entry.schedule._orig_day_of_week,
                )
                info('add task: ' + str('name: ' + entry.name + '; func: ' + entry.task + '; args: ' +
                                         entry.args.__str__() + '; cron: ' + cron) + '; limit_run_time: ' + str(entry.limit_run_time))

    def merge_inplace(self, tasks):
        # 重启 beat 调度会执行该函数
        if self.flush_tasks:
            self.remove_all()

        old_entries = self.rdb.zrangebyscore(self.key, 0, MAXINT, withscores=True)
        old_entries_dict = dict({})
        for task, score in old_entries:
            if not task:
                break
            entry = jsonpickle.decode(task)
            old_entries_dict[entry.name] = (entry, score)
        # 清空调度任务
        self.rdb.delete(self.key)
        # tasks 是配置文件中写的定时任务
        with self.rdb.pipeline() as pipe:   # 使用 pipeline 提交，性能更好
            for key in tasks:
                last_run_at = 0
                e = self.Entry(**dict(tasks[key], name=key, app=self.app))
                if key in old_entries_dict:
                    # 若配置文件和已存数据库中的任务重叠，获取数据库中上次运行的时间后从旧数据中删除
                    last_run_at = old_entries_dict[key][1]
                    del old_entries_dict[key]
                pipe.zadd(self.key, {jsonpickle.encode(e): min(last_run_at, self._when(e, e.is_due()[1], ) or 0)})
            # 将旧任务重新添加到调度任务当中
            for key, tasks in old_entries_dict.items():
                pipe.zadd(self.key, {jsonpickle.encode(tasks[0]): tasks[1]})
            pipe.execute()
        # debug(self.rdb.zrange(self.key, 0, -1))

    def is_due(self, entry):
        return entry.is_due()

    def _tick(self):
        tasks = self.rdb.zrangebyscore(
            self.key, 0,
            self.adjust(mktime(self.app.now().timetuple()), drift=0.010),
            withscores=True) or []
        next_times = [self.max_interval, ]
        with self.rdb.pipeline() as pipe:
            for task, score in tasks:
                entry = jsonpickle.decode(task)
                is_due, next_time_to_run = self.is_due(entry)
                next_times.append(next_time_to_run)
                if is_due:
                    try:
                        info("scheduler task entry: {} to publisher, total_run_count: {}, limit_run_time: {}".format(entry.name, entry.total_run_count + 1, entry.limit_run_time))
                        result = self.apply_async(entry)  # 添加任务到worker队列
                    except Exception as exc:
                        error('Message Error: %s\n%s',
                              exc, traceback.format_stack(), exc_info=True)
                    else:
                        debug('%s sent. id->%s', entry.task, result.id)
                    next_entry = self.reserve(entry)
                    pipe.zrem(self.key, task)  # 删除旧的任务
                    if next_entry.limit_run_time == 0 or next_entry.total_run_count < next_entry.limit_run_time:
                        # 将旧任务重新计算时间后再添加
                        pipe.zadd(self.key, {jsonpickle.encode(next_entry): self._when(next_entry, next_time_to_run, ) or 0})
                    else:
                        logger.info("task entry: {} limit to run {} times, stopped".format(entry.name, entry.limit_run_time))
            pipe.execute()

        # 获取最近一个需要执行的任务的时间
        next_task = self.rdb.zrangebyscore(self.key, 0, MAXINT, withscores=True, num=1, start=0)
        if not next_task:
            # info("no next task found")
            return min(next_times)
        entry = jsonpickle.decode(next_task[0][0])
        next_times.append(self.is_due(entry)[1])
        return min(next_times)

    def tick(self, **kwargs):
        # 每个任务重新调度会执行
        if self.multi_mode:
            if self.lock.acquire(blocking=False):
                # debug("Redis Lock acquired")
                result = self._tick()
                self.lock.release()
                # debug("Redis Lock released")
                return result
            if self.lock_sleep is None:
                next_time = random.randint(1, self.lock_ttl)    # 如果未获取到锁，随机 sleep
            else:   # 或者 sleep 设置的值
                next_time = self.lock_sleep
            info("Redis Lock not acquired, sleep {} s".format(next_time))
            return next_time
        else:
            return self._tick()

    def add(self, **kwargs):
        e = self.Entry(app=current_app, **kwargs)
        tasks = self.rdb.zrange(self.key, 0, -1) or []
        for task in tasks:
            entry = jsonpickle.decode(task)
            if entry.name == e.name:
                warning("task: {} is exists, can not add".format(e.name))
                return False
        # 其中 jsonpickle.encode(e) [任务序列化]为值，self._when(e, e.is_due()[1], ) or 0 [最后运行时间]为 score
        self.rdb.zadd(self.key, {jsonpickle.encode(e): self._when(e, e.is_due()[1], ) or 0})
        return True

    def remove(self, task_name):
        """
        删除任务还可以用另一种逻辑实现：
        调用 remove 时不实际删除，而是将其存入一个redis hash队列集合中，
        然后在调用 tick 时添加任务到 worker 前判断任务是否删除或者执行
        """
        tasks = self.rdb.zrange(self.key, 0, -1) or []
        for idx, task in enumerate(tasks):
            entry = jsonpickle.decode(task)
            if entry.name == task_name:
                self.rdb.zremrangebyrank(self.key, idx, idx)
                return True
        else:
            warning("task: {} is not exists, can not remove".format(task_name))
            return False

    def modify(self, **kwargs):
        e = self.Entry(app=current_app, **kwargs)
        tasks = self.rdb.zrange(self.key, 0, -1) or []
        for idx, task in enumerate(tasks):
            entry = jsonpickle.decode(task)
            if entry.name == e.name:    # 先删除任务再创建
                with self.rdb.pipeline() as pipe:
                    pipe.zremrangebyrank(self.key, idx, idx)
                    pipe.zadd(self.key, {jsonpickle.encode(e): self._when(e, e.is_due()[1], ) or 0})
                return True
        warning("task: {} is not exists, can not modify".format(e.name))
        return False

    def remove_all(self):
        if self.rdb.exists(self.key):
            info("remove all exist tasks in rdb")
            self.rdb.delete(self.key)
            return True
        else:
            warning("tasks key: {} is not exists in rdb".format(self.key))
            return False

    def task(self, task_name):
        tasks = self.rdb.zrange(self.key, 0, -1) or []
        for task in tasks:
            entry = jsonpickle.decode(task)
            if entry.name == task_name:
                return entry
        else:
            warning("task: {} is not exists".format(task_name))
            return None

    def tasks(self, start=0, end=-1):
        # 返回任务列表
        return [jsonpickle.decode(entry) for entry in self.rdb.zrange(self.key, start, end)]

    def iter_tasks(self, start=0, end=-1):
        # 返回任务迭代器
        return (jsonpickle.decode(entry) for entry in self.rdb.zrange(self.key, start, end))

    def close(self):
        self.sync()
        if self.multi_mode:
            try:
                self.lock.release()
            except LockError:
                pass
        self.rdb.close()

    def sentinel_connect(self, master_name):
        url = urlparse.urlparse(self.schedule_url)

        def parse_host(s):
            if ':' in s:
                host, port = s.split(':', 1)
                port = int(port)
            else:
                host = s
                port = 26379

            return host, port

        if '@' in url.netloc:
            auth, hostspec = url.netloc.split('@', 1)
        else:
            auth = None
            hostspec = url.netloc

        if auth and ':' in auth:
            _, password = auth.split(':', 1)
        else:
            password = None
        path = url.path
        if path.startswith('/'):
            path = path[1:]
        hosts = [parse_host(s) for s in hostspec.split(',')]
        sentinel = Sentinel(hosts, password=password, db=path)
        master = sentinel.master_for(master_name)
        return master

    @property
    def info(self):
        # 返回 Schedule 器信息
        return '    . db -> {self.schedule_url}, key -> {self.key}, multi_mode -> {self.multi_mode}'.format(self=self)
