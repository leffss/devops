import telnetlib
from threading import Thread
import json
import time
from util.tool import gen_rand_char, res as save_res
from django.conf import settings
from asgiref.sync import async_to_sync
import traceback
import socket
import sys
import os
import re
from util.control import remove_control_chars
from mp_readline import mp_readline
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    terminal_exipry_time = settings.CUSTOM_TERMINAL_EXIPRY_TIME
except Exception:
    terminal_exipry_time = 60 * 30


BufferSize = 4096


class Telnet:
    """
    由于 telnetlib 库的原因，终端无法显示颜色以及设置终端大小
    """
    def __init__(self, websocker, message):
        self.websocker = websocker
        self.message = message
        self.cmd = ''       # 多行命令
        self.cmd_tmp = ''   # 一行命令
        self.res = ''
        self.start_time = time.time()
        tmp_date1 = time.strftime("%Y-%m-%d", time.localtime(int(self.start_time)))
        tmp_date2 = time.strftime("%Y%m%d%H%M%S", time.localtime(int(self.start_time)))
        if not os.path.isdir(os.path.join(settings.RECORD_ROOT, tmp_date1)):
            os.makedirs(os.path.join(settings.RECORD_ROOT, tmp_date1))
        self.res_file = settings.RECORD_DIR + '/' + tmp_date1 + '/' + 'webtelnet_' + \
                        tmp_date2 + '_' + gen_rand_char(16) + '.txt'
        self.last_save_time = self.start_time
        self.res_asciinema = []
        self._buffer = b''
        self.tn = telnetlib.Telnet()
        mp_readline.TESTING = True
        self.rl = mp_readline.MpReadline()
        self.tab_mode = False   # 使用tab命令补全时需要读取返回数据然后添加到当前输入命令后
        self.history_mode = False
        self.enter = False  # 是否输入回车 \r, 为 True 时则根据 ssh 服务端返回的数据判断是否是执行的命令或者是编辑文本
        self.ctrl_z = False
        self.ctrl_c = False

    def connect(self, host, user, password, port=23, timeout=60 * 30, wait_time=3, user_pre=b"ogin:", password_pre=b"assword:"):
        """
        是因为telnet本身是弱协议，也就是说它并没有明确定义用户如何登陆，何时输入用户名或者密码，不同的telnet服务有着各自不同的实现方式。
        比如说，有些telnet服务会显示 Login: 来提示用户输入用户名，而另一些则用 username: 进行提示，还有的用 login: 进行提示。
        """
        try:
            self.tn.open(host=host, port=port, timeout=timeout)
            login_user = self.tn.read_until(user_pre, timeout=15)
            user = '{0}\n'.format(user).encode('utf-8')
            self.tn.write(user)

            self.tn.read_until(password_pre, timeout=15)
            password = '{0}\n'.format(password).encode('utf-8')
            self.tn.write(password)

            time.sleep(wait_time)     # 服务器响应慢的话需要多等待些时间
            command_result = self.tn.read_very_eager().decode('utf-8')

            self.message['status'] = 0
            self.message['message'] = command_result
            message = json.dumps(self.message)
            self.websocker.send(message)

            self.res += command_result
            if 'incorrect' in command_result or 'faild' in command_result or '失败' in command_result \
                    or '错误' in command_result or 'error' in command_result:
                self.message['status'] = 2
                self.message['message'] = 'connection login faild...'
                message = json.dumps(self.message)
                self.websocker.send(message)
                self.websocker.close(3001)
            else:
                self.res_asciinema.append(
                    json.dumps(
                        {
                            "version": 2,
                            "width": 250,  # 设置足够宽，以便播放时全屏不至于显示错乱
                            "height": 40,
                            "timestamp": int(self.start_time),
                            "env": {"SHELL": "/bin/sh", "TERM": "xterm"}
                        }
                    )
                )
                delay = round(time.time() - self.start_time, 6)
                self.res_asciinema.append(json.dumps([delay, 'o', command_result]))
            self.tn.write(b'export TERM=xterm\n')    # 设置后才能使用clear清屏命令
            time.sleep(wait_time)
            self.tn.read_very_eager().decode('utf-8')
            # 创建1线程将服务器返回的数据发送到django websocket, 多个的话会极容易导致前端显示数据错乱
            Thread(target=self.websocket_to_django).start()
        except Exception:
            logger.error(traceback.format_exc())
            self.message['status'] = 2
            self.message['message'] = 'connection faild...'
            message = json.dumps(self.message)
            self.websocker.send(message)
            self.websocker.close(3001)
    
    def su_root(self, superuser, superpassword, wait_time=1):
        self.django_to_telnet('su - {0}\n'.format(superuser))
        time.sleep(wait_time)
        try:
            self.tn.write('{}\n'.format(superpassword).encode('utf-8'))
        except Exception:
            logger.error(traceback.format_exc())
            self.close()
            
    def django_to_telnet(self, data):
        try:
            self.tn.write(data.encode('utf-8'))
            if data == '\r':  # 回车，开始根据服务端返回判断是否是命令，这种判断方式的特性就导致了无法是否禁止命令功能，当然想绝对禁止命令本身就是一个伪命题
                if self.cmd_tmp.strip() != '':
                    self.enter = True
            elif data.encode() == b'\x07':  # 响铃
                pass
            elif data == '\t' or data.encode() == b'\x1b':  # \x1b 点击2下esc键也可以补全
                self.tab_mode = True
            elif data.encode() == b'\x1b[A' or data.encode() == b'\x1b[B':
                self.history_mode = True
            elif data.encode() == b'\x03':  # 输入命令后先 ctrl + v，然后 ctrl + c 需要两次才能取消
                self.ctrl_c = True
            elif data.encode() == b'\x1a':  # ctrl + z
                self.ctrl_z = True
            else:
                self.cmd_tmp += data
        except Exception:
            logger.error(traceback.format_exc())
            self.close()

    def websocket_to_django(self):
        try:
            while 1:
                # read_very_eager 方法读取时会是无限循环，性能比较低
                # data = self.tn.read_very_eager().decode('utf-8')
                # if not len(data):
                #     continue

                # expect 使用正则匹配所有返回内容，还可以实现超时无返回内容断开连接
                if len(self._buffer) >= 1:
                    x = self._buffer[:BufferSize]
                    self._buffer = self._buffer[BufferSize:]
                else:
                    n, y, z = self.tn.expect([br'[\s\S]+'], timeout=terminal_exipry_time)
                    self._buffer += z
                    x = self._buffer[:BufferSize]  # 一次最多截取 BufferSize 个字符
                    self._buffer = self._buffer[BufferSize:]
                if not len(x):
                    raise socket.timeout

                try:
                    data = x.decode('utf-8')
                except UnicodeDecodeError:  # utf-8中文占3个字符，可能会被截断，需要拼接
                    try:
                        if len(self._buffer) >= 1:
                            x += self._buffer[:1]
                            self._buffer = self._buffer[1:]
                        else:
                            n, y, z = self.tn.expect([br'[\s\S]+'], timeout=terminal_exipry_time)
                            if len(z) > 1:
                                self._buffer += z
                                x += self._buffer[:1]
                                self._buffer = self._buffer[1:]
                            else:
                                x += z
                        data = x.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            if len(self._buffer) >= 1:
                                x += self._buffer[:1]
                                self._buffer = self._buffer[1:]
                            else:
                                n, y, z = self.tn.expect([br'[\s\S]+'], timeout=terminal_exipry_time)
                                if len(z) > 1:
                                    self._buffer += z
                                    x += self._buffer[:1]
                                    self._buffer = self._buffer[1:]
                                else:
                                    x += z
                            data = x.decode('utf-8')
                        except UnicodeDecodeError:
                            data = x.decode('utf-8', 'ignore')  # 拼接2次后还是报错则证明结果是乱码，强制转换
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
                # 指定条结果或者指定秒数或者占用指定大小内存就保存一次
                if len(self.res_asciinema) > 2000 or int(time.time() - self.last_save_time) > 60 or \
                        sys.getsizeof(self.res_asciinema) > 2097152:
                    tmp = list(self.res_asciinema)
                    self.res_asciinema = []
                    self.last_save_time = time.time()
                    save_res(self.res_file, tmp)

                if self.enter:
                    self.enter = False
                    if not data.startswith("\r\n"):  # 回车后结果不以\r\n开头的肯定不是命令
                        self.cmd_tmp = ''
                    else:
                        if re.match(rb'^\r\n\s+\x1b.*$', x):  # 终端为 xterm,linux 等显示颜色类型时在 vi 编辑模式下回车
                            self.cmd_tmp = ''
                        # elif x == b'\r\n':     # todo 正常模式下 vi 文件会返回 \r\n ,终端为 dumb 类型时在 vi 编辑模式下回车也会返回 \r\n，
                        #     self.cmd_tmp = ''
                        else:  # 记录真正命令, rl 不支持中文命令
                            cmd_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                            cmd = self.rl.process_line(self.cmd_tmp.encode("utf-8"))
                            if not cmd:  # 有可能 rl 库会返回 None，重试一次
                                mp_readline.TESTING = True
                                self.rl = mp_readline.MpReadline()
                                cmd = self.rl.process_line(self.cmd_tmp.encode("utf-8"))

                            if cmd:
                                self.cmd += cmd_time + "\t" + remove_control_chars(cmd) + '\n'
                            else:
                                logger.error(
                                    "recv from server: {} \nerror command: {}".format(x, self.cmd_tmp.encode("utf-8")))
                                self.cmd += cmd_time + "\t" + remove_control_chars(self.cmd_tmp) + '\n'
                            self.cmd_tmp = ''
                else:
                    if self.tab_mode:  # todo 兼容有问题
                        self.tab_mode = False
                        tmp = data.split(' ')
                        # tab 只返回一个命令时匹配
                        # print(tmp)
                        if len(tmp) == 2 and tmp[1] == '' and tmp[0] != '':
                            self.cmd_tmp = self.cmd_tmp + tmp[0].encode().replace(b'\x07', b'').decode()
                        elif len(tmp) == 1 and tmp[0].encode() != b'\x07':  # \x07 蜂鸣声
                            self.cmd_tmp = self.cmd_tmp + tmp[0].encode().replace(b'\x07', b'').decode()

                    # 多次上下箭头查找历史命令返回数据中可能会包含 \x1b[1P 导致 rl 无法解析命令，具体原因没有深究
                    if self.history_mode:
                        self.history_mode = False
                        if x != b'' and x != b'\x07':
                            x = re.sub(rb'\x1b\[\d+P', b'', x)
                            self.cmd_tmp += x.decode("utf-8")

                    if self.ctrl_c:  # 取消命令
                        self.ctrl_c = False
                        # if x == b'^C\r\n':
                        if re.match(rb'^\^C\r\n[\s\S]*$', x) or re.match(rb'^\r\n[\s\S]*$', x):
                            self.cmd_tmp = ""
                    if self.ctrl_z:
                        self.ctrl_z = False
                        if re.match(rb'^[\s\S]*\[\d+\]\+\s+Stopped\s+\S+[\s\S]*$', x):
                            self.cmd_tmp = ""
        except socket.timeout:
            self.message['status'] = 1
            self.message['message'] = '由于长时间没有操作或者没有数据返回，连接已断开!'
            message = json.dumps(self.message)
            if self.websocker.send_flag == 0:
                self.websocker.send(message)
            elif self.websocker.send_flag == 1:
                async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                    "type": "chat.message",
                    "text": message,
                })
            self.close(send_message=False)
        except Exception:
            logger.error(traceback.format_exc())
            self.close()

    def close(self, send_message=True):
        try:
            if send_message:
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
        except Exception:
            # logger.error(traceback.format_exc())
            pass

    def shell(self, data):
        self.django_to_telnet(data)
