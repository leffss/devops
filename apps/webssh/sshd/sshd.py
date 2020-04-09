# coding=utf-8
import os
import socket
import threading
import paramiko
from paramiko.common import WARNING
from webssh.sshd.sftpinterface import SFTPInterface
from webssh.sshd.sshinterface import ServerInterface
import logging
import warnings
warnings.filterwarnings("ignore")
paramiko.util.log_to_file('./paramiko.log', level=WARNING)
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SSHServer:

    def __init__(self, host, port, cons=100):
        self.listen_host = host
        self.listen_port = port
        self.cons = cons

    @property
    def host_key(self):
        # ssh-keygen -t rsa -P '' -f '/root/.ssh/id_rsa' 快速生成密钥
        host_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ssh_proxy_rsa.key')
        if not os.path.isfile(host_key_path):
            pass
        return paramiko.RSAKey(filename=host_key_path)

    def run(self):
        logger.info('启动 ssh_proxy 服务 @ {}:{}'.format(self.listen_host, self.listen_port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.listen_host, self.listen_port))
        sock.listen(self.cons)

        while 1:
            client, addr = sock.accept()  # 阻塞等待客户端连接
            t = threading.Thread(target=self.handle_connection, args=(client, addr))
            t.daemon = True
            t.start()

    def handle_connection(self, sock, addr):
        transport = paramiko.Transport(sock, gss_kex=False)
        transport.load_server_moduli()

        transport.add_server_key(self.host_key)
        transport.set_subsystem_handler(
            'sftp', paramiko.SFTPServer, SFTPInterface
        )
        logger.info('客户端连接: {}'.format(addr))
        proxy_ssh = ServerInterface()

        transport.start_server(server=proxy_ssh)  # SSH时输密码 或 SFTP时调用子系统开启SFTP

        while transport.is_active():
            chan_cli = transport.accept()
            proxy_ssh.chan_cli = chan_cli
            proxy_ssh.event.wait(10)  # 等待
            if not chan_cli:
                continue

            if not proxy_ssh.event.is_set():
                sock.close()
                return
            else:
                proxy_ssh.event.clear()

            t = threading.Thread(target=self.dispatch, args=(proxy_ssh,))
            t.daemon = True
            t.start()

    @staticmethod
    def dispatch(proxy_ssh):
        # supported = {'pty', 'x11', 'forward-agent'}
        supported = {'pty'}
        chan_type = proxy_ssh.type
        if chan_type in supported:
            proxy_ssh.conn_ssh()  # 连接后端真实SSH服务器
            proxy_ssh.bridge()  # 链接SSH客户端和后端真实SSH服务器，进行数据交换，阻塞函数
            if not proxy_ssh.closed:    # 避免重复记录操作记录
                proxy_ssh.close()
        elif chan_type == 'subsystem':  # sftp 连接
            # SFTP
            pass
        else:
            msg = "Request type `{}` not support now".format(chan_type)
            proxy_ssh.chan_cli.send(msg)


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 2222
    cons = 250  # SSHD 连接数
    ssh_server = SSHServer(host, port, cons=cons)
    ssh_server.run()
