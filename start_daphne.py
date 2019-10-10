#!/usr/bin/env python
""" 初始化创建 admin 账号"""
import subprocess


def __external_cmd(cmd, code="utf8"):
    print(cmd)
    process = subprocess.Popen(cmd, shell=True, bufsize=0, stdout=subprocess.PIPE, universal_newlines=True)
    while True:
        next_line = process.stdout.readline()
        print(next_line.strip())
        if next_line == "" and process.poll() is not None:
            break


if __name__ == '__main__':
    listen = '127.0.0.1'
    port = 8000
    __external_cmd('/home/python372/bin/daphne -b {} -p {} devops.asgi:application'.format(listen, port))

