#!/usr/bin/env python3

"""Test cases for mp_readline"""
from . import mp_readline
import unittest


class ReadLineTest(unittest.TestCase):

    def setUp(self):
        mp_readline.TESTING = True
        self.rl = mp_readline.MpReadline()

    def test_strings(self):
        tests = (
            ('test', 'test'),
            ('abc', 'abc'),
            # Backspace as 0x7f
            ('\x7f', ''),
            ('a\x7f', ''),
            ('ab\x7f', 'a'),
            ('ab\x7fc', 'ac'),
            # Backspace as 0x08
            ('\x08', ''),
            ('a\x08', ''),
            ('ab\x08', 'a'),
            ('ab\x08c', 'ac'),
            # Home as Control-A
            ('abc\x01d', 'dabc'),
            # Home as ESC [ 1 ~
            ('abc\x1b[1~d', 'dabc'),
            # Home as ESC [ 7 ~
            ('abc\x1b[7~d', 'dabc'),
            # Home as ESC O H
            ('abc\x1bOHd', 'dabc'),
            # End as Control-E
            ('abcd\x01e\x05f', 'eabcdf'),
            # End as ESC [ 4 ~
            ('abcd\x01e\x1b[4~f', 'eabcdf'),
            # End as ESC [ 8 ~
            ('abcd\x01e\x1b[8~f', 'eabcdf'),
            # End as ESC O F
            ('abcd\x01e\x1bOFf', 'eabcdf'),
            # Delete as ESC [ 3 ~
            ('abc\x1b[D\x1b[D\x1b[3~', 'ac'),
            # Delete as Control-D
            ('abc\x1b[D\x1b[D\x04', 'ac'),
            # Left Arrow
            ('def\x1b[D\x1b[Da', 'daef'),
            # Right Arrow
            ('def\x1b[D\x1b[Da\x1b[Cg', 'daegf'),
            # Up Arrow
            # Down Arrow
            # Overwrite/Insert mode
            ('abcdefghi\x1b[7~\x1b[C\x1b[C\x1b[C\x1b[2~jkl\x1b[2~mno', 'abcjklmnoghi'),

            ('ls\x08\x08\x1b[5@asdasda\x1b[C\x1b[C\x1b[C', 'asdasda -l'),
        )
        for rl_input, expected_result in tests:
            rl_input = bytes(rl_input, encoding='utf-8')
            self.assertEqual(self.rl.process_line(rl_input), expected_result)
            print("ori: {} rl: {} expect: {}".format(rl_input, self.rl.process_line(rl_input), expected_result))


if __name__ == "__main__":
    x = b'ls -l\x08\x08\x08\x08\x08\x1b[5@asdasda\x1b[C\x1b[C\x1b[C'
    unittest.main()
