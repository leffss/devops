# -*- coding: utf-8 -*-
"""
查看 django.db.backends.mysql.base.by 源码发现 django 连接 mysql 时没有使用连接池，
导致每次数据库操作都要新建新的连接并查询完后关闭，更坑的是按照 django 的官方文档设置
CONN_MAX_AGE 参数是为了复用连接，然后设置了 CONN_MAX_AGE 后，每个新连接查询完后并不
会 close 掉，而是一直在那占着。如果在高并发模式下，很容易出现 too many connections
错误。故重写 mysql 连接库，实现连接池功能。
"""
import random
from django.core.exceptions import ImproperlyConfigured

try:
    import MySQLdb as Database
except ImportError as err:
    raise ImproperlyConfigured(
        'Error loading MySQLdb module.\n'
        'Did you install mysqlclient?'
    ) from err

from django.db.backends.mysql.base import *
from django.db.backends.mysql.base import DatabaseWrapper as _DatabaseWrapper

DEFAULT_DB_POOL_SIZE = 5


class DatabaseWrapper(_DatabaseWrapper):
    def get_new_connection(self, conn_params):
        # 获取 DATABASES 配置字典中的 DB_POOL_SIZE 参数
        pool_size = self.settings_dict.get('DB_POOL_SIZE') or DEFAULT_DB_POOL_SIZE
        return ConnectPool.instance(conn_params, pool_size).get_connection()

    def _close(self):
        return None  # 覆盖掉原来的close方法，查询结束后连接不会自动关闭


class ConnectPool(object):
    def __init__(self, conn_params, pool_size):
        self.conn_params = conn_params
        self.pool_size = pool_size
        self.connects = []

    # 实现连接池的单例
    @staticmethod
    def instance(conn_params, pool_size):
        if not hasattr(ConnectPool, '_instance'):
            ConnectPool._instance = ConnectPool(conn_params, pool_size)
        return ConnectPool._instance

    def get_connection(self):
        if len(self.connects) < self.pool_size:
            new_connect = Database.connect(**self.conn_params)
            self.connects.append(new_connect)
            return new_connect
        index = random.randint(0, self.pool_size - 1)   # 随机返回连接池中的连接
        try:
            # 检测连接是否有效，去掉性能更好，但建议保留
            self.connects[index].ping()
        except Exception:
            self.connects[index] = Database.connect(**self.conn_params)
        return self.connects[index]
