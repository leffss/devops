# coding=utf-8
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from webssh.sshd.sshd import SSHServer


class Command(BaseCommand):
    # 生成SSH服务端，用于透明代理SSH
    help = u'生成SSH透明代理服务器，类似堡垒机功能，使网站支持CRT,Xshell等SSH终端'

    # def add_arguments(self, parser):
    #     parser.add_argument('port', nargs='?', default='2222', type=int,
    #                         help=u'''
    #                         SSH监听端口，默认为2222
    #                         ''')

    def handle(self, *args, **options):
        host = settings.PROXY_SSHD.get('listen_host', '0.0.0.0')
        port = settings.PROXY_SSHD.get('listen_port', 2222)
        cons = settings.PROXY_SSHD.get('cons', 250)
        ssh_server = SSHServer(host, port, cons)
        ssh_server.run()

