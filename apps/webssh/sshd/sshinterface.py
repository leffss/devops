#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import socket
import paramiko
from paramiko.common import WARNING
import selectors2 as selectors  # 基于 select 封装的多路复用 IO 库
import time
import json
from django.core.cache import cache
import django.utils.timezone as timezone
from server.models import RemoteUserBindHost
from webssh.models import TerminalSession
from user.models import Permission
from django.db.models import Q
from util.tool import gen_rand_char, terminal_log, res
from util.crypto import decrypt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
import traceback
from util.control import remove_control_chars
from mp_readline import mp_readline
import re
import sys
import os
import logging
import warnings
warnings.filterwarnings("ignore")
paramiko.util.log_to_file('./paramiko.log', level=WARNING)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# ssh_client ===>>          proxy_ssh             ==>> ssh_server
# ssh_client ===>> (proxy_server -> proxy_client) ==>> ssh_server

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

support_term = ["linux", "ansi", "xterm"]

BufferSize = 4096   # 4096 足够，高于 4096 时使用 zmodem 传输时会出现错误


def transport_keepalive(transport):
    # 对后端transport每隔x秒发送空数据以保持连接
    # send_keepalive = CliSSH.get('send_keepalive', 0)
    send_keepalive = 15
    transport.set_keepalive(send_keepalive)


class ServerInterface(paramiko.ServerInterface):
    # proxy_ssh = (proxy_server + proxy_client)
    def __init__(self):
        self.event = threading.Event()
        self.tty_args = ['xterm', 80, 40]  # 终端参数(终端, 长, 宽)
        # self.ssh_args = None  # ssh连接参数
        self.ssh_args = None
        self.type = None
        self.http_user = None  # 终端日志 -- http用户
        self.hostname = None        # 后端主机名称
        self.password = None
        self.hostid = None  # 终端日志 -- hostid
        self.closed = False
        self.chan_cli = None
        self.client = None
        self.client_addr = None
        self.group = 'session_' + gen_rand_char()
        self.cmd = ''       # 多行命令
        self.cmd_tmp = ''   # 一行命令
        self.start_time = time.time()
        tmp_date1 = time.strftime("%Y-%m-%d", time.localtime(int(self.start_time)))
        tmp_date2 = time.strftime("%Y%m%d%H%M%S", time.localtime(int(self.start_time)))
        if not os.path.isdir(os.path.join(settings.RECORD_ROOT, tmp_date1)):
            os.makedirs(os.path.join(settings.RECORD_ROOT, tmp_date1))
        self.res_file = settings.RECORD_DIR + '/' + tmp_date1 + '/' + 'clissh_' + \
                        tmp_date2 + '_' + gen_rand_char(16) + '.txt'
        self.log_start_time = timezone.now()
        self.last_save_time = self.start_time
        self.res_asciinema = []
        self.width = 80
        self.height = 40
        self.user_role = False      # False 普通用户  True 管理员
        self.superusername = None
        self.superpassword = None
        self.lock = False  # 锁定会话
        self.zmodem = False
        mp_readline.TESTING = True
        self.rl = mp_readline.MpReadline()
        self.tab_mode = False   # 使用tab命令补全时需要读取返回数据然后添加到当前输入命令后
        self.history_mode = False
        self.enter = False  # 是否输入回车 \r, 为 True 时则根据 ssh 服务端返回的数据判断是否是执行的命令或者是编辑文本
        self.ctrl_z = False
        self.ctrl_c = False

    def close_ssh_self(self, sleep_time=3):
        try:
            while 1:
                if not cache.get('{}_{}_ssh_session'.format(self.http_user, self.password), False):
                    if not self.closed:
                        try:
                            self.chan_cli.send('\n\r\033[31m当前会话已被管理员关闭\033[0m\r\n')
                        except Exception:
                            logger.error(traceback.format_exc())
                        try:
                            self.close()
                        except Exception:
                            logger.error(traceback.format_exc())
                    try:
                        # 发送数据给查看会话的 websocket 链接
                        message = dict()
                        message['status'] = 2
                        message['message'] = '\n\r\033[31m当前会话已被管理员关闭\033[0m\r\n'
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(self.group, {
                            "type": "chat.message",
                            "text": message,
                        })
                    except Exception:
                        logger.error(traceback.format_exc())
                    break
                self.lock = cache.get('{}_{}_ssh_session_lock'.format(self.http_user, self.password), False)
                time.sleep(sleep_time)  # 每次循环暂停一定时间，以免对 redis 造成压力
        except Exception:
            logger.error(traceback.format_exc())

    def conn_ssh(self):
        # proxy_client ==>> ssh_server
        proxy_client = paramiko.SSHClient()
        proxy_client.load_system_host_keys()
        proxy_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            logger.info("连接后端主机 (%s@%s) ...." % (self.ssh_args[2], self.ssh_args[0]))
            proxy_client.connect(*self.ssh_args)
            self.chan_ser = proxy_client.invoke_shell(*self.tty_args)
            if self.superusername and self.superpassword:     # 登陆后 su 跳转
                if self.user_role and self.http_user == 'admin':
                    self.su_root(self.superusername, self.superpassword)
                    logger.info("后端主机 (%s@%s) 跳转到用户 %s" % (self.ssh_args[2], self.ssh_args[0], self.superusername))
                else:
                    permissions = Permission.objects.filter(
                        Q(user__username=self.http_user) |
                        Q(group__user__username=self.http_user),
                        title='登陆后su跳转超级用户'
                    ).distinct()
                    if permissions:
                        self.su_root(self.superusername, self.superpassword)
                        logger.info("后端主机 (%s@%s) 跳转到用户 %s" % (self.ssh_args[2], self.ssh_args[0], self.superusername))
            logger.info("连接后端主机 (%s@%s) ok" % (self.ssh_args[2], self.ssh_args[0]))

            try:
                self.client = self.chan_cli.transport.remote_version
            except Exception:
                self.client = 'clissh'
            try:
                self.client_addr = self.chan_cli.transport.sock.getpeername()[0]
            except Exception:
                self.client_addr = '1.0.0.0'
            data = {
                'name': '{}_{}_ssh_session'.format(self.http_user, self.password),
                'group': self.group,
                'user': self.http_user,
                'host': self.ssh_args[0],
                'username': self.ssh_args[2],
                'protocol': 1,      # 1 ssh
                'port': self.ssh_args[1],
                'type': 3,      # 3 clissh
                'address': self.client_addr,
                'useragent': self.client,
            }
            TerminalSession.objects.create(**data)

            # 设置连接到redis，使管理员可强制关闭软件终端 会话最大有效时间 30 天
            cache.set('{}_{}_ssh_session'.format(self.http_user, self.password), True, timeout=60 * 60 * 24 * 30)

            t = threading.Thread(target=self.close_ssh_self)
            t.daemon = True
            t.start()

            self.res_asciinema.append(
                json.dumps(
                    {
                        "version": 2,
                        "width": 250,  # 设置足够宽，以便播放时全屏不至于显示错乱
                        "height": 40,
                        "timestamp": int(self.start_time),
                        "env": {"SHELL": "/bin/sh", "TERM": self.tty_args[0]}
                    }
                )
            )
        except Exception:
            logger.error(traceback.format_exc())
            self.close()

    def su_root(self, superuser, superpassword, wait_time=1):
        try:
            su = 'su - {0}\n'.format(superuser)
            self.cmd += su
            self.cmd_tmp = ''
            self.chan_ser.send(su)
            time.sleep(wait_time)
            self.chan_ser.send('{}\n'.format(superpassword))
        except Exception:
            logger.error(traceback.format_exc())
            self.close()

    def bridge(self):
        # 桥接 客户终端 和 代理服务终端 交互
        # transport_keepalive(self.chan_ser.transport)
        sel = selectors.DefaultSelector()  # 根据平台自动选择 IO 模式(kqueue, devpoll, epoll, poll, select)
        sel.register(self.chan_cli, selectors.EVENT_READ)
        sel.register(self.chan_ser, selectors.EVENT_READ)
        try:
            while self.chan_ser and self.chan_cli and not (self.chan_ser.closed or self.chan_cli.closed):
                events = sel.select(timeout=terminal_exipry_time)    # 指定时间无数据输入或者无数据返回则断开连接
                if not events:
                    raise socket.timeout
                for key, n in events:
                    if key.fileobj == self.chan_ser:
                        try:
                            recv_message = self.chan_ser.recv(BufferSize)
                            if self.zmodem:
                                if zmodemszend in recv_message or zmodemrzend in recv_message:
                                    self.zmodem = False
                                    delay = round(time.time() - self.start_time, 6)
                                    self.res_asciinema.append(json.dumps([delay, 'o', '\r\n']))
                                    # logger.info("zmodem end")
                                if zmodemcancel in recv_message:
                                    self.zmodem = False
                                    self.chan_ser.send(b'\n')
                                    # logger.info("zmodem cancel")
                                self.chan_cli.send(recv_message)
                                continue
                            else:
                                if zmodemszstart in recv_message or zmodemrzstart in recv_message or \
                                        zmodemrzestart in recv_message or zmodemrzsstart in recv_message or \
                                        zmodemrzesstart in recv_message:
                                    self.zmodem = True
                                    # logger.info("zmodem start")
                                    self.chan_cli.send(recv_message)
                                    continue

                            if len(recv_message) == 0:
                                self.chan_cli.send("\r\n\033[31m服务端已断开连接....\033[0m\r\n")
                                time.sleep(1)
                                break
                            else:
                                message = dict()
                                message['status'] = 0
                                try:
                                    # 发送数据给查看会话的 websocket 组
                                    message['message'] = recv_message.decode('utf-8')
                                except UnicodeDecodeError:
                                    try:
                                        recv_message += self.chan_ser.recv(1)
                                        message['message'] = recv_message.decode('utf-8')
                                    except UnicodeDecodeError:
                                        try:
                                            recv_message += self.chan_ser.recv(1)
                                            message['message'] = recv_message.decode('utf-8')
                                        except UnicodeDecodeError:
                                            logger.error(traceback.format_exc())
                                            # 拼接2次后还是报错则证明结果是乱码，强制转换
                                            message['message'] = recv_message.decode('utf-8', 'ignore')

                                self.chan_cli.send(recv_message)

                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(self.group, {
                                    "type": "chat.message",
                                    "text": message,
                                })

                                delay = round(time.time() - self.start_time, 6)
                                self.res_asciinema.append(json.dumps([delay, 'o', recv_message.decode('utf-8')]))

                                # 250条结果或者指定秒数就保存一次，这个任务可以优化为使用 celery
                                if len(self.res_asciinema) > 2000 or int(time.time() - self.last_save_time) > 60 \
                                        or sys.getsizeof(self.res_asciinema) > 2097152:
                                    tmp = list(self.res_asciinema)
                                    self.res_asciinema = []
                                    self.last_save_time = time.time()
                                    res(self.res_file, tmp)

                                try:
                                    data = recv_message.decode('utf-8')
                                    if self.enter:
                                        self.enter = False
                                        if not data.startswith("\r\n"):  # 回车后结果不以\r\n开头的肯定不是命令
                                            self.cmd_tmp = ''
                                        else:
                                            if re.match(rb'^\r\n\s+\x1b.*$', recv_message):  # 终端为 xterm,linux 等显示颜色类型时在 vi 编辑模式下回车
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
                                                    logger.error("recv from server: {} \nerror command: {}".format(recv_message, self.cmd_tmp.encode("utf-8")))
                                                    self.cmd += cmd_time + "\t" + remove_control_chars(self.cmd_tmp) + '\n'
                                                self.cmd_tmp = ''
                                    else:
                                        if self.tab_mode:  # todo 兼容有问题
                                            self.tab_mode = False
                                            tmp = data.split(' ')
                                            # tab 只返回一个命令时匹配
                                            # print(tmp)
                                            if len(tmp) == 2 and tmp[1] == '' and tmp[0] != '':
                                                self.cmd_tmp = self.cmd_tmp + tmp[0].encode().replace(b'\x07',
                                                                                                      b'').decode()
                                            elif len(tmp) == 1 and tmp[0].encode() != b'\x07':  # \x07 蜂鸣声
                                                self.cmd_tmp = self.cmd_tmp + tmp[0].encode().replace(b'\x07',
                                                                                                      b'').decode()

                                        # 多次上下箭头查找历史命令返回数据中可能会包含 \x1b[1P 导致 rl 无法解析命令，具体原因没有深究
                                        if self.history_mode:
                                            self.history_mode = False
                                            if recv_message != b'' and recv_message != b'\x07':
                                                recv_message = re.sub(rb'\x1b\[\d+P', b'', recv_message)
                                                self.cmd_tmp += recv_message.decode("utf-8")

                                        if self.ctrl_c:  # 取消命令
                                            self.ctrl_c = False
                                            # if x == b'^C\r\n':
                                            if re.match(rb'^\^C\r\n[\s\S]*$', recv_message) or re.match(rb'^\r\n[\s\S]*$', recv_message):
                                                self.cmd_tmp = ""
                                        if self.ctrl_z:
                                            self.ctrl_z = False
                                            if re.match(rb'^[\s\S]*\[\d+\]\+\s+Stopped\s+\S+[\s\S]*$', recv_message):
                                                self.cmd_tmp = ""
                                except Exception:
                                    logger.error(traceback.format_exc())
                        except socket.timeout:
                            logger.error(traceback.format_exc())
                    if key.fileobj == self.chan_cli:
                        try:
                            send_message = self.chan_cli.recv(BufferSize)
                            if len(send_message) == 0:
                                logger.info('客户端断开了连接 {}....'.format(self.client_addr))
                                # time.sleep(1)
                                break
                            else:
                                if not self.lock:
                                    self.chan_ser.send(send_message)
                                    if not self.zmodem:
                                        try:
                                            data = send_message.decode('utf-8')
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
                                else:
                                    # 红色提示文字
                                    self.chan_cli.send("\r\n\033[31m当前会话已被管理员锁定\033[0m\r\n")
                                    self.check_channel_window_change_request(
                                        self.chan_cli, self.width - 1, self.height, 0, 0
                                    )
                                    self.check_channel_window_change_request(
                                        self.chan_cli, self.width + 1, self.height, 0, 0
                                    )

                        except socket.timeout:
                            logger.error(traceback.format_exc())
                        except Exception:
                            logger.error(traceback.format_exc())
                            break
        except socket.timeout:
            self.chan_cli.send("\r\n\033[31m由于长时间没有操作或者没有数据返回，连接已断开!\033[0m\r\n")
            logger.info("后端主机 (%s@%s) 会话由于长时间没有操作或者没有数据返回，连接断开!" % (self.ssh_args[2], self.ssh_args[0]))
        except Exception:
            logger.error(traceback.format_exc())

    def close(self, terminal_type='ssh'):
        time.sleep(0.5)     # 防止多次停止重复保存数据

        if terminal_type is 'N':    # 重复登陆时可能会调用close，这时不能删除这些 key，否则会把当前正常会话也关闭掉
            self.closed = True
            try:
                # logger.error("密码无效 {} - {}".format(self.http_user, self.password))
                self.chan_cli.transport.close()
            except Exception:
                logger.error(traceback.format_exc())
            return

        if not self.closed:
            logger.info("后端主机 (%s@%s) 会话结束" % (self.ssh_args[2], self.ssh_args[0]))
            self.closed = True
            # 关闭ssh终端，必须分开 try 关闭，否则当强制关闭一方时，另一方连接可能被挂起
            try:
                self.chan_cli.transport.close()
            except Exception:
                logger.error(traceback.format_exc())

            try:
                self.chan_ser.transport.close()
            except Exception:
                logger.error(traceback.format_exc())

            try:
                if self.cmd:
                    terminal_log(
                        self.http_user,
                        self.hostname,
                        self.ssh_args[0],
                        'ssh',
                        self.ssh_args[1],
                        self.ssh_args[2],
                        self.cmd,
                        self.res_file,
                        self.client_addr,    # 客户端 ip
                        self.client,
                        self.log_start_time,
                    )
            except Exception:
                logger.error(traceback.format_exc())

            try:
                if self.cmd:
                    tmp = list(self.res_asciinema)
                    self.res_asciinema = []
                    res(self.res_file, tmp)
            except Exception:
                logger.error(traceback.format_exc())

            try:
                TerminalSession.objects.filter(
                    name='{}_{}_{}_session'.format(self.http_user, self.password, terminal_type)
                ).delete()
            except Exception:
                logger.error(traceback.format_exc())

            try:
                # 发送数据给查看会话的 websocket 链接
                message = dict()
                message['status'] = 1
                message['message'] = '\n\r连接已断开\r\n'
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(self.group, {
                    "type": "chat.message",
                    "text": message,
                })
            except Exception:
                # logger.error(traceback.format_exc())
                pass

            cache.delete('{}_{}_{}_session'.format(self.http_user, self.password, terminal_type))
            cache.delete('{}_{}_{}_session_lock'.format(self.http_user, self.password, terminal_type))

    def set_ssh_args(self, hostid):
        # 准备proxy_client ==>> ssh_server连接参数，用于后续SSH、SFTP
        # remote_host = RemoteUserBindHost.objects.get(id=hostid, enabled=True)
        if self.user_role and self.http_user == 'admin':
            hosts = RemoteUserBindHost.objects.filter(pk=hostid, enabled=True)
        else:
            hosts = RemoteUserBindHost.objects.filter(
                Q(user__username=self.http_user) | Q(group__user__username=self.http_user),
                pk=hostid,
                enabled=True
            ).distinct()
        if not hosts:
            raise Exception("不存在的主机")
        else:
            remote_host = hosts[0]
        self.hostname = remote_host.hostname
        self.superusername = remote_host.remote_user.superusername
        self.superpassword = decrypt(remote_host.remote_user.superpassword)
        host = remote_host.ip
        port = remote_host.port
        user = remote_host.remote_user.username
        passwd = decrypt(remote_host.remote_user.password)
        # self.ssh_args = ('192.168.223.112', 22, 'root', '123456')
        self.ssh_args = (host, port, user, passwd)

    def check_channel_request(self, kind, chanid):
        """
        securecrt 和 xshell 会话克隆功能（包括 securecrt 的 sftp session）会在
        同一个socket连接下（transport）开启多个channel，第一个channel id 为 0 后面 +1 递增
        由于 paramiko 实现的 ssh server 在克隆会话后，被克隆的会话就无法操作了，解决方法还没研究出来，
        所以这里使用 and chanid is 0 禁止克隆会话（开启多个 channel）
        """
        if kind == "session" and chanid is 0:
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, http_user, password):
        # 验证密码
        try:
            self.http_user = http_user
            self.password = password
            return paramiko.AUTH_SUCCESSFUL
        except Exception:
            logger.error(traceback.format_exc())
            return paramiko.AUTH_FAILED

    def check_auth_gssapi_keyex(self, username, gss_authenticated=paramiko.AUTH_FAILED, cc_file=None):
        if gss_authenticated == paramiko.AUTH_SUCCESSFUL:
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def enable_auth_gssapi(self):
        return True

    def get_allowed_auths(self, username):
        # return "gssapi-keyex,gssapi-with-mic,password,publickey"
        return "password"

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(
        self, channel, term, width, height, pixelwidth, pixelheight, modes
    ):
        self.width = width
        self.height = height
        key = 'ssh_%s_%s' % (self.http_user, self.password)
        key_ssh = 'ssh_%s_%s_ssh_count' % (self.http_user, self.password)
        key_sftp = 'ssh_%s_%s_sftp_count' % (self.http_user, self.password)
        try:
            ssh_count = cache.get(key_ssh, 0)
            sftp_count = cache.get(key_sftp, 0)
            if ssh_count > 0:
                # hostid = cache.get(key)
                hostinfo = cache.get(key)
                hostid = hostinfo['host_id']
                self.user_role = hostinfo['issuperuser']
                # cache.set(key_ssh, ssh_count - 1, timeout=60 * 60 * 24)
                cache.decr(key_ssh)   #　值 -1
                if hostid:
                    # cache.delete(key)
                    self.hostid = hostid
                    if not self.ssh_args:
                        self.set_ssh_args(self.hostid)
                if type(term) is bytes:
                    self.tty_args = [term.decode("utf-8").lower(), width, height]
                else:
                    self.tty_args = [term.lower(), width, height]
                # self.tty_args = ['dumb', width, height]
                if self.tty_args[0] not in support_term:
                    self.tty_args[0] = "xterm"
                self.type = 'pty'
            else:
                if ssh_count == 0 and sftp_count == 0:
                    cache.delete(key)
                    cache.delete(key_ssh)
                else:
                    cache.delete(key_ssh)
                    self.close(terminal_type='N')    # 超过随机密码使用次数限制直接断开连接
            return True
        except Exception:
            logger.error(traceback.format_exc())
            self.close(terminal_type='N')

    def check_channel_subsystem_request(self, channel, name):
        # SFTP子系统
        key = 'ssh_%s_%s' % (self.http_user, self.password)
        key_ssh = 'ssh_%s_%s_ssh_count' % (self.http_user, self.password)
        key_sftp = 'ssh_%s_%s_sftp_count' % (self.http_user, self.password)
        try:
            ssh_count = cache.get(key_ssh, 0)
            sftp_count = cache.get(key_sftp, 0)
            if sftp_count > 0:
                # hostid = cache.get(key)
                hostinfo = cache.get(key)
                hostid = hostinfo['host_id']
                self.user_role = hostinfo['issuperuser']
                # cache.set(key_sftp, sftp_count - 1, timeout=60 * 60 * 24)
                cache.decr(key_sftp)  # 值 -1
                if hostid:
                    # cache.delete(key)
                    self.hostid = hostid
                    if not self.ssh_args:
                        self.set_ssh_args(self.hostid)
                self.type = 'subsystem'
                self.event.set()
            else:
                if ssh_count == 0 and sftp_count == 0:
                    cache.delete(key)
                    cache.delete(key_sftp)
                else:
                    cache.delete(key_sftp)
                self.close(terminal_type='N')  # 超过随机密码使用次数限制直接断开连接
            return super(ServerInterface, self).check_channel_subsystem_request(channel, name)
        except Exception:
            logger.error(traceback.format_exc())
            self.close(terminal_type='N')

    def check_channel_window_change_request(self, channel, width, height, pixelwidth, pixelheight):
        try:
            self.chan_ser.resize_pty(width=width, height=height)    # 必须 try 错误，否则在打开 xshell 后关闭，再连接会出错
            self.width = width
            self.height = height
        except Exception:
            logger.error(traceback.format_exc())
            return False
        return True

    def check_channel_direct_tcpip_request(self, chan_id, origin, destination):
        # SSH隧道
        self.type = 'direct-tcpip'
        self.event.set()
        return 0
