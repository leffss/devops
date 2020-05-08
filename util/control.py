import re


# 去除字符中不可见的控制字符
def remove_control_chars(s):
    ctl_list = list(range(0, 32)) + list(range(127, 160))
    # 排除 \n 10 与 \r 13
    ctl_list.remove(10)
    ctl_list.remove(13)
    control_chars = ''.join(map(chr, ctl_list))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
    return control_char_re.sub('', s)
