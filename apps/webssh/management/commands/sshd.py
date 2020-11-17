# coding=utf-8
from django.core.management.base import BaseCommand
from django.conf import settings
from webssh.sshd.sshd import SSHServer


class Command(BaseCommand):
    help = '生成 SSH/SFTP 透明代理服务器，用于支持 SecureCRT/xshell/putty/winscp 等 SSH/SFTP 终端'

    # def add_arguments(self, parser):
    #     parser.add_argument('port', nargs='?', default='2222', type=int,
    #                         help='''
    #                         SSH监听端口，默认为2222
    #                         ''')
    #     parser.add_argument(
    #         '-n',
    #         '--name',
    #         action='store',
    #         dest='name',
    #         default='close',
    #         help='name of author.',
    #     )

    def handle(self, *args, **options):
        # if options['name']:
        #     print('hello world, %s' % options['name'])
        host = settings.PROXY_SSHD.get('listen_host', '0.0.0.0')
        port = settings.PROXY_SSHD.get('listen_port', 2222)
        cons = settings.PROXY_SSHD.get('cons', 100)
        ssh_server = SSHServer(host, port, cons)
        ssh_server.run()
