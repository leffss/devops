#!/usr/bin/env python
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
    
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)('specific.JVxvwNSz!CMCteTrCAHlO', {
        "type": "unlock.message",
        "text": '{"status":3, "message":"当前会话已被管理员锁定"}',
    })
    
    
if __name__ == '__main__':
    main()
