# devops
基于 python 3.7 + django 2.2.3 + channels 2.2.0 + celery 4.3.0 + ansible 2.8.5 + AdminLTE-3.0.0 实现的运维 devops 管理系统。具体见 `screenshots` 文件夹中的效果预览图。
本人为运维工程师，非专业开发，此项目各个功能模块都是现学现用，可能有点地方没有考虑到合理和性能的问题，代码写得烂，不喜勿喷，欢迎 issue。功能持续完善中。


# 部署安装

主机操作系统为 Centos 7.5，python 版本 3.7.2，docker 版本 1.13.1。windows 上就不建议部署了，那是作死的事情。

**安装依赖**
```bash
yum install -y epel-release
yum install -y sshpass python3-devel mysql-devel
```
- ansible 连接插件 connection 使用 ssh 模式（还可以使用 paramiko 等模式）并且密码连接主机时需要使用 sshpass
- python3-devel 与 mysql-devel 为 mysqlclient 库的依赖

**安装 redis（docker 方式）**
```bash
docker run --name redis-server -p 6379:6379 -d redis:latest
```
- channels、缓存、celery以及 session 支持所需，必须

**安装 guacd（docker 方式）**
```bash
docker run --name guacd -p 4822:4822 -d guacamole/guacd
```
- rdp 与 vnc 连接支持所需，非必须
- windows rdp 必须设置为`允许运行任意版本远程桌面的计算机连接(较不安全)(L)`才能连接

**安装 python 依赖库**
```bash
# 安装相关库
pip3 install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
```
- -i 指定阿里源，国外源慢得一逼，我大天朝威武，局域网玩得贼6

**修改 devops/settings.py 配置**

相关配置均有注释，根据实际情况修改。默认数据库使用的是 sqlite3，如果需要使用 mysql，方法如下：

修改 devops/settings.py 中的 `DATABASES` 配置为：
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        # 'ENGINE': 'db_pool.mysql',     # db_pool.mysql 为重写 django 官方 mysql 连接库实现了真正的连接池
        'NAME': 'devops',
        'USER':'devops',
        'PASSWORD':'devops',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        'CONN_MAX_AGE': 600,    # 如果使用 db_pool.mysql 尽量不要设置此参数
        # 数据库连接池大小，mysql 总连接数大小为：连接池大小 * 服务进程数
        'DB_POOL_SIZE': 20,     # 默认 5 个
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
         },
    }
}
```
- 相关数据库与账号必须事先在 mysql 数据库中创建好并授权。

**创建数据库**
```bash
sh delete_makemigrations.sh
rm -f db.sqlite3
# 以上是删除可能存在的开发环境遗留数据
python3 manage.py makemigrations
python3 manage.py migrate
```

**初始化数据**
```bash
python3 manage.py loaddata initial_data.json
python3 init.py
```
- initial_data.json 为权限数据
- init.py 创建超级管理员 admin 以及部分测试数据

**启动 django 服务**
```bash
rm -rf logs/*
export PYTHONOPTIMIZE=1		# 解决 celery 不允许创建子进程的问题
nohup gunicorn -c gunicorn.cfg devops.wsgi:application > logs/gunicorn.log 2>&1 &
nohup daphne -b 0.0.0.0 -p 8001 --access-log=logs/daphne_access.log devops.asgi:application > logs/daphne.log 2>&1 &
nohup python3 manage.py sshd > logs/sshd.log 2>&1 &
nohup celery -A devops worker -l info -c 3 --max-tasks-per-child 40 --prefetch-multiplier 1 --pidfile logs/celery_worker.pid > logs/celery.log 2>&1 &
nohup celery -A devops beat -l info --pidfile logs/celery_worker.pid > logs/celery_beat.log 2>&1 &
```
- gunicorn  处理 http 请求，监听 8000 端口
- daphne 处理 websocket 请求，监听 8001 端口
- sshd 为 ssh 代理服务器，监听 2222 端口，提供调用 securecrt、xshell、putty 以及 winscp 客户端支持，非必须
- celery 后台任务处理，`export PYTHONOPTIMIZE=1` 此环境变量非常重要，不设置无法后台运行 ansible api
- celery_beat 处理 `devops/settings.py` 中设置的 `CELERY_BEAT_SCHEDULE` 定时任务

**nginx  前端代理**
```
yum install -y nginx
```
- 为了方便，就不编译安装，直接 yum 安装，版本是 `nginx-1.16.1`

修改 nginx 配置 /etc/nginx/nginx.conf：
```
# For more information on configuration, see:
#   * Official English Documentation: http://nginx.org/en/docs/
#   * Official Russian Documentation: http://nginx.org/ru/docs/

# base on nginx 1.16.1

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log error;
pid /run/nginx.pid;

# Load dynamic modules. See /usr/share/nginx/README.dynamic.
include /usr/share/nginx/modules/*.conf;

events {
    worker_connections 1024;
    accept_mutex on;
    use epoll;
}
http {
    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for" "$server_name" $server_port';

    # 日志不立即写入磁盘，提高性能
    access_log  /var/log/nginx/access.log  main buffer=32k flush=1m;

    sendfile            on;
    tcp_nopush          on;
    tcp_nodelay         on;
    keepalive_timeout   30;
    types_hash_max_size 2048;
    server_tokens  off;

    include             /etc/nginx/mime.types;
    default_type        application/octet-stream;

    gzip on;
    gzip_min_length 2k;
    gzip_comp_level 4;
    gzip_types text/css text/xml image/gif image/jpeg application/javascript application/rss+xml text/plain image/png image/tiff image/x-icon image/x-ms-bmp image/svg+xml application/json;
    gzip_vary on;
    gzip_buffers 4 16k;
    # gzip_http_version 1.0;

	upstream wsgi-backend {
		ip_hash;
		server 127.0.0.1:8000 max_fails=3 fail_timeout=0;
	}

	upstream asgi-backend {
		ip_hash;
		server 127.0.0.1:8001 max_fails=3 fail_timeout=0;
	}

	server {
        listen 80 default_server;
		listen [::]:80 default_server;
		server_name  _;
		client_max_body_size 30m;
		add_header X-Frame-Options "DENY";
		
		location ~* ^/(media|static) {
			root /home/workspace/devops;   # 此目录根据实际情况修改
			# expires 30d;
			if ($request_filename ~* .*\.(css|js|gif|jpg|jpeg|png|bmp|swf|svg)$)
			{
				expires 7d;
			}
		}

		location /ws {
			try_files $uri @proxy_to_ws;
		}

		location @proxy_to_ws {
			proxy_pass http://asgi-backend;
			proxy_http_version 1.1;
			proxy_set_header Upgrade $http_upgrade;
			proxy_set_header Connection "upgrade";
			proxy_redirect off;
			proxy_set_header Host $host;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Forwarded-Proto $scheme;
			proxy_set_header X-Forwarded-Port $server_port;
			proxy_set_header X-Forwarded-Host $server_name;
			proxy_intercept_errors on;
			recursive_error_pages on;
		}

		location / {
			try_files $uri @proxy_to_app;
		}

		location @proxy_to_app {
			proxy_pass http://wsgi-backend;
			proxy_http_version 1.1;
			proxy_redirect off;
			proxy_set_header Host $host;
			proxy_set_header X-Real-IP $remote_addr;
			proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
			proxy_set_header X-Forwarded-Proto $scheme;
			proxy_set_header X-Forwarded-Port $server_port;
			proxy_set_header X-Forwarded-Host $server_name;
			proxy_intercept_errors on;
			recursive_error_pages on;
		}

		location = /favicon.ico {
				 access_log off;    #关闭正常访问日志
		}

		error_page 404 /404.html;
		location = /404.html {
			root   /usr/share/nginx/html;
			if ( $request_uri ~ ^/favicon\.ico$ ) {    #关闭favicon.ico 404错误日志
				access_log off;
			}
		}

		error_page 500 502 503 504 /50x.html;
		location = /50x.html {
			root   /usr/share/nginx/html;
		}
	}
}
```
- 建议生产环境使用 https 方式，并开启 http2 与 Brotli 压缩（一种比 gzip 更好的压缩方案），具体方法不表

启动 nginx：
```
systemctl start nginx
```
- 启动前建议先检查下配置是否正确：`nginx -t`

访问首页：http://127.0.0.1

超级管理员：
> 账号： admin     密码：123456


# 功能
有点多，看图，不想描述了。


# 存在问题
web 终端（包括 webssh，webtelnet）在使用 chrome 浏览器打开时，很大机率会出现一片空白无法显示 xterm.js 终端的情况。
解决方法是改变一下 chrome 的缩放比例就好了（ctrl + 鼠标滚轮），在 firefox 下无此问题，具体原因未知。


# 升级日志

### ver1.8.7
webssh 新增 zmodem(sz, rz) 上传下载文件支持（webtelnet 理论上也可以实现，原理一样，应该淘汰的协议，就懒得做了）；

### ver1.8.6
优化执行 playbook 逻辑：允许指定组；

优化终端登陆后 su 跳转逻辑：由管理员能够跳转变更为有权限就可跳转；

~~新增 apscheduler 在启动时执行清空 TerminalSession 表；~~

新增 django mysql 连接 ENGINE 优化版本：真正的支持连接池；

修正 clissh 使用 Zmodem 使用 sz 和 rz 时的 BUG；

更新 xterm.js 到 v3.14.5 版本，支持 webssh 与 webtelnet 复制文本内容；

- 此版本新增了一个任务调度模块，目前还是一个不完善的功能，不要太在意，仅供参考

### ver1.8.5
新增批量操作，比如批量删除，批量更新等；

### ver1.8.4
基于 url 实现的粒度到按钮级别的权限控制；

左侧菜单栏根据权限自动生成；

### ver1.8.3
修正终端日志保存时用户名覆盖主机名的 BUG；

新增 ansible 内置变量禁止使用名单，防止通过内置变量（比如 ansible_ssh_pass）获取到主机密码；

新增 django-ratelimit 页面访问频率限制；

远程主机账号密码由明文存储变更为密文存储；

日志审计页面 datatables 变更为服务器端处理数据模式；

修正 web 终端以及批量处理等多处可能产生的越权访问远程主机问题；

### ver1.8.2
新增执行 ansible module；

新增执行 ansible playbook；

### ver1.8.1
完善批量执行命令（增加日志记录）；

新增批量执行脚本（基于 ansible）；

新增批量上传文件（基于 ansible）；

### ver1.8.0
新增主机组；

新增自动获取主机详细信息，比如 CPU，内存等（基于 ansible，仅支持 liunx 主机）；

新增批量执行命令（基于 ansible）；

优化 UI 界面，加入 select2 选项框插件；

新增锁定屏幕功能；

### ver1.7.6
修正 webssh、webtelnet 和 clissh 可能会遇到的中文字符被截断以及遇到乱码字符错误退出的 BUG；

优化 UI 界面，加入动态效果；

### ver1.7.5
修正强制断开 clissh 后保存 2 次终端日志的 BUG；

新增会话在一定时间内无操作自动断开功能（默认 30 分钟，settings.py 中可配置）；

个人信息中新增调用本地 SSH 客户端与本地 SFTP 客户端相关配置；

webssh 终端页面新增文件上传与下载功能(支持 5GB 以下文件，分段上传，不占用服务器内存)；

修正 clissh 连接后无法使用 sz 下载文件和 rz 上传文件的 BUG（Zmodem 只适合上传下载小文件）；

### ver1.7.4
新增 webguacamole、webssh、webtelnet 会话锁定与解锁功能；

微调 web 终端 UI；

### ver1.7.3
新增 webguacamole，理论上支持 RDP、VNC 协议连接主机（VNC 没试过），并支持录像回放；

### ver1.7.2
新增客户端连接 sftp；

linux 平台下使用 celery 任务保存终端会话日志与录像（windows 不支持 celery）；

### ver1.7.1
优化界面；

修复客户端 SSH 连接部分 BUG；

### ver1.7.0
新增浏览器调用 securecrt，xshell，putty 等客户端终端；

新增会话录像审计；

### ver1.6.0 
新增实时查看在线终端会话；

### ver1.5.0 
新增全站表单验证（javascript 正则表达式验证）；

### ver1.4.0 
新增在线终端会话列表查看；

新增强制停止在线终端会话功能；

### ver1.3.0 
完善新增主机，新增主机账号等功能；

### ver1.2.0 
完善功能；

新增 docker 方式部署；

尝试加入 celery 实现异步任务；

### ver1.1.0 
新增 ssh 和 telnet（明文传输的古老协议，不推荐使用）连接远程主机；

### ver1.0.0 
初始版本


# 预览
![效果](https://github.com/leffss/devops/blob/master/screenshots/1.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/2.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/3.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/4.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/5.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/6.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/7.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/8.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/9.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/10.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/12.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/13.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/14.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/16.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/17.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/18.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/19.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/20.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/21.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/22.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/23.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/24.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/25.PNG?raw=true)


# TODO LISTS
- [ ] docker 容器管理
- [ ] k8s 集群管理
- [ ] 自动化部署 ci/cd


# MIT License
```
Copyright (c) 2019-2020 leffss
```


更多新功能不断探索发现中.
