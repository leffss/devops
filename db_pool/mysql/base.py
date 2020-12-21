# -*- coding: utf-8 -*-
"""
查看 django.db.backends.mysql.base.by 源码发现 django 连接 mysql 时没有使用连接池，
导致每次数据库操作都要新建新的连接并查询完后关闭，更坑的是按照 django 的官方文档设置
CONN_MAX_AGE 参数是为了复用连接，然后设置了 CONN_MAX_AGE 后，每个新连接查询完后并不
会 close 掉，而是一直在那占着。如果在高并发模式下，很容易出现 too many connections
错误。故重写 mysql 连接库，实现连接池功能。
"""
from django.core.exceptions import ImproperlyConfigured
import queue
import threading

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
    """
    使用此库时绝对不能设置 CONN_MAX_AGE 连接参数，否则会造成使用连接后不会快速释放到连接池，从而造成连接池阻塞
    """
    connect_pools = {}
    pool_size = None
    mutex = threading.Lock()

    def get_new_connection(self, conn_params):
        with self.mutex:
            # 获取 DATABASES 配置字典中的 DB_POOL_SIZE 参数
            if not self.pool_size:
                self.pool_size = self.settings_dict.get('DB_POOL_SIZE') or DEFAULT_DB_POOL_SIZE
            if self.alias not in self.connect_pools:
                self.connect_pools[self.alias] = ConnectPool(conn_params, self.pool_size)
            return self.connect_pools[self.alias].get_connection()

    def _close(self):
        with self.mutex:
            # 覆盖掉原来的 close 方法，查询结束后连接释放回连接池
            if self.connection is not None:
                with self.wrap_database_errors:
                    return self.connect_pools[self.alias].release_connection(self.connection)


class ConnectPool(object):
    def __init__(self, conn_params, pool_size):
        self.conn_params = conn_params
        self.pool_size = pool_size
        self.connect_count = 0
        self.connects = queue.Queue()

    def get_connection(self):
        if self.connect_count < self.pool_size:
            self.connect_count = self.connect_count + 1
            return Database.connect(**self.conn_params)
        conn = self.connects.get()
        try:
            # 检测连接是否有效，去掉性能更好，但建议保留
            conn.ping()
        except Exception:
            conn = Database.connect(**self.conn_params)
        return conn

    def release_connection(self, conn):
        self.connects.put(conn)
