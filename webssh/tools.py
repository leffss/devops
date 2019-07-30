#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : HuYuan
# @File    : tools.py

import time
import random
import hashlib

def get_key_obj(pkeyobj, pkey_file=None, pkey_obj=None, password=None):
    if pkey_file:
        with open(pkey_file) as fo:
            try:
                pkey = pkeyobj.from_private_key(fo, password=password)
                return pkey
            except:
                pass
    else:
        try:
            pkey = pkeyobj.from_private_key(pkey_obj, password=password)
            return pkey
        except:
            pkey_obj.seek(0)

def unique():
    ctime = str(time.time())
    salt = str(random.random())
    m = hashlib.md5(bytes(salt, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()