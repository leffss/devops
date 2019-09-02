import telnetlib
from threading import Thread
import json
import time
from util.tool import gen_rand_char
from django.conf import settings
from asgiref.sync import async_to_sync
import traceback
from webssh.tasks import celery_save_res_asciinema
import platform


class Telnet:
    """
    由于 telnetlib 库的原因，终端无法显示颜色以及设置终端大小
    """
    def __init__(self, websocker, message):
        self.websocker = websocker
        self.message = message
        self.cmd = ''       # 多行命令
        self.cmd_tmp = ''   # 一行命令
        self.res_file = gen_rand_char(16) + '.txt'
        self.res = ''
        self.tab_mode = False   # 使用tab命令补全时需要读取返回数据然后添加到当前输入命令后
        self.history_mode = False
        self.start_time = time.time()
        self.last_save_time = self.start_time
        self.res_asciinema = []
        
        self.tn = telnetlib.Telnet()

    def connect(self, host, user, password, port=23, timeout=30, wait_time=5, user_pre=b"ogin:", password_pre=b"assword:"):
        """
        是因为telnet本身是弱协议，也就是说它并没有明确定义用户如何登陆，何时输入用户名或者密码，不同的telnet服务有着各自不同的实现方式。
        比如说，有些telnet服务会显示 Login: 来提示用户输入用户名，而另一些则用 username: 进行提示，还有的用 login: 进行提示。
        """
        try:
            self.tn.open(host=host, port=port, timeout=timeout)
            self.tn.read_until(user_pre, timeout=10)
            user = '{0}\n'.format(user).encode('utf-8')
            self.tn.write(user)

            self.tn.read_until(password_pre, timeout=10)
            password = '{0}\n'.format(password).encode('utf-8')
            self.tn.write(password)

            time.sleep(wait_time)     # 服务器响应慢的话需要多等待些时间
            command_result = self.tn.read_very_eager().decode('utf-8')

            self.message['status'] = 0
            self.message['message'] = command_result
            message = json.dumps(self.message)
            self.websocker.send(message)

            self.res += command_result
            if 'Login incorrect' in command_result:
                self.message['status'] = 2
                self.message['message'] = 'connection login faild...'
                message = json.dumps(self.message)
                self.websocker.send(message)
                self.websocker.close(3001)
            self.tn.write(b'export TERM=ansi\n')
            time.sleep(wait_time)
            self.tn.read_very_eager().decode('utf-8')
            # 创建1线程将服务器返回的数据发送到django websocket, 多个的话会极容易导致前端显示数据错乱
            Thread(target=self.websocket_to_django).start()
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
        except:
            self.message['status'] = 2
            self.message['message'] = 'connection faild...'
            message = json.dumps(self.message)
            self.websocker.send(message)
            self.websocker.close(3001)
    
    def su_root(self, superuser, superpassword, wait_time=1):
        self.django_to_ssh('su - {0}\n'.format(superuser))
        time.sleep(wait_time)
        try:
            self.tn.write('{}\n'.format(superpassword).encode('utf-8'))
        except:
            self.close()
            
    def django_to_ssh(self, data):
        try:
            self.tn.write(data.encode('utf-8'))
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
                data = self.tn.read_very_eager().decode('utf-8')
                if not len(data):
                    continue
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
                # 250条结果或者指定秒数就保存一次，这个任务可以优化为使用 celery
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
        try:
            self.message['status'] = 1
            self.message['message'] = 'connection closed...'
            message = json.dumps(self.message)
            if self.websocker.send_flag == 0:
                self.websocker.send(message)
            elif self.websocker.send_flag == 1:
                async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                    "type": "chat.message",
                    "text": message,
                })
            self.websocker.close()
            self.tn.close()
        except:
            pass

    def shell(self, data):
        self.django_to_ssh(data)

