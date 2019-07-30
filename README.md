# mycmdb
基于 python 3.7 + django 2.2.3 + AdminLTE-3.0.0-beta.1 实现的运维devops管理系统。具体见 `screenshots` 文件夹中的效果预览图。功能持续完善中。


# 安装
```
# 安装相关库
pip install -r requirements.txt

# 运行
python3 manage.py runserver
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


# TODO LISTS
- [x] 用户登陆
- [ ] 查看用户信息
- [ ] 修改用户信息
- [ ] 修改用户密码
- [ ] 重置用户密码
- [x] 查看用户
- [x] 查看用户组
- [ ] 添加用户
- [ ] 添加用户组
- [ ] 修改用户
- [ ] 修改用户组
- [ ] 删除用户
- [ ] 删除用户组
- [ ] 权限管理
- [ ] 仪表盘
- [x] 查看主机
- [x] 查看主机用户
- [ ] 添加主机
- [ ] 添加主机用户
- [ ] 修改主机
- [ ] 修改主机用户
- [ ] 删除主机
- [ ] 删除主机用户
- [ ] 批量命令
- [x] web终端
- [x] 用户日志审计
- [ ] 操作日志审计
- [x] web终端日志审计
- [ ] 所有界面表单数据验证
- [ ] 搜索
