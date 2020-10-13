# 更加详细设置见官方文档：https://docs.gunicorn.org/en/20.0.3/settings.html
import multiprocessing
import os

if not os.path.exists('logs'):
    os.mkdir('logs')

# Server Socket 模块配置
bind = '0.0.0.0:8000'   # 监听， 设置为 [::1]:8000 监听ipv4和ipv6所有IP
# 服务器中在pending状态的最大连接数，即client处于waiting的数目。
# 超过这个数目， client连接会得到一个error。
# 建议值64-2048。
backlog = 2048

# Debugging 模块设置
debug = False
reload = False   # 代码变得是否重启worker，开发模式使用
spew = False    # 跟踪服务器执行的每一个步骤（函数代码等）

# Logging 模块设置
loglevel = 'info'  # 可设置debug info warning error critical
# errorlog = 'logs/error.log'  # 错误日志，设置 '-' 打印到终端错误输出
# accesslog = 'logs/access.log'   # 访问日志，设置 '-' 打印到终端正确输出
errorlog = '-'  # 错误日志，设置 '-' 打印到终端错误输出
accesslog = '-'   # 访问日志，设置 '-' 打印到终端正确输出
access_log_format = '%(t)s %(h)s %({x-real-ip}i)s %({X-Forwarded-For}i)s %({X-Forwarded-Proto}i)s %({X-Forwarded-Port}i)s %({X-Forwarded-Host}i)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'   # 访问日志格式
# 含义如下
# Identifier Description
# h	remote address
# l	'-'
# u	user name
# t	date of the request
# r	status line (e.g. GET / HTTP/1.1)
# m	request method
# U	URL path without query string
# q	query string
# H	protocol
# s	status
# B	response length
# b	response length or '-' (CLF format)
# f	referer
# a	user agent
# T	request time in seconds
# D	request time in microseconds
# L	request time in decimal seconds
# p	process ID
# {Header}i	request header
# {Header}o	response header
# {Variable}e environment variable

# Process Naming 模块设置
proc_name = 'devops_gunicorn'    # 进程名设置，默认：gunicorn

# Security 模块设置
limit_request_line = 4094
limit_request_fields = 100  # 请求头个数限制，默认100，防止DDOS，最大值32768
limit_request_field_size = 8190 # 每个请求头大小限制， 0 为不限制


# Server Mechanics 模块设置
# chdir = /tmp    # 工作目录
daemon = False  # 后台进程模式
pidfile = 'logs/gunicorn.pid'
# worker_tmp_dir = '/tmp' # 临时目录，如果不设置则使用系统默认，推荐设置为内存临时文件系统：tmpfs
# user = 'gunicorn'     # 启动用户
# group = 'gunicorn'    # 启动用户组

# Worker Processes 模块设置
# 启动的进程数，推荐一个cpu核心 2-4 个
workers = multiprocessing.cpu_count() * 2 + 1
# workers = 2
# worker进程的工作方式。 有 sync, eventlet, gevent, tornado, gthread, 缺省值sync。
# sync 为 select 模式，gevent 为 epoll 模式
worker_class = 'gevent'
# 工作进程中线程的数量。建议值2-4 x $(NUM_CORES)， 缺省值1。
# 此配置只适用于gthread 进程工作方式， 因为gevent这种使用的是协程工作方式。
# threads = 100
# 客户端最大同时连接数。只适用于eventlet， gevent工作方式。
worker_connections = 2000
# worker重启之前处理的最大requests数， 缺省值为0表示禁用自动重启。主要是防止内存泄露。
max_requests = 4096
# 抖动参数，防止worker全部同时重启。
max_requests_jitter = 512
# 通常设为30
timeout = 60
# 接收到restart信号后，worker可以在graceful_timeout时间内，继续处理完当前requests。
graceful_timeout = 120
# keepalive, 1-5 秒
# server端保持连接时间。如果 Gunicorn 在负载均衡后面，可以设置高点
keepalive = 5

# 启动 worker 前加载代码，代码只执行一次，但是使用 kill -HUP 重启 gunicorn 后无法更新代码了
preload = False


# Server Hooks 模块设置
def on_starting(server):    # master 主进程启动前执行，只允许一次
    pass


def when_ready(server):     # 服务启动完成后执行，只允许一次
    pass


def on_reload(server):      # 当使用 SIGHUP 信号使 worker 子进程 reload 时执行
    pass


def pre_fork(server, worker):       # worker 子进程启动前执行
    pass


def post_fork(server, worker):      # worker 子进程启动后执行
    pass


# 其他钩子函数，参考官方文档


# SSL 配置
# keyfile = 'server.key'
# certfile = 'server.crt'

# ssl_version 对应值
# SSLv3         0
# SSLv23        1
# TLS           2
# TLSv1         3
# TLSv1_1       4
# TLSv1_2       5
# TLS_SERVER    6
# ssl_version = 5
# ssl_version = 'TLSv1_2'
