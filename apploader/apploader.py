#!/usr/bin/env python

import sys
import traceback
import time
from urllib import parse
import subprocess


def main():
    try:
        tags = parse.unquote(sys.argv[1])
        if tags.endswith('/'):  # 当前URL PROTOCOL协议传过来的数据中无 '/' 时，默认会在字符末尾添加一个 '/'，需要去掉
            tags = tags[:-1]
        # print(tags)
        tags = tags.split('://')
        del tags[0]
        # print(tags)
        subprocess.Popen('://'.join(tags))
        # time.sleep(20)
    except:
        print(traceback.format_exc())
        time.sleep(20)
    

if __name__ == '__main__':
    main()
