import paramiko
import threading
from threading import Thread
from .tools import get_key_obj
from asgiref.sync import async_to_sync
import socket
from django.conf import settings
import json
import time
import traceback
from util.tool import gen_rand_char
from .tasks import celery_save_res_asciinema
import platform


class SSH:
    def __init__(self, websocker, message):
        self.websocker = websocker
        self.message = message
        self.cmd = ''       # 多行命令
        self.cmd_tmp = ''   # 一行命令
        self.res = ''
        self.tab_mode = False   # 使用tab命令补全时需要读取返回数据然后添加到当前输入命令后
        self.history_mode = False
        self.res_file = gen_rand_char(16) + '.txt'
        self.start_time = time.time()
        self.last_save_time = self.start_time
        self.res_asciinema = []
    
    # term 可以使用 ansi, linux, vt100, xterm, dumb，除了 dumb外其他都有颜色显示
    def connect(self, host, user, password=None, ssh_key=None, port=22, timeout=30,
                term='linux', pty_width=80, pty_height=24):
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

            self.res_asciinema.append(
                json.dumps(
                    {
                     "version": 2,
                     "width": 250,  # 设置足够宽，以便播放时全屏不至于显示错乱
                     "height": 40,
                     "timestamp": int(self.start_time),
                     "env": {"SHELL": "/bin/sh", "TERM": "linux"}
                     }
                )
            )

            for i in range(2):
                recv = self.channel.recv(1024).decode('utf-8')
                self.message['status'] = 0
                self.message['message'] = recv
                message = json.dumps(self.message)
                if self.websocker.send_flag == 0:
                    self.websocker.send(message)
                elif self.websocker.send_flag == 1:
                    async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                        "type": "chat.message",
                        "text": message,
                    })
                self.res += recv

                delay = round(time.time() - self.start_time, 6)
                self.res_asciinema.append(json.dumps([delay, 'o', recv]))

            # 创建3个线程将服务器返回的数据发送到django websocket（1个线程都可以）
            Thread(target=self.websocket_to_django).start()
            # Thread(target=self.websocket_to_django).start()
            # Thread(target=self.websocket_to_django).start()
        except:
            self.message['status'] = 2
            self.message['message'] = 'Connection faild...'
            self.cmd += self.message['message']
            self.res += self.message['message']

            delay = round(time.time() - self.start_time, 6)
            self.res_asciinema.append(json.dumps([delay, 'o', self.message['message']]))

            message = json.dumps(self.message)
            if self.websocker.send_flag == 0:
                self.websocker.send(message)
            elif self.websocker.send_flag == 1:
                async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                    "type": "chat.message",
                    "text": message,
                })
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
            if data == '\r':    # 记录命令
                data = '\n'
                if self.cmd_tmp.strip() != '':
                    self.cmd_tmp += data
                    self.cmd += self.cmd_tmp

                    # print('-----------------------------------')
                    # print(self.cmd_tmp)
                    # print(self.cmd_tmp.encode())
                    # print('-----------------------------------')
                    
                    self.cmd_tmp = ''
            elif data.encode() == b'\x07':
                pass
            else:
                if data == '\t' or data.encode() == b'\x1b':    # \x1b 点击2下esc键也可以补全
                    self.tab_mode = True
                elif data.encode() == b'\x1b[A' or data.encode() == b'\x1b[B':
                    self.history_mode = True
                else:
                    self.cmd_tmp += data
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
                if self.websocker.send_flag == 0:
                    self.websocker.send(message)
                elif self.websocker.send_flag == 1:
                    async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                        "type": "chat.message",
                        "text": message,
                    })

                delay = round(time.time() - self.start_time, 6)
                self.res_asciinema.append(json.dumps([delay, 'o', data]))

                # 250条结果或者指定秒数就保存一次
                if len(self.res_asciinema) > 250 or int(time.time() - self.last_save_time) > 30:
                    tmp = list(self.res_asciinema)
                    self.res_asciinema = []
                    self.last_save_time = time.time()
                    # windows无法正常支持celery任务
                    if platform.system().lower() == 'linux':
                        celery_save_res_asciinema.delay(settings.MEDIA_ROOT + '/' + self.res_file, tmp)
                    else:
                        with open(settings.MEDIA_ROOT + '/' + self.res_file, 'a+') as f:
                            for line in tmp:
                                f.write('{}\n'.format(line))

                if self.tab_mode:
                    tmp = data.split(' ')
                    # tab 只返回一个命令时匹配
                    # print(tmp)
                    if len(tmp) == 2 and tmp[1] == '' and tmp[0] != '':
                        self.cmd_tmp = self.cmd_tmp + tmp[0].encode().replace(b'\x07', b'').decode()
                    elif len(tmp) == 1 and tmp[0].encode() != b'\x07':  # \x07 蜂鸣声
                        self.cmd_tmp = self.cmd_tmp + tmp[0].encode().replace(b'\x07', b'').decode()
                    self.tab_mode = False
                if self.history_mode:   # 不完善，只支持向上翻一个历史命令
                    # print(data)
                    if data.strip() != '':
                        self.cmd_tmp = data
                    self.history_mode = False
        except:
            self.close()

    def close(self):
        self.message['status'] = 1
        self.message['message'] = 'Connection closed...'
        message = json.dumps(self.message)
        if self.websocker.send_flag == 0:
            self.websocker.send(message)
        elif self.websocker.send_flag == 1:
            async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                "type": "chat.message",
                "text": message,
            })
        self.websocker.close()
        self.channel.close()

    def shell(self, data):
        # 原作者使用创建线程的方式发送数据到ssh，每次发送都是一个字符，可以不用线程
        # 直接调用函数性能更好
        # Thread(target=self.django_to_ssh, args=(data,)).start()
        self.django_to_ssh(data)
        
        # 原作者将发送数据到django websocket的线程创建函数如果写到这，会导致每在客户端输入一个字符就创建一个线程
        # 最终可能导致线程创建太多，故将其写到 connect 函数中
        # Thread(target=self.websocket_to_django).start()
