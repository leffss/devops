import telnetlib
from threading import Thread
import json
import time


class Telnet:
    """
    由于 telnetlib 库的原因，终端无法显示颜色以及设置终端大小
    """
    def __init__(self, websocker, message):
        self.websocker = websocker
        self.message = message
        self.cmd = ''
        self.res = ''
        self.tn = telnetlib.Telnet()

    def connect(self, host, user, password, port=23, timeout=30, wait_time=1.5, user_pre=b"ogin:", password_pre=b"assword:"):
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
            if data == '\r':
                data = '\n'
            self.cmd += data
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
                self.websocker.send(message)
        except:
            self.close()

    def close(self):
        try:
            self.message['status'] = 1
            self.message['message'] = 'connection closed...'
            message = json.dumps(self.message)
            self.websocker.send(message)
            self.websocker.close()
            self.tn.close()
        except:
            pass

    def shell(self, data):
        self.django_to_ssh(data)

