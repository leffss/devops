from threading import Thread
from django.conf import settings
from asgiref.sync import async_to_sync
import time
import traceback
from util.tool import gen_rand_char
import platform
from guacamole.client import GuacamoleClient
import os
from webssh.tasks import celery_save_res_asciinema


class Client:
    def __init__(self, websocker):
        self.websocker = websocker
        self.start_time = time.time()
        self.last_save_time = self.start_time
        self.res_file = 'webguacamole_' + str(int(self.start_time)) + '_' + gen_rand_char(16) + '.txt'
        self.res = []
        self.guacamoleclient = None

    def connect(self, protocol, hostname, port, username, password, width, height, dpi):
        try:
            self.guacamoleclient = GuacamoleClient(
                settings.GUACD.get('host'),
                settings.GUACD.get('port'),
                settings.GUACD.get('timeout'),
            )
            if protocol == 'vnc':  # vnc 登陆不需要账号
                self.guacamoleclient.handshake(
                    protocol=protocol,
                    hostname=hostname,
                    port=port,
                    password=password,
                    width=width,
                    height=height,
                    dpi=dpi,
                )
            elif protocol == 'rdp':
                self.guacamoleclient.handshake(
                    protocol=protocol,
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    width=width,
                    height=height,
                    dpi=dpi,
                )
            Thread(target=self.websocket_to_django).start()
        except Exception:
            self.websocker.close(3001)

    def django_to_guacd(self, data):
        try:
            self.guacamoleclient.send(data)
        except Exception:
            self.close()

    def websocket_to_django(self):
        try:
            while True:
                time.sleep(0.001)
                data = self.guacamoleclient.receive()
                if not data:
                    return
                if self.websocker.send_flag == 0:
                    self.websocker.send(data)
                elif self.websocker.send_flag == 1:
                    async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                        "type": "group.message",
                        "text": data,
                    })
                self.res.append(data)
                # 指定条结果或者指定秒数就保存一次
                if len(self.res) > 1000 or int(time.time() - self.last_save_time) > 50:
                    tmp = list(self.res)
                    self.res = []
                    self.last_save_time = time.time()
                    # windows无法正常支持celery任务
                    if platform.system().lower() == 'linux':
                        celery_save_res_asciinema.delay(settings.MEDIA_ROOT + '/' + self.res_file, tmp, False)
                    else:
                        with open(settings.MEDIA_ROOT + '/' + self.res_file, 'a+') as f:
                            for line in tmp:
                                f.write('{}'.format(line))
        except Exception:
            if self.websocker.send_flag == 0:
                self.websocker.send('0.;')
            elif self.websocker.send_flag == 1:
                async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                    "type": "group.message",
                    "text": '0.;',
                })
        finally:
            self.close()

    def close(self):
        self.websocker.close()
        self.guacamoleclient.close()

    def shell(self, data):
        self.django_to_guacd(data)

