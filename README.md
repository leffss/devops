# devops
基于 python 3.7 + django 2.2.3 + channels 2.2.0 + celery 4.3.0 + ansible 2.8.5 + AdminLTE-3.0.0-beta.1 实现的运维 devops 管理系统。具体见 `screenshots` 文件夹中的效果预览图。功能持续完善中。


# 安装
首先其他依赖服务（docker 方式）

**sshpass**
```
yum install -y sshpass
```
- ansible 使用密码连接主机时需要 sshpass 支持

**redis**
```
docker run --name redis-server -p 6379:6379 -d redis:latest
```

**guacd**
```
docker run --name guacd -p 4822:4822 -d guacamole/guacd
```

然后部署 devops

**原始方式**
```
# 安装相关库
pip install -r requirements.txt

# 运行
python3 manage.py runserver
python3 manage.py sshd
export PYTHONOPTIMIZE=1     # 解决 celery 不允许创建子进程的问题
celery -A devops worker -l info -c 3 --max-tasks-per-child 40 --prefetch-multiplier 1
```

**docker 方式（Centos 7）**
```
sh start_docker.sh
```

- 其他依赖服务相关配置见项目配置文件：devops/settings.py
- windows 对 celery 兼容很差，无法正常使用，所以请使用 linux 部署，推荐 Centos 7 系列
- 调用 securecrt、xshell、putty 以及 winscp 客户端使用的是 URL PROTOCOL，具体使用方法见：个人信息 - 配置

访问首页：http://127.0.0.1:8000

账号： admin     密码：123456

**提醒：** 以上部署方式都是开发环境，正式环境部署一般为 nginx(静态资源处理和请求的分发) + uwsgi/gunicorn(处理http) + daphne(处理websocket)，具体方法等后面功能做得差不多了再更新。

**使用 mysql 数据库**
以上是使用的 django 默认的数据库是 sqlite3，如果需要使用 mysql 数据库，方法如下：
首先安装pymysql：
```
pip install pymysql
```
修改 devops/settings.py 中的 `DATABASES` 配置：
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'devops',
        'USER':'devops',
        'PASSWORD':'devops',
        'HOST':'192.168.223.111',
        'PORT':'3306',
        'OPTIONS': {
            # 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'init_command': "SET sql_mode=''",
         },
    }
}
```
- 数据库 devops 以及账号 devops 必须事先在 mysql 数据库中创建好并授权。

在 devops/____init____.py 中添加配置：
```
import pymysql

pymysql.install_as_MySQLdb()
```
然后执行数据库迁移时不出意外会出现以下提示
```
django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3.
```
原因是 django 2.2 默认使用 `MySQLdb` 连接 mysql，但是 python3 已经摒弃这个库，改用 `pymysql`。网上解决方法一般2种：
- 将 django 降低到 2.14 以下即可：这个不用想，降你妹，老子就要用最新的！
- 修改 django 代码支持，就选它了。

修改方法：

**首先**在`[python安装目录内]/site-packages/django/db/backends/mysql/base.py` 中找到以下代码并**注释**：
```
if version < (1, 3, 13):
    raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)
```

**然后**将`[python安装目录内]/site-packages/django/db/backends/mysql/operations.py` 中 146 行找到以下代码：
```
query = query.decode(errors='replace')
```
修改为
```
query = query.encode(errors='replace')
```
再次运行就 ok 了。


# 功能
有点多，看图，不想描述了。


# 升级日志

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
修正强制断开 clissh 后保存 2 次终端日志的BUG；

新增会话在一定时间内无操作自动断开功能（默认 30 分钟，settings.py 中可配置）；

个人信息中新增调用本地 SSH 客户端与本地 SFTP 客户端相关配置；

webssh 终端页面新增文件上传与下载功能(支持 5GB 以下文件，分段上传，不占用服务器内存)；

修正 clissh 连接后无法使用 sz 下载文件和 rz 上传文件的 BUG（Zmodem 只适合上传下载小文件）；

### ver1.7.4
新增 webguacamole、webssh、webtelnet 会话锁定与解锁功能；

微调 web 终端 UI；

### ver1.7.3
新增 webguacamole，支持 RDP、VNC 协议连接主机，并支持录像回放；

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
新增 ssh 和 telnet 协议连接远程主机；

### ver1.0.0 
初始版本


# 预览
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

# TODO LISTS
- [ ] 集成 ansible，执行 module 与 playbook
- [ ] docker 容器管理
- [ ] k8s 集群管理


更多新功能不断探索发现中.

