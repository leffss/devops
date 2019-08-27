#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import os
import paramiko
from .sshinterface import transport_keepalive
import traceback
import warnings
warnings.filterwarnings("ignore")
paramiko.util.log_to_file('./paramiko.log')
from util.tool import gen_rand_char
# ssh_client ===>>          proxy_ssh             ==>> ssh_server
# ssh_client ===>> (proxy_server -> proxy_client) ==>> ssh_server


class SFTPInterface(paramiko.SFTPServerInterface):
    def __init__(self, proxy_ssh, *largs, **kwargs):
        # print(proxy_ssh, 999999999)
        self.char = gen_rand_char(16)
        super(SFTPInterface, self).__init__(proxy_ssh, *largs, **kwargs)
        # import ipdb; ipdb.set_trace()
        self.client, self.transport = self.get_sftp_proxy_client(proxy_ssh.ssh_args)
        transport_keepalive(self.transport)
        self.root_path = proxy_ssh.root_path if ('root_path' in proxy_ssh.__dict__) else ''

    def get_sftp_proxy_client(self, ssh_args):
        # ssh_args = (ip, port, username, password)
        # proxy_client ==>> sftp_server
        # import ipdb; ipdb.set_trace()
        # print ssh_args, 77777777777777
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
        ssh_proxy_client = paramiko.SFTPClient.from_transport(t)
        return ssh_proxy_client, t

    def session_ended(self):
        # import ipdb; ipdb.set_trace()
        print(self.char)
        print('后端SFTP断开: %s@%s' % (self.transport.get_username(), self.transport.getpeername()[0]))
        super(SFTPInterface, self).session_ended()
        self.client.close()
        self.transport.close()

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
        print('open-----------')
        print(self.char)
        print(path)
        print(flags)
        print(attr)
        print('open-----------')
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
        print('remove-----------')
        print(self.char)
        print(path)
        print('remove-----------')
        try:
            self.client.remove(self._parsePath(path))
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def rename(self, oldpath, newpath):
        print('rename-----------')
        print(self.char)
        print(oldpath)
        print(newpath)
        print('rename-----------')
        try:
            self.client.rename(self._parsePath(oldpath), self._parsePath(newpath))
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def mkdir(self, path, attr):
        print('mkdir-----------')
        print(self.char)
        print(path)
        print(attr)
        print('mkdir-----------')
        try:
            if attr.st_mode is None:
                self.client.mkdir(self._parsePath(path))
            else:
                self.client.mkdir(self._parsePath(path), attr.st_mode)
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def rmdir(self, path):
        print('rmdir-----------')
        print(self.char)
        print(path)
        print('rmdir-----------')
        try:
            self.client.rmdir(self._parsePath(path))
        except IOError as e:
            return paramiko.SFTPServer.convert_errno(e.errno)
        return paramiko.SFTP_OK

    def chattr(self, path, attr):
        print('chattr-----------')
        print(self.char)
        print(path)
        print(attr)
        print('chattr-----------')
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
