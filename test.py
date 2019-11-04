#!/usr/bin/env python
import os
import sys
import datetime
import time
import re
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from cryptography.fernet import Fernet


def main():
    # 使用django配置文件进行设置
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')
    
    # 让django初始化
    import django
    django.setup()
    
    from django.core.cache import cache
    cache.set('test_123', ['x', 'y'], 600)
    print(cache.get('test_123'))
    print(type(cache.get('test_123')))
    
    cache.delete('leffss')


def convert_byte(byte):
    byte = int(byte)
    if byte <= 1024:
        return '{} B'.format(byte)
    elif 1024 < byte <= 1048576:
        return '{} KB'.format('%.2f' % (byte / 1024))
    elif 1048576 < byte <= 1073741824:
        return '{} MB'.format('%.2f' % (byte / 1024 / 1024))
    elif 1073741824 < byte <= 1099511627776:
        return '{} GB'.format('%.2f' % (byte / 1024 / 1024 / 1024))
    elif byte > 1099511627776:
        return '{} TB'.format('%.2f' % (byte / 1024 / 1024 / 1024 / 1024))


class Prpcrypt:
    def __init__(self, _key):
        self.key = _key
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, _text):
        cryptor = AES.new(self.key, self.mode, self.key)
        # 这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        # length = 16
        length = len(self.key)
        count = len(_text)
        add = length - (count % length)
        _text = _text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(_text)
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext).decode()

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, _text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(_text))
        return plain_text.decode().rstrip('\0')


if __name__ == '__main__':
    # main()
    # x = b'\xe8\xb5'
    # print(x.decode('utf-8'))
    # y = '知'
    # print(y.encode('utf-8'))
    # print(y.encode('gbk'))
    #
    # a = 'xxxx'
    # print(a[0:2])
    # print(a[100:])

    # msg = format('PLAY_{}'.format('xx'), '*<50')
    # print(msg)
    #
    # msg = format('xx_{}'.format('yyy'), '*<50')
    # print(msg)
    #
    # a = {'hosts': '5,4,3,2,1', 'dst': '', 'backup': True, 'src': '/devops/media/tmp/hello.yml'}
    # if 'hosts' not in a:
    #     print('hosts not in')

    # a = 2588262400
    a = 1048576
    print(convert_byte(a))

    x = r'^[\S\s]*?(?P<ansible>[\S\s]?(vars|hostvars|ansible_ssh_pass|ansible_ssh_private_key_file|ansible_become_pass|ansible_pass|ansible_sudo_pass|ansible_su_pass|vault_password)[\S\s]?)[\S\s]*$'
    b = 'a=vars;'
    pattern = re.compile(x, re.I)
    res = pattern.search(b)
    print(res)
    if res:
        info = res.groupdict()
        print(info)
        info = info['ansible'].replace('=', '').replace('{', '').replace('}', '').strip()
        print(info)
    print('end')

    a = 'xasdas}'
    print(a[:-1])

    # _key = 'Liff@2019_______'       # 解密配置文件中加密过的密码的密钥，重要
    _key = 'Liff@2019_______'
    _de = Prpcrypt(_key)
    print(_de.decrypt('d2f044591d6291d895cc8acac93f62f2db8fd30e48ee6b2060bda2f74f16f514'))

    a = 'xxsadasdasd'
    print(_de.encrypt(a))
    b = '37fbd0f8f39a462e39fef72852061f35'
    print(_de.decrypt(b))

    a = 'WAF@ADmin#Sql$719'
    print(_de.encrypt(a))


    # 使用django配置文件进行设置
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devops.settings')
    # 让django初始化
    import django
    django.setup()
    from util.crypto import encrypt, decrypt
    passwd = '1213'
    en = encrypt(passwd)
    print(en)
    print(decrypt(en))

    x = 'gAAAAABduSzufr3De6SKUdjF44QSU8khLWO1V2n7et1if5pYjUsJ6hxn30sYlXEfiP-JWt5ADjtrx6vI_tE7ZNCwniBX0xWSjQ=='
    print(decrypt(x))


    x = 'gAAAAABduSzujDu0XLd0sy1FvNgd2Ttf9id_YKTG4P2XySMxRM9CFk6qOiAKEnMY1PMByervIGUoDVcK1HuxYIOHYOWU7T115w=='
    print(decrypt(x))

    hosts = {
        'k8s1': '192.168.223.111',
        'k8s2': '192.168.223.111',
        'k8s3': '192.168.223.111',
        'k8s4': '192.168.223.111',
        'k8s5': '192.168.223.111',
        'k8s6': '192.168.223.111',
        'k8s7': '192.168.223.111',
        'k8s8': '192.168.223.111',
    }
    for k, v in hosts.items():
        print('已创建远程主机：{}_{}'.format(k, v))

    home_path = '/root'
    remote_path = home_path if home_path else '/tmp'
    print(remote_path)
