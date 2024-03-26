# -*- coding: UTF-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction, QFileDialog
from PyQt5.QtCore import  *
import serial.tools.list_ports
import os
import argparse
import serial
from Gui.ui_MainWindow import *
from Gui.ui_BreakPointDialog import *
from Gui.ui_PortSelect import *
from Logic.BreakPointDialog import  *
from Logic.PortSent import *
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
serial_is_open = False
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sign_one = pyqtSignal(str)

    global hexfile_dir
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)


        self.actionUpdateregister.triggered.connect(self.get_register)
        self.actionOpen.triggered.connect(self.gethex)
        self.actionLoad.triggered.connect(self.upload)
        self.actionStep_Run.triggered.connect(self.set_register)


        def PortSelect_show():
            ps = PortSelectDialog()
            ps.exec()
            #ps.closeEvent()
        def BreakPointDialog_show():
            bk = BreakPointDialog()
            bk.show()
        self.actionMake_BreakPoint.triggered.connect(BreakPointDialog_show)
        self.actionList_Port.triggered.connect(PortSelect_show)
    def gethex(self):
        # From disk open file format（*.hex），return dir
        global hexfile_dir
        s, _=QFileDialog.getOpenFileName(None, 'Open a hex file', 'C:\\', 'hex files (*.hex)')
        hexfile_dir = s
        #print(hexfile_dir)
        if hexfile_dir==None:
             print("> > > Successful: File '{}' is not found".format(hexfile_dir))
        else:
            print("Successful: File '{}' is open".format(hexfile_dir))
        return hexfile_dir


    # upload hex-file to labborad
    def upload(self):
        global hexfile_dir
        s = hexfile_dir
        print(s)
        PortSent.upload51(s)
        return hexfile_dir

    def get_register(self):
            PortSent().send("X\r".encode("utf-8"))

            s = PortSent().receive()
            #s = "RA RB R0 R1 R2 R3 R4 R5 R6 R7 PSW DPTR SP PC<\r><\n>FF FF FF FF FF FF FF FF FF FF ---R0--- 0000 07 0000 <\r><\n>"

            if len(s) == 0 or s[-1] != "#":
                raise Exception("Could not get all register. Please reset and try again.")
            else:
                self.set_register(self.s)

        #def register_value= a
        #return register_value


    def make_breakpoint(self):
        BreakPointDialog.show()
        with serial.Serial(
                port, 9600,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
        ) as board:
            print("> Starting make breakpoint... ")
            board.write("X\r".encode("utf-8"))
            s = board.read_until(expected="#".encode("utf-8")).decode("utf-8")
            if len(s) == 0 or s[-1] != "#":
                raise Exception("Could not make breakpoint. Please reset and try again.")

    def set_register(self,message):
        s=massage
        s.replace('\r', '')
        self.label.setText(s)
    def set_RAM(self):

        port = PortSelectDialog.openport()
        #board = serial.Serial(port=port, 9600,timeout=1,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE)

        s =('C:0000: 02 00 03 75 E8 FE 78 14 - 11 13 D8 FC E5 E8 23 F5 <\r><\n>'
            'C:0010: 02 00 03 75 E8 FE 78 14 - 11 13 D8 FC E5 E8 23 F5 <\r><\n>'
            'C:0020: 02 00 03 75 E8 FE 78 14 - 11 13 D8 FC E5 E8 23 F5 <\r><\n>'
            'C:0030: 02 00 03 75 E8 FE 78 14 - 11 13 D8 FC E5 E8 23 F5 <\r><\n>'
            'C:0040: 02 00 03 75 E8 FE 78 14 - 11 13 D8 FC E5 E8 23 F5 <\r><\n>'
            'C:0050: 02 00 03 75 E8 FE 78 14 - 11 13 D8 FC E5 E8 23 F5 <\r><\n>'
            'C:0060: 02 00 03 75 E8 FE 78 14 - 11 13 D8 FC E5 E8 23 F5 <\r><\n>'
            'C:0070: 02 00 03 75 E8 FE 78 14 - 11 13 D8 FC E5 E8 23 F5 <\r><\n>'
            'C:0080: E8 80 F3 C0 01 C0 00 79 - C1 78 80 D8 FE D9 FA D0 <\r><\n>'
            'C:0090: 00 D0 01 22 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>'
            'C:00A0: 00 00 00 00 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>'
            'C:00B0: 00 00 00 00 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>'
            'C:00C0: 00 00 00 00 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>'
            'C:00D0: 00 00 00 00 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>'
            'C:00E0: 00 00 00 00 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>'
            'C:00F0: 00 00 00 00 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>'
            'C:0110: 00 00 00 00 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>'
            'C:0120: 00 00 00 00 00 00 00 00 - 00 00 00 00 00 00 00 00 <\r><\n>')
        s = s.replace('<\r>','')
        s = s.replace('<\n>','\n')
        s = s.replace('C:','')
        self.label_RAM.setText(s)
        # except Exception as e:
        #     print("> > > ERROR: {}".format(e))
        #     exit(1)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
