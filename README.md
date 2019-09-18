# devops
基于 python 3.7 + django 2.2.3 + channels 2.2.0 + celery 4.3.0 + AdminLTE-3.0.0-beta.1 实现的运维 devops 管理系统。具体见 `screenshots` 文件夹中的效果预览图。功能持续完善中。


# 安装
首先其他依赖服务（docker 方式）

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
python3 manage.py proxy_sshd
celery -A devops worker -l info -c 3 --max-tasks-per-child 40
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


# 升级日志

### ver1.7.6
修正 webssh 与 webtelnet 可能会遇到的中文字符被截断以及遇到乱码字符错误退出的 BUG；

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


# 功能
有点多，我很懒，不想描述了。


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


# TODO LISTS
- [ ] 批量执行命令
- [ ] 批量上传文件
- [ ] 集成 ansible，执行 module 与 playbook


更多新功能不断探索发现中.

