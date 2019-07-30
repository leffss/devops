import paramiko
import threading
from threading import Thread
from .tools import get_key_obj
import socket
import json
import time


class SSH:
    def __init__(self, websocker, message):
        self.websocker = websocker
        self.message = message
        self.cmd = ''
        self.res = ''
    
    # term 可以使用 ansi, linux, vt100, xterm, dumb，除了 dumb外其他都有颜色显示
    def connect(self, host, user, password=None, ssh_key=None, port=22, timeout=30,
                term='ansi', pty_width=80, pty_height=24):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if ssh_key:
                key = get_key_obj(paramiko.RSAKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.DSSKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.ECDSAKey, pkey_obj=ssh_key, password=password) or \
                      get_key_obj(paramiko.Ed25519Key, pkey_obj=ssh_key, password=password)

                ssh_client.connect(username=user, hostname=host, port=port, pkey=key, timeout=timeout)
            else:
                ssh_client.connect(username=user, password=password, hostname=host, port=port, timeout=timeout)

            transport = ssh_client.get_transport()
            self.channel = transport.open_session()
            self.channel.get_pty(term=term, width=pty_width, height=pty_height)
            self.channel.invoke_shell()

            for i in range(2):
                recv = self.channel.recv(1024).decode('utf-8')
                self.message['status'] = 0
                self.message['message'] = recv
                message = json.dumps(self.message)
                self.websocker.send(message)
                self.res += recv
            
            # 创建3个线程将服务器返回的数据发送到django websocket（1个线程都可以）
            Thread(target=self.websocket_to_django).start()
            Thread(target=self.websocket_to_django).start()
            Thread(target=self.websocket_to_django).start()
            # self.su_root('root', '123456')    # 切换root测试
        except:
            self.message['status'] = 2
            self.message['message'] = 'Connection faild...'
            self.cmd += self.message['message']
            self.res += self.message['message']
            message = json.dumps(self.message)
            self.websocker.send(message)
            self.websocker.close(3001)

    def resize_pty(self, cols, rows):
        self.channel.resize_pty(width=cols, height=rows)
    
    def su_root(self, superuser, superpassword, wait_time=1):
        self.django_to_ssh('su - {0}\n'.format(superuser))
        time.sleep(wait_time)
        try:
            self.channel.send('{}\n'.format(superpassword))
        except:
            self.close()
    
    def django_to_ssh(self, data):
        try:
            self.channel.send(data)
            if data == '\r':
                data = '\n'
            self.cmd += data
        except:
            self.close()

    def websocket_to_django(self):
        try:
            while True:
                data = self.channel.recv(1024).decode('utf-8')
                if not len(data):
                    return
                self.message['status'] = 0
                self.message['message'] = data
                self.res += data
                message = json.dumps(self.message)
                self.websocker.send(message)
        except:
            self.close()

    def close(self):
        self.message['status'] = 1
        self.message['message'] = 'Connection closed...'
        message = json.dumps(self.message)
        self.websocker.send(message)
        self.channel.close()
        self.websocker.close()

    def shell(self, data):
        # 原作者使用创建线程的方式发送数据到ssh，每次发送都是一个字符，可以不用线程
        # 直接调用函数性能更好
        # Thread(target=self.django_to_ssh, args=(data,)).start()
        self.django_to_ssh(data)
        
        # 原作者将发送数据到django websocket的线程创建函数如果写到这，会导致每在客户端输入一个字符就创建一个线程
        # 最终可能导致线程创建太多，故将其写到 connect 函数中
        # Thread(target=self.websocket_to_django).start()
