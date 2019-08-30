# devops
基于 python 3.7 + django 2.2.3 + AdminLTE-3.0.0-beta.1 实现的运维devops管理系统。具体见 `screenshots` 文件夹中的效果预览图。功能持续完善中。


# 安装
原始方式
```
# 安装相关库
pip install -r requirements.txt

# 运行
python3 manage.py runserver
python3 manage.py proxy_sshd
```

docker方式(Centos 7)
```
sh start_docker.sh
```

- 注意，celery 与 channel_layers 依赖 redis 服务，默认使用 redis 服务：地址 127.0.0.1 ，端口 6379
- redis 相关配置见项目配置文件：settings.py
- windows 对 celery 兼容很差，无法正常使用，所以请使用 linux 部署，推荐 Centos 7 系列

访问首页：http://127.0.0.1:8000
账号： admin     密码：123456


# 升级日志
### ver1.7.2
新增客户端连接sftp；
linux平台下使用celery任务保存终端会话日志与录像(windows不支持celery)；

### ver1.7.1
优化界面；
修复客户端SSH连接部分BUG；

### ver1.7.0
新增浏览器调用securecrt,xshell,putty等客户端终端；
新增会话录像审计；

### ver1.6.0 
新增实时查看在线终端会话；

### ver1.5.0 
新增全站表单验证(原生javascript正则表达式验证)；

### ver1.4.0 
新增在线终端会话列表查看；
新增强制停止在线终端会话功能；

### ver1.3.0 
完善新增主机，新增主机账号等功能；


### ver1.2.0 
完善功能；
新增 docker 方式部署；
尝试加入 celery 4.3.0 实现异步任务；

### ver1.1.0 
新增ssh和telnet协议连接远程主机；

### ver1.0.0 
初始版本


# 效果
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
![效果](https://github.com/leffss/devops/blob/master/screenshots/11.PNG?raw=true)


# TODO LISTS
- [x] 用户登陆
- [x] 查看用户信息
- [x] 修改用户信息
- [x] 修改用户密码
- [ ] 重置用户密码
- [x] 查看用户
- [x] 查看用户组
- [x] 添加用户
- [x] 添加用户组
- [x] 修改用户
- [x] 修改用户组
- [x] 删除用户
- [x] 删除用户组
- [ ] 权限管理(已实现部分)
- [ ] 仪表盘
- [x] 查看主机
- [x] 查看主机用户
- [x] 添加主机
- [x] 添加主机用户
- [x] 修改主机
- [x] 修改主机用户
- [x] 删除主机
- [x] 删除主机用户
- [ ] 主机信息自动获取
- [ ] 主机监控信息查看(zabbix调用)
- [ ] 批量命令
- [ ] 批量脚本
- [x] webssh终端
- [x] webtelnet终端
- [x] 网页调用securecrt,xshell,putty,winscp等终端(目前只支持windows)
- [ ] websftp终端
- [x] 查看在线会话列表
- [x] 实时查看在线会话
- [ ] 锁定实时在线会话
- [x] 强制关闭在线会话
- [ ] 文件上传
- [ ] 文件下载
- [x] 用户日志审计
- [x] 操作日志审计
- [x] web终端日志审计
- [x] web终端操作录像
- [x] 所有界面表单数据验证(原生javascript正则表单式验证)
- [ ] 搜索
- [ ] 后台耗时任务使用 celery

更多新功能不断探索发现中.

