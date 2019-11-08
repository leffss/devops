# -*- coding: utf-8 -*-
import logging
import paramiko
from paramiko.common import WARNING
import traceback
import warnings
warnings.filterwarnings("ignore")
paramiko.util.log_to_file('./paramiko.log', level=WARNING)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SFTP:
    def __init__(self, host, port, username, password=None, key_file=None):
        self.username = username
        self.transport = paramiko.Transport((host, port))

        if key_file:
            private_key = paramiko.RSAKey.from_private_key_file(key_file)
            self.transport.connect(username=self.username, pkey=private_key)
        else:
            self.transport.connect(username=self.username, password=password)

        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = self.transport

    def put_file(self, local_file, user_home):
        """
        user_home指用户的家目录，比如：/home/zz，主要用于获取用户的uid和gid
        :param local_file: 本地文件的路径
        :param user_home: 远程服务器登录用户的家目录，路径最后没有"/"
        """
        try:
            filename = local_file.split('/')[-1]
            remote_file = '{}/{}'.format(user_home, filename)
            self.sftp.put(local_file, remote_file)
            file_stat = self.sftp.stat(user_home)
            self.sftp.chown(remote_file, file_stat.st_uid, file_stat.st_gid)
        except Exception:
            print(traceback.format_exc())
        finally:
            self.transport.close()

    def get_file(self, remote_file, local_file):
        try:
            self.sftp.get(remote_file, local_file)
        except FileNotFoundError:
            print('下载错误，远程主机无此文件: {}'.format(remote_file))
        except Exception:
            print(traceback.format_exc())
        finally:
            self.transport.close()

    def download_file(self, download_file, local_file):
        try:
            self.get_file(download_file, local_file)
            return True
        except Exception:
            print(traceback.format_exc())
            return False

    def upload_file(self, file_name, upload_file_path):
        try:
            stdin, stdout, stderr = self.ssh.exec_command('echo $HOME')
            home_path = stdout.read().decode().strip()
            remote_path = home_path if home_path else '/tmp'
            local_file = '{}/{}'.format(upload_file_path, file_name)
            self.put_file(local_file, remote_path)
            return True, remote_path
        except Exception:
            print(traceback.format_exc())
            return False, None
