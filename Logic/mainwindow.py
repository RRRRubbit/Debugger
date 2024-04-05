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
       # self.actionLoad.triggered.connect(self.upload)
        self.actionStep_Run.triggered.connect(self.PortSelect.run_step_code)
        self.actionStep_Function_Run.triggered.connect(self.PortSelect.run_step_function_code)
        self.actionMake_BreakPoint.triggered.connect(self.BreakPointDialog_show)
        self.actionClean_All_Break_Point.triggered.connect(self.clean_all_break_point)
        self.PortSelect.text_receive.connect(self.set_register)
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

        #def register_value= a
        #return register_value


    def clean_all_break_point(self):
            print("> Starting make breakpoint... ")
            self.comSend(message="BK ALL\r")
            #s = PortSelectDialog.(expected="#".encode("utf-8")).decode("utf-8")
            #if len(s) == 0 or s[-1] != "#":
                #raise Exception("Could not make breakpoint. Please reset and try again.")

    def set_register(self,message):
       #message=self.PortSelect.text_receive
        message = message[:-1]
        message.replace('\r', '')
        self.label.setText(message)
        return message
    def set_RAM(self):
        board = PortSelectDialog.com
        board.com.write("\x03".encode("utf-8"))
        #port = PortSelectDialog.openport()
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
