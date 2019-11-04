#!/usr/bin/env python

import sys
import time
from urllib import parse
import subprocess


def main():
    tags = ''
    try:
        tags = parse.unquote(sys.argv[1])
        if tags.endswith('/'):  # 当前URL PROTOCOL协议传过来的数据中无 '/' 时，默认会在字符末尾添加一个 '/'，需要去掉
            tags = tags[:-1]
        tags = tags.split('://')
        del tags[0]
        subprocess.Popen('://'.join(tags))  # 如果程序调用参数中有 :// 时
    except Exception:
        print('调用客户端错误，请检查程序路径或者参数是否正确')
        print('://'.join(tags))
        time.sleep(60)
    
    
if __name__ == '__main__':
    main()
