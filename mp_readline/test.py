#!/usr/bin/env python3

"""Test cases for mp_readline"""
import mp_readline

mp_readline.TESTING = True
rl = mp_readline.MpReadline()


if __name__ == "__main__":
    input1 = b'free asd\x08\x08\x08\x08\x08\x08\x08\x08pp\x1b[K\x08\x08free asd\x08\x08\x08\x08\x08\x08\x08\x08pp\x1b[K\x08\x08sk\x08\x08vim xasd\x08\x08\x08\x08\x08\x08\x08\x08\x1b[1Pfree -m'
    input = b'pp\x1b[K\x08\x08pp\x1b[K\x08\x08\x1b[1Pfree -m'
    inputx = b'pp\x1b[K\x08\x08\x1b[1Pfree -m'
    # \x1b[1
    xx = b'free -m\x08\x08\x08\x08\x08\x08\x08\x1b[5Pls -l\x08\x08\x08\x08\x08free -m\x08\x08asd\x08\x08\x08\x08\x08\x08\x08\x08pp\x1b[K'
    yy = 'pp'

    real = 'free -m'
    a = rl.process_line(xx)
    print(a)
    x = 1
    y = 2
    print(x, y)
