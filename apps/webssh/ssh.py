import paramiko
from threading import Thread
from .tools import get_key_obj
from asgiref.sync import async_to_sync
import socket
from django.conf import settings
import json
import time
import sys
import os
import traceback
from util.tool import gen_rand_char, res as save_res
from util.control import remove_control_chars
from mp_readline import mp_readline
import re
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


try:
    terminal_exipry_time = settings.CUSTOM_TERMINAL_EXIPRY_TIME
except Exception:
    terminal_exipry_time = 60 * 30

# sz
zmodemszstart = b'**\x18B00000000000000\r\x8a\x11'
zmodemszend = b'**\x18B0800000000022d\r\x8a'

# rz
zmodemrzstart = b'**\x18B0100000023be50\r\x8a\x11'   # rz
zmodemrzestart = b'**\x18B0100000063f694\r\x8a\x11'  # rz -e
zmodemrzsstart = b'**\x18B0100000223d832\r\x8a\x11'  # rz -S
zmodemrzesstart = b'**\x18B010000026390f6\r\x8a\x11'  # rz -e -S
zmodemrzend = b'**\x18B0800000000022d\r\x8a'

# zmodem cancel
zmodemcancel = b'\x18\x18\x18\x18\x18\x08\x08\x08\x08\x08'


BufferSize = 4096   # 4096 足够，高于 4096 时使用 zmodem 传输时会出现错误


class SSH:
    def __init__(self, websocker, message):
        self.websocker = websocker
        self.message = message
        self.cmd = ''       # 记录多行处理过的命令
        self.cmd_tmp = ''   # 记录一行待处理的命令
        self.res = ''
        self.start_time = time.time()
        tmp_date1 = time.strftime("%Y-%m-%d", time.localtime(int(self.start_time)))
        tmp_date2 = time.strftime("%Y%m%d%H%M%S", time.localtime(int(self.start_time)))
        if not os.path.isdir(os.path.join(settings.RECORD_ROOT, tmp_date1)):
            os.makedirs(os.path.join(settings.RECORD_ROOT, tmp_date1))
        self.res_file = settings.RECORD_DIR + '/' + tmp_date1 + '/' + 'webssh_' + \
                        tmp_date2 + '_' + gen_rand_char(16) + '.txt'
        self.last_save_time = self.start_time
        self.res_asciinema = []
        self.zmodem = False
        self.zmodemOO = False
        mp_readline.TESTING = True
        self.rl = mp_readline.MpReadline()
        self.tab_mode = False   # 使用tab命令补全时需要读取返回数据然后添加到当前输入命令后
        self.history_mode = False
        self.enter = False  # 是否输入回车 \r, 为 True 时则根据 ssh 服务端返回的数据判断是否是执行的命令或者是编辑文本
        self.ctrl_z = False
        self.ctrl_c = False
    
    # term 可以使用 ansi, linux, vt100, xterm, dumb，除了 dumb外其他都有颜色显示
    def connect(self, host, user, password=None, ssh_key=None, port=22, timeout=30,
                term='xterm', pty_width=80, pty_height=24):
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

            # 如果socket连接在指定时间内无数据交互会断开，原理就是读取socket连接，如果指定时间内无返回就抛出异常
            # 需要注意：当在终端上运行无输入内容但是会阻塞当前阻断的程序时如果超过这个时间也会被断开
            self.channel.settimeout(terminal_exipry_time)    # 30分钟

            self.res_asciinema.append(
                json.dumps(
                    {
                     "version": 2,
                     "width": 250,  # 设置足够宽，以便播放时全屏不至于显示错乱
                     "height": 40,
                     "timestamp": int(self.start_time),
                     "env": {"SHELL": "/bin/sh", "TERM": term}
                     }
                )
            )

            for i in range(2):
                recv = self.channel.recv(4096).decode('utf-8')
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
        except Exception:
            print(traceback.format_exc())
            self.message['status'] = 2
            self.message['message'] = 'Connection faild...'
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
        except Exception:
            print(traceback.format_exc())
            self.close()
    
    def django_to_ssh(self, data):
        try:
            self.channel.send(data)
            if not self.zmodem and not self.zmodemOO:
                if data == '\r':    # 回车，开始根据服务端返回判断是否是命令，这种判断方式的特性就导致了无法是否禁止命令功能，当然想绝对禁止命令本身就是一个伪命题
                    if self.cmd_tmp.strip() != '':
                        self.enter = True
                elif data.encode() == b'\x07':  # 响铃
                    pass
                elif data == '\t' or data.encode() == b'\x1b':    # \x1b 点击2下esc键也可以补全
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

    def django_bytes_to_ssh(self, data):
        try:
            self.channel.send(data)
        except:
            logger.error(traceback.format_exc())
            self.close()

    def websocket_to_django(self):
        try:
            while 1:
                if self.zmodemOO:
                    self.zmodemOO = False
                    x = self.channel.recv(2)
                    if not len(x):
                        return
                    if x == b'OO':
                        self.websocker.send(bytes_data=x)
                        continue
                    else:
                        x += self.channel.recv(BufferSize)
                else:
                    x = self.channel.recv(BufferSize)
                    if not len(x):
                        return

                if self.zmodem:
                    if zmodemszend in x or zmodemrzend in x:
                        self.zmodem = False
                        if zmodemszend in x:
                            self.zmodemOO = True
                    if zmodemcancel in x:
                        self.zmodem = False
                        self.channel.send('\n')
                    self.websocker.send(bytes_data=x)
                else:
                    if zmodemszstart in x or zmodemrzstart in x or zmodemrzestart in x or zmodemrzsstart in x \
                            or zmodemrzesstart in x:
                        self.zmodem = True
                        self.websocker.send(bytes_data=x)
                    else:
                        try:
                            data = x.decode('utf-8')
                        except UnicodeDecodeError:  # utf-8中文占3个字符，可能会被截断，需要拼接
                            try:
                                x += self.channel.recv(1)
                                data = x.decode('utf-8')
                            except UnicodeDecodeError:
                                try:
                                    x += self.channel.recv(1)
                                    data = x.decode('utf-8')
                                except UnicodeDecodeError:
                                    logger.error(traceback.format_exc())
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

                        # 指定条结果或者指定秒数或者占用指定内存就保存一次
                        if len(self.res_asciinema) > 2000 or int(time.time() - self.last_save_time) > 60 or \
                                sys.getsizeof(self.res_asciinema) > 20971752:
                            tmp = list(self.res_asciinema)
                            self.res_asciinema = []
                            self.last_save_time = time.time()
                            save_res(self.res_file, tmp)

                        if self.enter:
                            self.enter = False
                            if not data.startswith("\r\n"):   # 回车后结果不以\r\n开头的肯定不是命令
                                self.cmd_tmp = ''
                            else:
                                if re.match(rb'^\r\n\s+\x1b.*$', x):  # 终端为 xterm,linux 等显示颜色类型时在 vi 编辑模式下回车
                                    self.cmd_tmp = ''
                                # elif x == b'\r\n':     # todo 正常模式下 vi 文件会返回 \r\n ,终端为 dumb 类型时在 vi 编辑模式下回车也会返回 \r\n，
                                #     self.cmd_tmp = ''
                                else:   # 记录真正命令, rl 不支持中文命令
                                    cmd_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                                    cmd = self.rl.process_line(self.cmd_tmp.encode("utf-8"))
                                    if cmd is None:     # 有可能 rl 库会返回 None，重试一次
                                        mp_readline.TESTING = True
                                        self.rl = mp_readline.MpReadline()
                                        cmd = self.rl.process_line(self.cmd_tmp.encode("utf-8"))

                                    if cmd:
                                        self.cmd += cmd_time + "\t" + remove_control_chars(cmd) + '\n'
                                    else:
                                        if cmd is None:
                                            logger.error("recv from server: {} \nerror command: {}".format(x, self.cmd_tmp.encode("utf-8")))
                                            self.cmd += cmd_time + "\t" +  remove_control_chars(self.cmd_tmp) + '\n'
                                    self.cmd_tmp = ''
                        else:
                            if self.tab_mode:       # todo 兼容有问题
                                self.tab_mode = False
                                if x == b'\x07':
                                    pass

                                tmp = data.split(' ')
                                # tab 只返回一个命令时匹配
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

                            if self.ctrl_c:     # 取消命令
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
            logger.info(traceback.format_exc())
            self.close()

    def close(self, send_message=True):
        try:
            if send_message:
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
        except Exception:
            # logger.error(traceback.format_exc())
            pass

    def shell(self, data):
        # 原作者使用创建线程的方式发送数据到ssh，每次发送都是一个字符，可以不用线程
        # 直接调用函数性能更好
        # Thread(target=self.django_to_ssh, args=(data,)).start()
        self.django_to_ssh(data)
        # 原作者将发送数据到django websocket的线程创建函数如果写到这，会导致每在客户端输入一个字符就创建一个线程
        # Thread(target=self.websocket_to_django).start()
