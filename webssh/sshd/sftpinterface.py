#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import os
import paramiko
from .sshinterface import transport_keepalive
import traceback
import threading
import time
import warnings
warnings.filterwarnings("ignore")
paramiko.util.log_to_file('./paramiko.log')
from util.tool import gen_rand_char, terminal_log
# ssh_client ===>>          proxy_ssh             ==>> ssh_server
# ssh_client ===>> (proxy_server -> proxy_client) ==>> ssh_server


class SFTPInterface(paramiko.SFTPServerInterface):
    def __init__(self, proxy_ssh, *largs, **kwargs):
        self.sftp_closed = False
        self.char = gen_rand_char(16)
        super(SFTPInterface, self).__init__(proxy_ssh, *largs, **kwargs)
        self.client, self.transport = self.get_sftp_proxy_client(proxy_ssh.ssh_args)
        transport_keepalive(self.transport)
        self.root_path = proxy_ssh.root_path if ('root_path' in proxy_ssh.__dict__) else ''
        self.cmd = ''
        self.proxy_ssh = proxy_ssh

        try:
            self._client = self.proxy_ssh.chan_cli.transport.remote_version
        except:
            self._client = 'clissh'
        try:
            self.client_addr = self.proxy_ssh.chan_cli.transport.sock.getpeername()[0]
        except:
            self.client_addr = '1.0.0.0'

        t = threading.Thread(target=self.check_backend)
        t.daemon = True
        t.start()

    def get_sftp_proxy_client(self, ssh_args):
        host = ssh_args[0]
        port = ssh_args[1]
        username = ssh_args[2]
        password = ssh_args[3]
        t = paramiko.Transport((host, port))
        t.use_compression()  # 开启压缩
        t.connect(
            username=username,
            password=password,
            # gss_host=host,
        )
        # 设置 window_size 稍微提高下载速度 5MB/s --> 13MB/s
        ssh_proxy_client = paramiko.SFTPClient.from_transport(t, window_size=2 ** 32 - 1)
        # ssh_proxy_client = paramiko.SFTPClient.from_transport(t)
        return ssh_proxy_client, t

    def check_backend(self, sleep_time=5):  # 检测后端sftp服务器是否已断开连接
        try:
            while 1:
                if self.sftp_closed:
                    break
                try:
                    self.transport.getpeername()
                except:
                    self.session_ended()
                    break
                time.sleep(sleep_time)  # 每次循环暂停一定时间，以免对 redis 造成压力
        except:
            pass

    def session_ended(self):
        try:
            if self.cmd:
                terminal_log(
                    self.proxy_ssh.http_user,
                    self.proxy_ssh.hostname,
                    self.proxy_ssh.ssh_args[0],
                    'sftp',
                    self.proxy_ssh.ssh_args[1],
                    self.proxy_ssh.ssh_args[2],
                    self.cmd,
                    # self.res_file,
                    'nothing',
                    self.client_addr,    # 客户端 ip
                    self._client,
                    self.proxy_ssh.log_start_time,
                )
                self.cmd = ''
        except:
            pass
        try:
            self.proxy_ssh.chan_cli.transport.close()
        except:
            pass
        try:
            print('SFTP断开: %s@%s' % (self.transport.get_username(), self.transport.getpeername()[0]))
            super(SFTPInterface, self).session_ended()
            self.client.close()
            self.transport.close()
        except:
            pass
        finally:
            if not self.sftp_closed:
                self.sftp_closed = True

    def _parsePath(self, path):
        if not self.root_path:
            return path
        # Prevent security violation when root_path provided
        result = os.path.normpath(self.root_path + '/' + path)
        if not result.startswith(self.root_path):
            raise IOError(errno.EACCES)
        return result

    def list_folder(self, path):
        try:
            filelist = self.client.listdir_attr(self._parsePath(path))
            # import ipdb; ipdb.set_trace()
            # for fileattr in filelist:
            #     # Paramiko SFTP生成的用户/组是ID数值，改为字符
            #     attrs = [s for s in fileattr.longname.split(' ') if s]
            #     if len(attrs) > 6:
            #         pass
            #         fileattr.st_uid = attrs[2]
            #         fileattr.st_gid = attrs[3]
            return filelist
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def stat(self, path):
        try:
            return self.client.stat(self._parsePath(path))
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def lstat(self, path):
        try:
            return self.client.lstat(self._parsePath(path))
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def open(self, path, flags, attr):
        if flags == 769:
            self.cmd += '上传 {0}\n'.format(path)
        elif flags == 0:
            self.cmd += '下载 {0}\n'.format(path)
        else:
            self.cmd += '打开文件 {1} {0}\n'.format(path, flags)
        try:
            if (flags & os.O_CREAT) and (attr is not None):
                attr._flags &= ~attr.FLAG_PERMISSIONS
                paramiko.SFTPServer.set_file_attr(self._parsePath(path), attr)

            if flags & os.O_WRONLY:
                if flags & os.O_APPEND:
                    fstr = 'ab'
                else:
                    fstr = 'wb'
            elif flags & os.O_RDWR:
                if flags & os.O_APPEND:
                    fstr = 'a+b'
                else:
                    fstr = 'r+b'
            else:
                # O_RDONLY (== 0)
                fstr = 'rb'

            f = self.client.open(self._parsePath(path), fstr)

            fobj = paramiko.SFTPHandle(flags)
            fobj.filename = self._parsePath(path)
            fobj.readfile = f
            fobj.writefile = f
            fobj.client = self.client
            return fobj

            # TODO: verify (socket.error when stopping file upload/download)
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)

    def remove(self, path):
        self.cmd += '删除文件 {0}\n'.format(path)
        try:
            self.client.remove(self._parsePath(path))
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def rename(self, oldpath, newpath):
        self.cmd += '重命名/移动 {0} --> {1}\n'.format(oldpath, newpath)
        try:
            self.client.rename(self._parsePath(oldpath), self._parsePath(newpath))
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def mkdir(self, path, attr):
        self.cmd += '创建文件夹 {0}\n'.format(path)
        try:
            if attr.st_mode is None:
                self.client.mkdir(self._parsePath(path))
            else:
                self.client.mkdir(self._parsePath(path), attr.st_mode)
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def rmdir(self, path):
        self.cmd += '删除文件夹 {0}\n'.format(path)
        try:
            self.client.rmdir(self._parsePath(path))
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def chattr(self, path, attr):
        self.cmd += '权限变更 {0} {1}\n'.format(path, attr)
        try:
            if attr._flags & attr.FLAG_PERMISSIONS:
                self.client.chmod(self._parsePath(path), attr.st_mode)
            if attr._flags & attr.FLAG_UIDGID:
                self.client.chown(self._parsePath(path), attr.st_uid, attr.st_gid)
            if attr._flags & attr.FLAG_AMTIME:
                self.client.utime(self._parsePath(path), (attr.st_atime, attr.st_mtime))
            if attr._flags & attr.FLAG_SIZE:
                with self.client.open(self._parsePath(path), 'w+') as f:
                    f.truncate(attr.st_size)
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def symlink(self, target_path, path):
        return paramiko.SFTP_OP_UNSUPPORTED

    def readlink(self, path):
        try:
            return self.client.readlink(self._parsePath(path))
        except:
            return paramiko.SFTP_OP_UNSUPPORTED
