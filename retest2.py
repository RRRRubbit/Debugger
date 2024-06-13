#!/data/data/com.termux/files/usr/bin/python
# -*- coding: UTF-8 -*-
'''
__Author__:sbdlhl
功能       :测试Ascii码表
'''


def testAscii():
    print(u'-----------Ascii 字符测试-----------')
    print("", end='	')
    for i in range(32, 127):
        # chr()返回值是当前整数对应的 ASCII 字符
        print("[", i, "]", chr(i), end='	')


def main():
    testAscii()


if __name__ == "__main__":
    main()