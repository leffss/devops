#!/usr/bin/env python
import os
import sys
import datetime
import time


def main():
    # 使用django配置文件进行设置
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')
    
    # 让django初始化
    import django
    django.setup()
    
    from django.core.cache import cache
    cache.set('test_123', ['x', 'y'], 600)
    print(cache.get('test_123'))
    print(type(cache.get('test_123')))
    
    cache.delete('leffss')


def convert_byte(byte):
    byte = int(byte)
    if byte <= 1024:
        return '{} B'.format(byte)
    elif 1024 < byte <= 1048576:
        return '{} KB'.format('%.2f' % (byte / 1024))
    elif 1048576 < byte <= 1073741824:
        return '{} MB'.format('%.2f' % (byte / 1024 / 1024))
    elif 1073741824 < byte <= 1099511627776:
        return '{} GB'.format('%.2f' % (byte / 1024 / 1024 / 1024))
    elif byte > 1099511627776:
        return '{} TB'.format('%.2f' % (byte / 1024 / 1024 / 1024 / 1024))


if __name__ == '__main__':
    # main()
    # x = b'\xe8\xb5'
    # print(x.decode('utf-8'))
    # y = '知'
    # print(y.encode('utf-8'))
    # print(y.encode('gbk'))
    #
    # a = 'xxxx'
    # print(a[0:2])
    # print(a[100:])

    # msg = format('PLAY_{}'.format('xx'), '*<50')
    # print(msg)
    #
    # msg = format('xx_{}'.format('yyy'), '*<50')
    # print(msg)
    #
    # a = {'hosts': '5,4,3,2,1', 'dst': '', 'backup': True, 'src': '/devops/media/tmp/hello.yml'}
    # if 'hosts' not in a:
    #     print('hosts not in')

    # a = 2588262400
    a = 1048576
    print(convert_byte(a))

