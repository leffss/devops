# devops
基于 python 3.7.9 + django 2.2.16 + channels 2.4.0 + celery 4.4.7 + ansible 2.9.14 + AdminLTE-3.0.0 实现的运维 devops 管理系统。具体见 `screenshots` 文件夹中的效果预览图。
本人为运维工程师，非专业开发，项目各个功能模块都是现学现用，可能有的地方暂时没有考虑合理和性能的问题。


# 功能
看图。


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


# 部署安装

环境：Centos 7.5，python 3.7.9，docker 1.13.1，项目目录为 `/home/workspace/devops` 。

**1. 安装依赖**
```bash
yum install -y epel-release
yum install -y gcc sshpass python3-devel mysql-devel
```
- ansible 连接插件 connection 使用 ssh 模式（还可以使用 paramiko 等模式）并且密码连接主机时需要使用 sshpass
- python3-devel 与 mysql-devel 为 mysqlclient 库的依赖
- 不建议使用 pymysql 代替 mysqlclient ，因为 pymysql 为纯 python 编写的库，性能较低

**2. 安装 mysql（docker 方式）**
```bash
docker run -d --name mysql -e MYSQL_ROOT_PASSWORD=123456 -p 3306:3306 mysql:5.7.31
```

**3. 安装 redis（docker 方式）**
```bash
docker run --name redis-server -p 6379:6379 -d redis:6.0.8
```
- channels、缓存、celery以及 session 支持所需，必须

**4. 安装 guacd（docker 方式）**
```bash
docker run --name guacd -e GUACD_LOG_LEVEL=info -v /home/workspace/devops/media/guacd:/fs -p 4822:4822 -d guacamole/guacd:1.1.0
```
- rdp 与 vnc 连接支持所需，非必须
- rdp 必须设置为`允许运行任意版本远程桌面的计算机连接(较不安全)(L)`才能连接，也就说目前暂不支持 nla 登陆方式
- `-v /home/workspace/devops/media/guacd:/fs` 挂载磁盘，用于远程挂载文件系统实现上传和下载文件

**5. 安装 python 依赖库**
```bash
# 安装相关库
pip3 install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
```
- -i 指定阿里源，速度飞起，我大 TC 威武，局域网玩得贼 6

**6. 修改 devops/settings.py 配置**

相关配置均有注释，根据实际情况修改。默认数据库使用的是 sqlite3，如果需要使用 mysql，方法如下：

修改 devops/settings.py 中的 `DATABASES` 配置为：
```python
DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.mysql',
        'ENGINE': 'db_pool.mysql',     # db_pool.mysql 为重写 django 官方 mysql 连接库实现了真正的连接池
        'NAME': 'devops',
        'USER':'devops',
        'PASSWORD':'devops',
        'HOST':'127.0.0.1',
        'PORT':'3306',
        # 'CONN_MAX_AGE': 600,    # 如果使用 db_pool.mysql 绝对不能设置此参数，否则会造成使用连接后不会快速释放到连接池，从而造成连接池阻塞
        # 数据库连接池大小，mysql 总连接数大小为：连接池大小 * 服务进程数
        'DB_POOL_SIZE': 3,     # 默认 5 个
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
         },
    }
}
```
- 相关数据库(不需创建表)与账号必须事先在 mysql 数据库中创建好并授权。

**7. 迁移数据库**
```bash
sh delete_makemigrations.sh
rm -f db.sqlite3
# 以上是删除可能存在的开发环境遗留数据
python3 manage.py makemigrations
python3 manage.py migrate
```

**8. 初始化数据**
```bash
python3 manage.py loaddata initial_data.json
python3 init.py
```
- initial_data.json 为权限数据
- init.py 创建超级管理员 admin 以及部分测试数据，可根据实际情况修改

**9. 启动相关服务**
```bash
rm -rf logs/*
export PYTHONOPTIMIZE=1		# 解决 celery 不允许创建子进程的问题
nohup celery -A devops worker -l info -c 3 --max-tasks-per-child 40 --prefetch-multiplier 1 --pidfile logs/celery_worker.pid > logs/celery.log 2>&1 &
nohup celery -A devops beat -l info --pidfile logs/celery_worker.pid > logs/celery_beat.log 2>&1 &
nohup python3 manage.py sshd > logs/sshd.log 2>&1 &
nohup daphne -b 0.0.0.0 -p 8001 --access-log=logs/daphne_access.log devops.asgi:application > logs/daphne.log 2>&1 &
nohup gunicorn -c gunicorn.cfg devops.wsgi:application > logs/gunicorn.log 2>&1 &
```
- gunicorn 处理 http 请求，监听 8000 端口
- daphne 处理 websocket 请求，监听 8001 端口
- sshd 为 ssh 代理服务器，监听 2222 端口，提供调用 securecrt、xshell、putty 以及 winscp 客户端支持，非必须
- celery 后台任务处理进程，`export PYTHONOPTIMIZE=1` 此环境变量非常重要，不设置无法后台运行 ansible api
- celery_beat 定时任务处理进程，读取 `devops/settings.py` 中设置的 `CELERY_BEAT_SCHEDULE` 定时任务，详见 v1.8.8 升级日志
- 需要停止时 kill 相应的进程，然后删除 logs 目录下所有的 pid 文件即可

**10. 配置 nginx 前端代理**
```
yum install -y nginx
```
- 为了方便，就不编译安装，直接 yum 安装，版本为 `nginx-1.16.1`

修改 nginx 配置 /etc/nginx/nginx.conf 如下：
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
- 建议生产环境使用 https 方式，并开启 http2 与 Brotli 压缩（一种比 gzip 更好的压缩方案），具体方法不表，
可以参考根目录下的 `make_nginx.sh` 与 `nginx.conf`。

启动 nginx：
```
systemctl start nginx
```
- 启动前建议先检查下配置是否正确：`nginx -t`

**11. 访问首页：http://127.0.0.1**

初始超级管理员：
> 账号： admin     密码：123456


# 已知问题或者不足
1. 代码的质量以我现在的眼光来看都太差了，但是这个项目的初衷也只是学习而已，也就没有动力重构优化了。

2. web 终端（包括 webssh，webtelnet）在使用 chrome 浏览器打开时，很大机率会出现一片空白无法显示 xterm.js 终端的情况。
解决方法是改变一下 chrome 窗口大小就好了，在 firefox 下也有无此问题，但出现的机率小一些，具体原因未知。

3. 关于使用 vue 做前后端分离，这肯定是以后的趋势，但是由于个人时间精力的问题，只能是慢慢来吧。

4. 数据权限是有一点小问题的，在某些特定的情况下会越权，细心的同学可以在代码中发现。

5. webssh 使用 zmodem 上传下载还有很多可以优化的地方，可以参考我的 go 项目 [gowebssh](https://github.com/leffss/gowebssh) 。

6. webrdp 下载文件也还可以优化。


# 升级日志
### ver2.2.2
优化 supervisord 日志输出配置；

修正 ‘日志审计 - 操作日志’ 中无法按类型排序的问题；

### ver2.2.1
新增 celery beat 定时任务自动清除数据库历史数据，详见 devops/settings.py 相关设置；

### ver2.2.0
升级 webguacamole，支持设置 AD 域账号以及设置多种验证方式（any、rdp、tls、nla、nla-ext）；

升级部分依赖：
- celery 4.3.0 到 4.4.7；
- channel 2.2.0 到 2.4.0；
- channel-redis 2.4.0 到 3.1.0；
- daphne 2.3.0 到 2.5.0；
- pyasn1 0.4.3 到 0.4.8；
- cryptography 2.7 到 2.8；
- gunicorn 20.0.3 到 20.0.4；
- supervisor 4.1.0 到 4.2.1；
- redis 3.3.11 到 3.5.3；
- django-redis 4.10.0 到 4.12.1；
- requests==2.22.0 到 2.24.0；
- jsonpickle 1.2 到 1.4.1；
- gssapi==1.6.2 到 1.6.9；
- django-cachalot 2.3.1 到 2.3.2；
- ansible 2.9.2 到 2.9.14；

### ver2.1.1
修正 greenlet 与 gunicorn 的兼容性问题；

### ver2.1.0
增强 zmodem 命令兼容性，新增支持 rz -e \ rz -S \ rz -e -S 命令；

新增 django_cachalot 缓存 sql 数据库查询结果，提高整体响应速度；

### ver2.0.0
优化 web 终端无法显示 _ 符号的问题（xterm v3 默认的渲染器 canvas 有兼容问题 ，故改用 dom，v4 版本不存在此问题）；

完全重构 db_pool.mysql 连接池（以前的版本存在的问题：会出现多个调用同时使用同一个连接，进而导致数据安全问题）；

### ver1.9.0
优化 webssh 与 webtelnet 终端大小自动调整功能；

优化 webssh、webtelnet 与 clissh 命令记录功能；
- 记录执行时间
- 支持控制字符
- 支持历史命令
- 支持识别 vi/vim 与 emacs 编辑器（使用 dumb 等无颜色的终端类型时会识别错误，
所以就限制 webssh 使用 xterm 终端类型， clissh 使用 linux\ansi\xterm 终端类型）
- 支持识别 ctrl + c 与 ctrl + z（其他特殊操作可能部分会不兼容）
- tab 自动补全命令无法正常识别（tab 补全操作太复杂，不好判断）
- 无法识别 top 等类似命令中输入的操作命令
- 无法识别中文命令
- 识别命令的准确率只能尽可能的提高，应该没有那个堡垒机(包括商业的)敢说自己准确率 100% 吧
- 真正想实现 100% 准确率，应该只有修改 shell 源码或者调用 shell 历史命令了（但是这些方式都不是太现实）

优化 webrdp 下载文件时录像数据记录逻辑（不保存下载的文件内容到录像结果）

### ver1.8.9
修正 clissh 与 webssh 使用 zmodem 时传输中途执行了取消操作后会丢失后续操作记录的 bug；

新增 webrdp 与 webvnc 挂载文件系统实现上传和下载文件；
- 下载文件的方法是将需要下载的文件拖动到挂载的文件系统中的 `download` 文件夹中
，简单测试了下，在 chrome（版本 81）下下载 300MB 的文件会导致 chrome 占用过大内存而崩溃；
而 firefox（版本 72）也会占用较大内存（比 chrome 稍微小一些），但是不会崩溃，可以正常下载文件。
所以需要下载大文件时建议先在远程主机上分卷压缩一下，然后再批量下载小的分卷文件。
- 上传文件的方法是通过点击浏览器上传文件，上传好的文件会在挂载的文件系统根目录中
- 仅测试过 webrdp

新增 webrdp 与 webvnc 会话实时查看功能；
- 仅测试过 webrdp

新增 webrdp 与 webvnc 屏幕键盘
- 仅测试过 webrdp

### ver1.8.8
新增修改版 celery beat：
- 兼容读取原版配置文件中的静态任务；
- 使用 redis 有序集合存储任务，在此基础上实现了任务的动态添加、修改和删除；
- 新增 redis 分布式锁，实现运行多个 beat 实例而不会重复执行任务（官方只允许运行一个 beat 实例）；
- 新增 limit_run_time 参数限制任务运行次数；
- 具体使用方法参考 `devops/settings.py` 配置以及 `redismultibeat/scheduler.py` 注释；

### ver1.8.7
webssh 新增 zmodem(sz, rz) 上传下载文件支持（webtelnet 理论上也可以实现，原理一样，应该淘汰的协议，就懒得做了）；

### ver1.8.6
优化执行 playbook 逻辑：允许指定组；

优化终端登陆后 su 跳转逻辑：由管理员能够跳转变更为有权限就可跳转；

~~新增 apscheduler 在启动时执行清空 TerminalSession 表；~~

新增 django mysql 连接 ENGINE 优化版本：真正的支持连接池；

修正 clissh 使用 zmodem(sz, rz) 时的一些 bug；

更新 xterm.js 到 v3.14.5 版本，支持 webssh 与 webtelnet 复制文本内容；

- 此版本新增了一个任务调度模块，目前只是一个尝试，估计要烂尾，不要太在意，仅供参考

### ver1.8.5
新增批量操作，比如批量删除，批量更新等；

### ver1.8.4
基于 url 实现的粒度到按钮级别的权限控制（有点像 RBAC ，但不是）；

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

webssh 终端页面新增文件上传与下载功能(支持 4GB 以下文件，分段上传，不占用服务器内存)；

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


# TODO LISTS
- [ ] docker 容器管理
- [ ] k8s 集群管理
- [ ] 自动化部署 ci/cd


# MIT License
```
Copyright (c) 2019-2020 leffss.
```


更多新功能不断探索发现中.
