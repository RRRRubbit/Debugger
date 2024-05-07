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
from Logic.BreakPointDialog import *
from Logic.PortSent import *
from PyQt5.QtSerialPort import QSerialPortInfo, QSerialPort
serial_is_open = False
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sign_one = pyqtSignal(str)
    trigger_PortSent = pyqtSignal()
    global hexfile_dir
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.CreateItems()
        self.CreateSignalSlot()
    def CreateSignalSlot(self):
        self.actionOpen_Port.triggered.connect(self.PortSent_show)
        self.actionUpdateregister.triggered.connect(self.get_register)
        self.actionOpen.triggered.connect(self.PortSelect.send_from_hex_file)
        self.actionRun.triggered.connect(self.PortSelect.run_code)
        self.actionLoad.triggered.connect(self.get_lst)
       # self.actionLoad.triggered.connect(self.upload)
        self.actionStep_Run.triggered.connect(self.PortSelect.run_step_code)
        self.actionStep_Function_Run.triggered.connect(self.PortSelect.run_step_function_code)
        self.actionUpdate_RAM.triggered.connect(self.get_RAM)
        self.actionUpdate_Port.triggered.connect(self.get_IO)
        self.actionMake_BreakPoint.triggered.connect(self.BreakPointDialog_show)
        self.actionClean_All_Break_Point.triggered.connect(self.clean_all_break_point)
        self.PortSelect.text_receive_register.connect(self.set_register)
        self.PortSelect.text_receive_RAM.connect(self.set_RAM)
        self.PortSelect.text_receive_IO.connect(self.set_IO)

    def CreateItems(self):
        self.PortSelect = PortSelectDialog()
        self.BreakPoint = BreakPointDialog()
    def PortSent_show(self):
        # 创建子窗口实例
        self.PortSelect.show()
        # dialog.stop_thread.connect(thread.stop)
        # self.thread.start()
        #PortSelect = PortSelectDialog()
        # 将信号连接到子窗口的槽函数
        # 显示子窗口
        self.PortSelect.exec_()
        # 发出信号，触发子窗口的槽函数
        #ps.closeEvent()
    def BreakPointDialog_show(self):
        #bk = BreakPointDialog()
        self.BreakPoint.show()
    def get_IO(self):
        s = self.PortSelect.get_IO()
        if s == "":
            QMessageBox.warning(self, "Warning", "Could not get all ports. Please check the connection.")
            return
        elif s != "":
            # s = "P0=1111111\r\nP1=1111111\r\nP2=1111111\r\nP3=1111111\r\nP4=1111111\r\nP5=1111111\r\n"
            if len(s) == 0 or s[-1] != "#":
                QMessageBox.warning(self, "Warning", "Could not get all ports. Please check the connection.")
            else:
                # self.set_register(self.s)
                return
        time.sleep(0.1)
    def get_lst(self):
        s, _ = QFileDialog.getOpenFileName(None, 'Open a hex file', 'C:\\', 'lst files (*.lst)')
        global hexfile_dir
        hexfile_dir = s
        a=open(hexfile_dir, 'r').readlines()
        self.listWidget_ASM.addItems(a)

        keyStart = '<Package name="com.tencent.tmgp.sgame">'
        keyEnd = '</Package>'
        buff = file.read()
        pat = re.compile(keyStart + '(.*?)' + keyEnd, re.S)
        result = pat.findall(buff)

    def set_IO(self, message):
        #s=message.split("\r\n#dd")
        s= re.compile(r'D:(.+?)\r\n#')
        c=s.findall(message)
        i = 0
        P = ['P0=', 'P1=', 'P2=', 'P3=', 'P4=', 'P5=']
        d = ''
        e = '\r\n'
        '''
        D:80: BD
        #dd80 80
        D:90: FE 
        #dd90 90
        D:A0: 7E
        #dda0 a0
        D:B0: FD
        #ddb0 b0
        D:E8: FF
        #dde8 e8
        D:F8: 3F
        #ddf8 f8
        #di0 4f
        '''
        for line in c:
            #print(line)
            line = line.split()
            line_list = list(line)
            line_list[0]=P[i]
            i=i+1
            line_list_1_bin=bin(int(line_list[1],16))
            line_list_1_bin=line_list_1_bin.lstrip('0b')
            line_list[1]='{:0>8}'.format(line_list_1_bin)
            line = ''.join(line_list)
            d = d+line+e
        print(d)
        self.label_Port.setText(d)
        return d
    def get_register(self):
        s=self.PortSelect.get_register()
        if s == "":
            QMessageBox.warning(self,"Warning","Could not get all register. Please check the connection.")
            return
        elif s !="":
            #s = "RA RB R0 R1 R2 R3 R4 R5 R6 R7 PSW DPTR SP PC<\r><\n>FF FF FF FF FF FF FF FF FF FF ---R0--- 0000 07 0000 <\r><\n>"
            if len(s) == 0 or s[-1] != "#":
                QMessageBox.warning(self,"Warning","Could not get all register. Please check the connection.")
            else:
                #self.set_register(self.s)
                return
        time.sleep(0.1)
    def set_register(self, message):
        # message=self.PortSelect.text_receive
        message = message[:-1]
        message.replace('\r', '')
        self.label.setText(message)
        return message
    #def register_value= a
    #return register_value
    def clean_all_break_point(self):
            print("> Starting make breakpoint... ")
            self.comSend(message="BK ALL\r")
            #s = PortSelectDialog.(expected="#".encode("utf-8")).decode("utf-8")
            #if len(s) == 0 or s[-1] != "#":
                #raise Exception("Could not make breakpoint. Please reset and try again.")
    def get_RAM(self):
        s = self.PortSelect.get_RAM()
        if s == "":
            QMessageBox.warning(self,"Warning","Could not get all register. Please check the connection.")
            return
        elif s !="":
            #s = "RA RB R0 R1 R2 R3 R4 R5 R6 R7 PSW DPTR SP PC<\r><\n>FF FF FF FF FF FF FF FF FF FF ---R0--- 0000 07 0000 <\r><\n>"
            if len(s) == 0 or s[-1] != "#":
                QMessageBox.warning(self,"Warning","Could not get all register. Please check the connection.")
            else:
                #self.set_register(self.s)
                return
        time.sleep(0.1)
    def set_RAM(self,message):
        s = message[:-1]
        '''
        s =(
C:0000: 01 00 03 75 E8 FE 78 14 11 13 D8 FC E5 E8 23 F5
C:0010: 02 00 03 75 E8 FE 78 14 11 13 D8 FC E5 E8 23 F5
C:0020: 03 00 03 75 E8 FE 78 14 11 13 D8 FC E5 E8 23 F5
C:0030: 04 00 03 75 E8 FE 78 14 11 13 D8 FC E5 E8 23 F5
C:0040: 05 00 03 75 E8 FE 78 14 11 13 D8 FC E5 E8 23 F5
C:0050: 06 00 03 75 E8 FE 78 14 11 13 D8 FC E5 E8 23 F5
C:0060: 07 00 03 75 E8 FE 78 14 11 13 D8 FC E5 E8 23 F5
C:0070: 08 00 03 75 E8 FE 78 14 11 13 D8 FC E5 E8 23 F5
C:0080: E9 80 F3 C0 01 C0 00 79 C1 78 80 D8 FE D9 FA D0
C:0090: 10 D0 01 22 00 00 00 00 00 00 00 00 00 00 00 00
C:00A0: 11 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
C:00B0: 12 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
C:00C0: 13 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
C:00D0: 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
C:00E0: 15 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
C:00F0: 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
C:0110: 17 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
C:0120: 18 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
#
        )
        '''
        s = s.replace('C:','')
        b = '-'
        c=str.splitlines(s)
        d = ''
        e = '\r\n'
        for line in c:
            #print(line)
            line = line.split()
            line_list = list(line)
            line_list.insert(7,b)
            line = ' '.join(line_list)
            d = d+line+e
            #print(d)
        print(d)
        self.label_RAM.setText(d)
        return s

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
