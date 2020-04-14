#!/usr/bin/env python
"""
初始化创建 admin 账号
并插入部分测试数据
"""
import os


def main():
    # 使用django配置文件进行设置
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')
    
    # 让django初始化
    import django
    django.setup()
    
    from user.models import User
    from server.models import RemoteUser, RemoteUserBindHost
    from util.tool import hash_code
    from util.crypto import encrypt
    
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
        print('已创建管理员账号：root，密码：123456')

        data = {
            'username': 'leffss',
            'password': hash_code('123456'),
            'nickname': '运维工程师',
            'email': 'leffss@leffss.com',
            'sex': 'male',
            'enabled': True,
            'role': 2,
        }
        User.objects.create(**data)
        print('已创建普通账号：leffss，密码：123456')

        data = {
            'name': '通用root账号',
            'username': 'root',
            'password': encrypt('123456'),
            'enabled': False,
        }
        remote_user = RemoteUser.objects.create(**data)
        print('已创建远程账号：root，密码：123456')

        hosts = {
            'k8s1': '192.168.223.111',
            'k8s2': '192.168.223.112',
            'k8s3': '192.168.223.113',
            'k8s4': '192.168.223.114',
            'k8s5': '192.168.223.115',
            'k8s6': '192.168.223.116',
            'k8s7': '192.168.223.117',
            'k8s8': '192.168.223.118',
        }
        for k, v in hosts.items():
            data = {
                'hostname': k,
                'type': 6,
                'ip': v,
                'protocol': 1,
                'env': 2,
                'platform': 1,
                'port': 22,
                'release': 'CentOS 7',
                'remote_user': remote_user
            }
            RemoteUserBindHost.objects.create(**data)
            print('已创建远程主机：{}_{}'.format(k, v))

    print('初始化结束...')
        
    
if __name__ == '__main__':
    main()
