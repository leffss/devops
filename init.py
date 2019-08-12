#!/usr/bin/env python
""" 初始化创建 admin 账号"""
import os
import sys


def main():
    # 使用django配置文件进行设置
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')
    
    # 让django初始化
    import django
    django.setup()
    
    from user.models import User
    from util.tool import hash_code
    
    print('初始化开始...')
    username = 'admin'
    nickname = '超级管理员'
    password = hash_code('123456')
    email = 'admin@admin.com'
    sex = 'male'
    enabled = True
    role = 1
    if User.objects.filter(username=username).count() > 0:
        print('已存在 {} 账号，无需初始化，退出...'.format(username))
    else:
        user = User()
        user.username = username
        user.nickname = nickname
        user.password = password
        user.email = email
        user.sex = sex
        user.enabled = enabled
        user.role = role
        user.save()
        print('已创建账号：{0}，密码：{1}'.format(username, password))
    print('初始化结束...')
        
    
if __name__ == '__main__':
    main()
