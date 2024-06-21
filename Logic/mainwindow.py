# -*- coding: UTF-8 -*-
import re

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QBrush, QColor
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
    ScrollBar_RAM = pyqtSignal(int)
    ProgramCounter = pyqtSignal((str))
    global hexfile_dir

######initialization function##############################################################################################
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.CreateItems()
        self.CreateSignalSlot()
        self.SetListwidget()

    def CreateSignalSlot(self):
        self.actionOpen_Port.triggered.connect(self.PortSent_show)
        self.actionUpdate_Register.triggered.connect(self.get_register)
        self.actionOpen.triggered.connect(self.PortSelect.send_from_hex_file)
        self.actionRun.triggered.connect(self.PortSelect.run_code)
        self.actionLoad.triggered.connect(self.get_lst)
        self.actionList_Port.triggered.connect(self.set_Hightlight)
        self.ProgramCounter.connect(self.set_Hightlight)
       # self.actionLoad.triggered.connect(self.upload)
        self.actionStep_Run.triggered.connect(self.PortSelect.run_step_code)
        self.actionStep_Function_Run.triggered.connect(self.PortSelect.run_step_function_code)
        self.actionUpdate_RAM.triggered.connect(self.get_RAM)
        self.actionUpdate_Port.triggered.connect(self.get_IO)
        self.actionMake_BreakPoint.triggered.connect(self.BreakPointDialog_show)
        self.actionMake_BreakPoint.triggered.connect(self.BreakPoint.read_BreakPoints)
        self.actionClean_All_Break_Point.triggered.connect(self.clean_all_break_point)

        # Breakpoint model signal connect
        self.PortSelect.text_receive_register.connect(self.set_register)
        self.PortSelect.text_receive_RAM.connect(self.set_RAM)
        self.PortSelect.text_receive_IO.connect(self.set_IO)
        self.verticalScrollBar_RAM.valueChanged.connect(self.get_ScrollBar)
        self.ScrollBar_RAM.connect(self.PortSelect.get_RAM)
        self.PortSelect.text_receive_Breakpoint.connect(self.BreakPoint.set_BreakPoints_text)
        self.PortSelect.signal_get_register.connect(self.get_register)
        self.PortSelect.signal_get_RAM.connect(self.get_RAM)
        self.PortSelect.signal_get_IO.connect(self.get_IO)

        #Breakpoint model signal connect
        self.BreakPoint.BP_signal.connect(self.PortSelect.Set_Breakpoint)
        self.BreakPoint.BP_startread_signal.connect(self.PortSelect.Read_Breakpoint)

        #StatusBar model signal connect
        self.PortSelect.signal_status_bar.connect(self.statusBar_show)

    def CreateItems(self):
        self.PortSelect = PortSelectDialog()
        self.BreakPoint = BreakPointDialog()

    def PortSent_show(self):
        # 创建子窗口实例
        self.PortSelect.show()
        self.statusBar_show('PortSelect window is open')
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
        self.statusBar_show('Breakpoint window is open')
    def statusBar_show(self,message):
        self.statusbar.showMessage(message,5000)
######Breakpoint functions##############################################################################################
    def SetListwidget(self):
        self.listWidget_ASM.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget_ASM.customContextMenuRequested.connect(self.show_context_menu)
        # 创建断点列表
        self.breakpoints = []
        # 创建QLineEdit列表
        self.lineEdits = [getattr(self.BreakPoint, f'lineEdit_{i:02d}') for i in range(10)]
    def show_context_menu(self, position):
        # 创建上下文菜单
        menu = QMenu()
        item = self.listWidget_ASM.itemAt(position)
        if item is None:
            return
        # 添加断点动作
        add_breakpoint_action = QAction('Add Breakpoint', self)
        add_breakpoint_action.triggered.connect(lambda: self.add_breakpoint(item))
        menu.addAction(add_breakpoint_action)

        # 删除断点动作
        remove_breakpoint_action = QAction('Remove Breakpoint', self)
        remove_breakpoint_action.triggered.connect(lambda: self.remove_breakpoint(item))
        menu.addAction(remove_breakpoint_action)

        # 添加设置断点动作
        enable_breakpoint_action = QAction('Enable Breakpoint', self)
        enable_breakpoint_action.triggered.connect(lambda: self.enable_breakpoint(item))
        menu.addAction(enable_breakpoint_action)

        # 禁用断点动作
        disable_breakpoint_action = QAction('Disable Breakpoint', self)
        disable_breakpoint_action.triggered.connect(lambda: self.disable_breakpoint(item))
        menu.addAction(disable_breakpoint_action)

        # 显示菜单
        menu.exec_(self.listWidget_ASM.mapToGlobal(position))

    def add_breakpoint(self, item):
        item_text = item.text()
        address_part = item_text[0:4]
        BP_signal = address_part
        if self.PortSelect.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please open the Serial Port.")
            return False
        else:
            # 调用设置断点的方法，并传递 BP_signal 作为参数
            s=self.PortSelect.Set_Breakpoint(BP_signal)
            if s == None:
                self.breakpoints += [BP_signal]
                if ' [Breakpoint]' not in item_text:
                    item.setText(f"{item_text} [Breakpoint] [Enable]")
                else:
                    QMessageBox.warning(self, "Warning", "There is already a Breakpoint.")
                    return
            else:
                return
    def remove_breakpoint(self, item):
        item_text = item.text()
        address_part = item_text[0:4]
        BP_Addtrss = address_part
        if self.PortSelect.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please open the Serial Port.")
        elif BP_Addtrss in self.breakpoints:
            BP_signal=self.breakpoints.index(BP_Addtrss)
            s = self.PortSelect.Remove_Breakpoint(BP_signal)
            print(f'Removed breakpoint at: {item_text}')
            if s == None:
                if ' [Breakpoint] [Enable]' in item_text:
                    item.setText(item_text.replace(' [Breakpoint] [Enable]', ''))
                    # self.breakpoints.remove(item_text.replace(' [Breakpoint]', ''))
                elif ' [Breakpoint] [Disable]' in item_text:
                    item.setText(item_text.replace(' [Breakpoint] [Disable]', ''))
                else:
                    QMessageBox.warning(self, "Warning", "There is no Breakpoint.")
            else:
                return
        else:
            QMessageBox.warning(self, "Warning", "There is no Breakpoint.")
            return

    def enable_breakpoint(self, item):
        item_text = item.text()
        address_part = item_text[0:4]
        BP_Addtrss = address_part
        if self.PortSelect.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please open the Serial Port.")
        elif BP_Addtrss in self.breakpoints:
            BP_signal=self.breakpoints.index(BP_Addtrss)
            s = self.PortSelect.Enable_Breakpoint(BP_signal)
            print(f'Enable breakpoint at: {item_text}')
            if s == None:
                if ' [Breakpoint]' not in item_text:
                    QMessageBox.warning(self, "Warning", "There is no Breakpoint.")
                elif ' [Breakpoint] [Enable]'  in item_text:
                    QMessageBox.warning(self, "Warning", "The is already Breakpoint enabled.")
                elif ' [Breakpoint] [Disable]' in item_text:
                    item.setText(item_text.replace(' [Disable]', ' [Enable]'))
                    address_part = item_text[0:4]
                    BP_signal = address_part
                    self.PortSelect.Enable_Breakpoint(BP_signal)
                    print(f'Removed breakpoint at: {item_text}')
                else:
                    item.setText(f"{item_text} [Enable]")
            else:
                return
        else:
            QMessageBox.warning(self, "Warning", "There is no Breakpoint.")
            return


    def disable_breakpoint(self, item):
        item_text = item.text()
        address_part = item_text[0:4]
        BP_Addtrss = address_part
        if self.PortSelect.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please open the Serial Port.")
        elif BP_Addtrss in self.breakpoints:
            BP_signal=self.breakpoints.index(BP_Addtrss)
            s = self.PortSelect.Disable_Breakpoint(BP_signal)
            print(f'Disable breakpoint at: {item_text}')
            if s == None:
                if ' [Breakpoint]' not in item_text:
                    QMessageBox.warning(self, "Warning", "There is no Breakpoint.")
                else:
                    item.setText(item_text.replace('[Enable]', '[Disable]'))
            else:
                return
        else:
            QMessageBox.warning(self, "Warning", "There is no Breakpoint.")
            return

######Data geting functions##############################################################################################
    def get_ScrollBar(self):
        s = self.verticalScrollBar_RAM.sliderPosition() #获取进度条信息
        self.ScrollBar_RAM.emit(s)
    def get_RAM(self):
        if self.PortSelect.com.is_open == True:
            print("> Starting get RAM... ")
            self.statusBar_show("Getting RAM")
            Scroll_Value = self.verticalScrollBar_RAM.value()
            #print(Scroll_Value)
            s = self.PortSelect.get_RAM(Scroll_Value)
            if s == "":
                QMessageBox.warning(self,"Warning","Could not get RAM. Please check the connection.")
                return
            elif s !="":
                if len(s) == 0 or s[-1] != "#":
                    QMessageBox.warning(self,"Warning","Could not get RAM. Please check the connection.")
                else:
                    #self.set_register(self.s)
                    return
            #time.sleep(0.1)
        else:
            QMessageBox.warning(self, "Warning", "Please open the serial port")
            return
    def get_IO(self):
        self.statusBar_show("Getting IO")
        if self.PortSelect.com.is_open == True:
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
        else:
            QMessageBox.warning(self,"Warning","Could not get all ports. Please check the connection.")

    def get_register(self):
        self.statusBar_show("Getting register")
        if self.PortSelect.com.is_open == True:
            s = self.PortSelect.get_register()
            if s == "":
                QMessageBox.warning(self, "Warning", "Could not get all register. Please check the connection.")
                return
            elif s != "":
                # s = "RA RB R0 R1 R2 R3 R4 R5 R6 R7 PSW DPTR SP PC<\r><\n>FF FF FF FF FF FF FF FF FF FF ---R0--- 0000 07 0000 <\r><\n>"
                if s == None or len(s) == 0 or s[-1] != "#":
                    QMessageBox.warning(self, "Warning", "Could not get all register. Please check the connection.")
                else:
                    self.get_ProgramCounter(s)
                    # self.set_register(self.s)
                    return
        else:
            QMessageBox.warning(self,"Warning","Could not get all registers. Please check the connection.")

    def get_lst(self):
        #Clean ASM Code Zone
        self.listWidget_ASM.clear()
        self.statusBar_show("Uploading lst file")
        s, _ = QFileDialog.getOpenFileName(None, 'Open a lst file', 'D:\\', 'lst files (*.lst)')
        global lstfile_dir
        lstfile_dir = s
        if lstfile_dir == '':
            return
        else:
            with open(lstfile_dir, 'r') as f:
                lst_content = f.read()
            #pattern = re.compile(r'^(\s*[\w\$]+:)?\s*([^\r\n;]*)', re.MULTILINE)

            address_pattern = re.compile(r'\s+\d+/(.+?);', re.MULTILINE)

            # 提取地址和内容
            addresses = address_pattern.findall(lst_content)
            # 输出匹配结果
            lines = addresses
            address_lines = {}

            # 遍历每一行
            for line in lines:
                parts = line.split(':')
                address = parts[0].strip()  # 获取地址部分
                content = parts[1].strip() if len(parts) > 1 else ''  # 获取内容部分（如果有）
                address_lines[address] = content  # 更新字典

            # 输出结果
            for address, content in address_lines.items():
                address=address.zfill(4) #补全4位十六进制
                memory=address+' : '+content
                self.listWidget_ASM.addItem(memory)

            if lstfile_dir == None:
                print("> > > Successful: File '{}' is not found".format(lstfile_dir))
            else:
                print("Successful: File '{}' is open".format(lstfile_dir))
                self.statusBar_show("Successful: File '{}' is open".format(lstfile_dir))
            return lstfile_dir

######Date processing and displaying functions##############################################################################################
    def set_RAM(self, message):
        s = message[:-1]  # 去掉#
        '''
        s =('DC 66c0 66ff
C:66C0: 12 8B 98 98 00 00 00 00 00 00 00 00 00 00 00 00 
C:66D0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
C:66E0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
C:66F0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
#'
        )
        '''
        s = s.replace('C:', '')  # 去掉C
        bar = '-'  # 每隔8位HEX添加分隔符
        star = '|'  # 分割ASCII区域分隔符
        c = str.splitlines(s)  # 把数列列表分割成字符串
        c = c[1:]  # 去掉指令部分
        d = ''
        e = '\r\n'
        for line in c:
            line = line.split()  # 分割字符串成单个行
            line_list = list(line)  # 分割每个行为单个字节
            ascii_list = []
            for hex_str in line_list[1:]:
                char = chr(int(hex_str, 16))
                if char.isprintable():  # 判断是否可见ASCII码
                    ascii_list.append(char)
                else:
                    ascii_list.append('.')  # 不可见替换成'.'
            line_list.insert(9, bar)  # 添加分隔符
            line_hex = ' '.join(line_list)
            line_ascii = ''.join(ascii_list)
            d = d + line_hex + ' ' + star + line_ascii + star + e
            # print(d)
        # print(d)
        # print(repr(d))
        # print(ascii_list)
        self.label_RAM.setText(d)
        return s

    def set_IO(self, message):
        #s=message.split("\r\n#dd")
        pattern= re.compile(r'D:(.+?)\r\n#')
        c=pattern.findall(message)
        i = 0
        P = ['P0 = ', 'P1 = ', 'P2 = ', 'P3 = ', 'P4 = ', 'P5 = ']
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
            d = d+line+e+e
        #print(d)
        self.label_Port.setText(d)
        return d
    def set_register(self, message):
        # message=self.PortSelect.text_receive
        message = message[:-1]#去掉#
        message = message[3:]#去掉X\r\n
        message.replace('\r', '')
        self.label_Reg.setText(message)
        return message
    #def register_value= a
    #return register_value
    def get_ProgramCounter(self, message=None):
        self.statusBar_show("Getting ProgramCounter")
        #message = "X\r\nRA RB R0 R1 R2 R3 R4 R5 R6 R7 PSW DPTR SP PC\r\nFF FF FF FF FF FF FF FF FF FF ---R0--- 0000 07 0010 \r\n#"
        if message != None:
            message = message[:-1]  # 去掉#
            message = message[3:]  # 去掉X\r\n
            message.replace('\r', '')
            message.replace('\n', '')
            parts = message.split()
            reversed_parts = reversed(parts)
            for part in reversed_parts:
                if len(part) == 4 and part.isalnum() and part.lower().isalpha() == False:  # 检查是否为4位非字母字符
                    PC= part
                    #print('PC='+PC+'\n')  # 输出: 0000
                    break
                else:
                    PC = '0000'
            self.ProgramCounter.emit(PC)
        else:
            return
    def set_Hightlight(self, PC=None,BP=None):
        self.statusBar_show("Hightlighting ProgramCounter")
        for index in range(self.listWidget_ASM.count()):
                item = self.listWidget_ASM.item(index)
                # 设置背景颜色
                Background = QBrush(QColor(255, 255, 255, 255))  # 黄色，带有一些透明度
                item.setBackground(Background)
        ProgramCounter=PC
        text_to_find=ProgramCounter
        for index in range(self.listWidget_ASM.count()):
                item = self.listWidget_ASM.item(index)
                if text_to_find in item.text():
                    # 设置背景颜色
                    brush = QBrush(QColor(255, 255, 0, 160))  # 黄色，带有一些透明度
                    item.setBackground(brush)

    def clean_all_break_point(self):
        if self.PortSelect.com.is_open == True:
            self.statusBar_show("Cleaning All Breakpoint")
            print("> Cleaning All Breakpoint... ")
            self.PortSelect.Com_Send_Data(message="BK ALL\r")
            s = self.PortSelect.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            self.PortSelect.textEdit_Receive.insertPlainText(s)
            print(s)
        else:
            QMessageBox.warning(self, "Warning", "Please open the serial port")
            return
            #s = PortSelectDialog.(expected="#".encode("utf-8")).decode("utf-8")
            #if len(s) == 0 or s[-1] != "#":
                #raise Exception("Could not make breakpoint. Please reset and try again.")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
