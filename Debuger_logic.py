# -*- coding: utf-8 -*-
# @Time    : 2021/4/2 22:23
# @Author  : Zeeland
# @File    : FunEdit.py
# @Software: PyCharm

from PyQt5.QtWidgets import QFileDialog
import os
import argparse
import serial
__version__ = "0.1"
def gethex(self):
    # 从C盘打开文件格式（*.jpg *.gif *.png *.jpeg）文件，返回路径
    hexfile_dir, _ = QFileDialog.getOpenFileName(None, 'Open file', 'C:\\', 'hex files (*.hex)')
    # print(hexfile_dir)
    if hexfile_dir == None:
        print("> > > Successful: File '{}' is not found".format(hexfile_dir))
    else:
        print("Successful: File '{}' is open".format(hexfile_dir))
    return hexfile_dir

def upload51(filename, port):
    try:
        # check if hex-file exits(prevents FileNotFoundError)
        if not os.path.isfile(filename):
            print("> > > ERROR: File '{}' not found".format(filename))
            exit(1)

        # count tries to cancel upload if board is not resetted
        i = 0

        # open file
        with open(filename, mode="r") as file:

            # open serial port
            with serial.Serial(
                    port, 9600,
                    timeout=1,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE
            ) as board:

                # wait for reset
                print("> Connectiong to MPT2-Labbord...")
                while i < 10:
                    i += 1
                    board.write("\x03".encode("utf-8"))
                    s = board.read_until(expected="#".encode("utf-8")).decode("utf-8")
                    if len(s) > 0 and s[-1] == "#":
                        break
                else:
                    raise Exception("Could not connect to MPT2-Labboard. Please reset and try again.")

                # Ignorierte Befehle, da Wirkung nicht bekannt:
                # schicke "F\r"
                # schicke "\r"
                # schicke "\r"

                # upload file
                print("> Uploading...")
                for line in file:
                    board.write("{}\r".format(line.strip()).encode("utf-8"))
                    s = board.read_until(expected="#".encode("utf-8")).decode("utf--8")
                    if len(s) == 0 or s[-1] != "#":
                        raise Exception("Could not upload file. Please reset and and try again.")

                # clearing breakpoints
                print("> Clearing breakpoints...")
                board.write("BK ALL\r".encode("utf-8"))
                s = board.read_until(expected="#".encode("utf-8")).decode("utf-8")
                if len(s) == 0 or s[-1] != "#":
                    raise Exception("Could not upload file. Please reset and try again.")

                # excuting program
                print("> Starting...")
                board.write("G 8000\r".encode("utf-8"))
                s = board.read_until(expected="#".encode("utf-8")).decode("utf-8")
                if len(s) == 0 or s[-1] != "#":
                    raise Exception("Could not start program. Please reset and try again.")
                board.write("G\r".encode("utf-8"))

    # handle all other exceptions:
    except Exception as e:
        print("> > > ERROR: {}".format (e))
        exit(1)

    '''主方法运行入口'''

if __name__ == "__main__":
    # define command line options
    cli = argparse.ArgumentParser(
        description="Tool to upload an intel-hex-formatted code-file to the MPT2-Labboard"
    )

    # option -- version (-v): shows version of upload tool
    cli.add_argument(
        "-v", "--version",
        action="version", version="%(prog)s " + __version__
    )

    # option file: hex-file that should be uploaded
    cli.add_argument(
        "file",
        help="path to a file in intel-hex format",
        type=str
    )

    # option --port (-p): COM-port to use
    cli.add_argument(
        "-p", "--port",
        help="COM-port of the MPT2-Labboard (Default: COM1)",
        type=str, default="COM1"
    )

    # parse command line options
    args = cli.parse_args()

    # start upload
    upload51(args.file, args.port)

