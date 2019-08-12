# devops
基于 python 3.7 + django 2.2.3 + AdminLTE-3.0.0-beta.1 实现的运维devops管理系统。具体见 `screenshots` 文件夹中的效果预览图。功能持续完善中。


# 安装
原始方式
```
# 安装相关库
pip install -r requirements.txt

# 运行
python3 manage.py runserver
```

docker方式(centos7)
```
sh start_docker.sh
```

访问首页：http://127.0.0.1:8000
账号： admin     密码：123456


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
![效果](https://github.com/leffss/devops/blob/master/screenshots/12.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/13.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/14.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/15.PNG?raw=true)
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
![效果](https://github.com/leffss/devops/blob/master/screenshots/26.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/27.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/28.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/29.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/30.PNG?raw=true)
![效果](https://github.com/leffss/devops/blob/master/screenshots/31.PNG?raw=true)


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
- [ ] 文件上传
- [ ] 文件下载
- [x] 用户日志审计
- [x] 操作日志审计
- [x] web终端日志审计
- [ ] 所有界面表单数据验证
- [ ] 搜索
- [ ] 后台耗时任务使用 celery
更多新功能不断探索发现中.
