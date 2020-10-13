from threading import Thread
from django.conf import settings
from asgiref.sync import async_to_sync
import time
import traceback
from util.tool import gen_rand_char, res
from guacamole.client import GuacamoleClient, PROTOCOLS
from guacamole.exceptions import GuacamoleError
from guacamole.instruction import GuacamoleInstruction as Instruction
import sys
import os
import base64
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 重写 hanshake 方法以支持加入现有连接操作，实现查看会话功能
class MyGuacamoleClient(GuacamoleClient):
    def handshake(self, protocol='vnc', width=1024, height=768, dpi=96,
                  audio=None, video=None, image=None, **kwargs):
        """
        Establish connection with Guacamole guacd server via handshake.
        """
        if protocol not in PROTOCOLS:
            if protocol[0] != '$':
                self.logger.debug('Invalid protocol: %s' % protocol)
                raise GuacamoleError('Cannot start Handshake. Missing protocol.')

        if audio is None:
            audio = list()

        if video is None:
            video = list()

        if image is None:
            image = list()

        # 1. Send 'select' instruction
        self.logger.debug('Send `select` instruction.')
        self.send_instruction(Instruction('select', protocol))

        # 2. Receive `args` instruction
        instruction = self.read_instruction()
        self.logger.debug('Expecting `args` instruction, received: %s'
                          % str(instruction))

        if not instruction:
            self.close()
            raise GuacamoleError(
                'Cannot establish Handshake. Connection Lost!')

        if instruction.opcode != 'args':
            self.close()
            raise GuacamoleError(
                'Cannot establish Handshake. Expected opcode `args`, '
                'received `%s` instead.' % instruction.opcode)

        # 3. Respond with size, audio & video support
        self.logger.debug('Send `size` instruction (%s, %s, %s)'
                          % (width, height, dpi))
        self.send_instruction(Instruction('size', width, height, dpi))

        self.logger.debug('Send `audio` instruction (%s)' % audio)
        self.send_instruction(Instruction('audio', *audio))

        self.logger.debug('Send `video` instruction (%s)' % video)
        self.send_instruction(Instruction('video', *video))

        self.logger.debug('Send `image` instruction (%s)' % image)
        self.send_instruction(Instruction('image', *image))

        # 4. Send `connect` instruction with proper values
        connection_args = [
            kwargs.get(arg.replace('-', '_'), '') for arg in instruction.args
        ]

        self.logger.debug('Send `connect` instruction (%s)' % connection_args)
        self.send_instruction(Instruction('connect', *connection_args))

        # 5. Receive ``ready`` instruction, with client ID.
        instruction = self.read_instruction()
        self.logger.debug('Expecting `ready` instruction, received: %s'
                          % str(instruction))

        if instruction.opcode != 'ready':
            self.logger.warning(
                'Expected `ready` instruction, received: %s instead')

        if instruction.args:
            self._id = instruction.args[0]
            self.logger.debug(
                'Established connection with client id: %s' % self.id)

        self.logger.debug('Handshake completed.')
        self.connected = True


class Client:
    def __init__(self, websocker):
        self.websocker = websocker
        self.start_time = time.time()
        self.last_save_time = self.start_time
        tmp_date1 = time.strftime("%Y-%m-%d", time.localtime(int(self.start_time)))
        tmp_date2 = time.strftime("%Y%m%d%H%M%S", time.localtime(int(self.start_time)))
        if not os.path.isdir(os.path.join(settings.RECORD_ROOT, tmp_date1)):
            os.makedirs(os.path.join(settings.RECORD_ROOT, tmp_date1))
        self.res_file = settings.RECORD_DIR + '/' + tmp_date1 + '/' + 'webguacamole_' + \
                        tmp_date2 + '_' + gen_rand_char(16) + '.txt'
        self.res = []
        self.guacamoleclient = None
        self.file_index = {}
        self.file_cmd = ''

    def connect(self, protocol, hostname, port, username, password, width, height, dpi, **kwargs):
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
                    ignore_cert="true",
                    disable_audio="true",
                    client_name="devops",
                    **kwargs,
                )
            elif protocol == 'rdp':
                if 'security' not in kwargs.keys():
                    kwargs['security'] = 'any'
                self.guacamoleclient.handshake(
                    protocol=protocol,
                    port=port,
                    username=username,
                    password=password,
                    hostname=hostname,
                    width=width,
                    height=height,
                    dpi=dpi,
                    # domain='SWAD.COM',  # 域验证服务器
                    # security='nla',  # rdp,nla,nla-ext,tls,any
                    ignore_cert="true",
                    disable_audio="true",
                    client_name="devops",
                    **kwargs,
                )
            Thread(target=self.websocket_to_django).start()
        except Exception:
            logger.error(traceback.format_exc())
            self.websocker.close(3001)

    def django_to_guacd(self, data):
        try:
            self.guacamoleclient.send(data)
        except Exception:
            self.close()

    def websocket_to_django(self):
        try:
            while 1:
                # time.sleep(0.00001)
                data = self.guacamoleclient.receive()
                if not data:
                    message = str(base64.b64encode('连接被断开或者协议不支持'.encode('utf-8')), 'utf-8')
                    self.websocker.send('6.toastr,1.2,{0}.{1};'.format(len(message), message))
                    break

                save_res = True

                if data.startswith("4.file,"):
                    tmp = data.split(",")
                    file_index = tmp[1].split(".")[1]
                    file_type = tmp[2].split(".")[1]
                    file_name_tmp = tmp[3].rstrip(";").split(".")
                    del file_name_tmp[0]
                    file_name = '.'.join(file_name_tmp)
                    self.file_index[file_index] = [file_name, file_type]
                    message = str(base64.b64encode('开始下载文件 - {}'.format(file_name).encode('utf-8')), 'utf-8')
                    self.websocker.send('6.toastr,1.3,{0}.{1};'.format(len(message), message))
                    save_res = False

                if self.file_index:
                    if data.startswith("4.blob,"):
                        tmp = data.split(",")
                        index = tmp[1].split(".")[1]
                        if index in self.file_index:
                            # lenx = tmp[2].split(".")[0]
                            # logger.info("file: {} len: {}".format(self.file_index[index][0], lenx))
                            save_res = False

                    if data.startswith("3.end,"):
                        tmp = data.split(",")
                        index = tmp[1].rstrip(";").split(".")[1]
                        if index in self.file_index:
                            cmd_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
                            self.file_cmd += cmd_time + "\t" + '下载文件 - {}'.format(self.file_index[index][0]) + '\n'
                            message = str(base64.b64encode('文件下载完成 - {}'.format(self.file_index[index][0]).encode('utf-8')), 'utf-8')
                            self.websocker.send('6.toastr,1.3,{0}.{1};'.format(len(message), message))
                            save_res = False
                            del self.file_index[index]

                if self.websocker.send_flag == 0:
                    self.websocker.send(data)
                elif self.websocker.send_flag == 1:
                    async_to_sync(self.websocker.channel_layer.group_send)(self.websocker.group, {
                        "type": "group.message",
                        "text": data,
                    })

                if save_res:    # 不保存下载文件时的数据到录像
                    self.res.append(data)
                    # 指定条结果或者指定秒数就保存一次
                    if len(self.res) > 2000 or int(time.time() - self.last_save_time) > 60 or \
                            sys.getsizeof(self.res) > 2097152:
                        tmp = list(self.res)
                        self.res = []
                        self.last_save_time = time.time()
                        res(self.res_file, tmp, False)

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
        try:
            self.websocker.close()
            self.guacamoleclient.close()
        except Exception:
            logger.error(traceback.format_exc())

    def shell(self, data):
        self.django_to_guacd(data)


class ClientView:
    def __init__(self, websocker):
        self.websocker = websocker
        self.guacamoleclient = None

    def connect(self, protocol, hostname, port, username, password, width, height, dpi, **kwargs):
        try:
            self.guacamoleclient = MyGuacamoleClient(
                settings.GUACD.get('host'),
                settings.GUACD.get('port'),
                settings.GUACD.get('timeout'),
            )
            self.guacamoleclient.handshake(
                protocol=protocol,
                hostname=hostname,
                port=port,
                username=username,
                password=password,
                width=width,
                height=height,
                dpi=dpi,
                readonly="true",
                **kwargs,
            )
            Thread(target=self.websocket_to_django).start()
        except Exception:
            self.websocker.close(3001)

    def websocket_to_django(self):
        try:
            while 1:
                # time.sleep(0.00001)
                data = self.guacamoleclient.receive()
                if not data:
                    break
                self.websocker.send(data)
        except Exception:
            self.websocker.send('0.;')
        finally:
            self.close()

    def close(self):
        self.websocker.close()
        self.guacamoleclient.close()

    def django_to_guacd(self, data):
        try:
            self.guacamoleclient.send(data)
        except Exception:
            self.close()

    def shell(self, data):
        self.django_to_guacd(data)
