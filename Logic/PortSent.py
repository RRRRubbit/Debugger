import re
import sys
import binascii
import threading
import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer, QUrl, pyqtSignal, QObject
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QPushButton, QMainWindow, QProgressDialog
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QThread
#from Gui.ui_BreakPointDialog import *
#from Gui.ui_MainWindow import *
from Gui.ui_PortSelect import *
#from Logic.mainwindow import *

class PortSelectDialog(QtWidgets.QDialog, Ui_Dialog_PortSelect):
    text_receive_register=pyqtSignal(str)
    text_receive_RAM = pyqtSignal(str)
    text_receive_IO =pyqtSignal(str)
    text_receive_Breakpoint =pyqtSignal(str)
    signal_get_register=pyqtSignal(str)
    signal_get_RAM=pyqtSignal(str)
    signal_get_IO=pyqtSignal(str)
    def __init__(self, parent=None):
        super(PortSelectDialog, self).__init__(parent)
        self.setupUi(self)
        # 设置实例
        self.CreateItems()
        # 设置信号与槽
        self.CreateSignalSlot()
    def openSerialPort(self):
        global serial_is_open
        serial_is_open = True
    # 设置实例
    def CreateItems(self):
        #Qt 串口类
        #self.com = QSerialPort()
        #serial串口类
        self.com = serial.Serial()
        # Qt 定时器类
        # 创建串口管理器实例
        #self.serial_manager = self.SerialManager()
        self.timer = QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.ShowTime)  # 计时结束调用operate()方法
        self.timer.start(100)  # 设置计时间隔 100ms 并启动


    # 设置信号与槽
    def CreateSignalSlot(self):
        self.pushButton_OpenPort.clicked.connect(self.Com_Open_Button_clicked)
        self.pushButton_ClosePort.clicked.connect(self.Com_Close_Button_clicked)
        self.pushButton_Send.clicked.connect(self.SendButton_clicked)
        self.pushButton_Refresh.clicked.connect(self.Com_Refresh_Button_Clicked)
        self.timer.timeout.connect(self.Com_Receive_Data)  # 接收数据
        self.checkBox_HexShow.stateChanged.connect(self.hexShowingClicked)
        self.checkBox_HexSend.stateChanged.connect(self.hexSendingClicked)
        self.pushButto_Clear.clicked.connect(self.clean_Receive_Zone)
        ####测试区域
        #self.checkBox_AutoSend.stateChanged.connect(self.progress)
        ####测试区域



    # 显示时间
    def ShowTime(self):
        self.label_Time.setText(time.strftime("%B %d, %H:%M:%S", time.localtime()))
####从这里开始补充测试
    def send_from_hex_file(self):
        if self.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please Open Serial Port")
            return
        else:

            #设置进度条
            self.progress_dialog = QProgressDialog('Uploading Hex File...', 'Cancel', 0, 100, self)
            self.progress_dialog.setAutoClose(True)
            self.progress_dialog.setAutoReset(True)
            self.progress_dialog.canceled.connect(self.cancel_upload)
            self.upload_thread = None
            #初始化进度条信息
            self.progress_dialog.setValue(0)
            self.progress_dialog.show()
            #打开串口
            self.file_path, _ = QFileDialog.getOpenFileName(self, 'Open hex file', '', 'Hex Files (*.hex)')
            if not self.file_path:
                QMessageBox.warning(self, "Warning", "No file selected")
                return
            #创建线程实例
            self.upload_thread=UploadThread(self.com, self.file_path)
            self.upload_thread.progress.connect(self.update_progress)
            self.upload_thread.finished.connect(self.upload_finished)
            self.upload_thread.start()
    def update_progress(self, value):
        if value == -1:
            QMessageBox.critical(self, "Error", "An error occurred during upload")
            self.progress_dialog.cancel()
        else:
            self.progress_dialog.setValue(value)

    def upload_finished(self):
        self.progress_dialog.setValue(100)
        QMessageBox.information(self, "Success", "Upload finished successfully")

    def cancel_upload(self):
        if self.upload_thread.isRunning():
            self.upload_thread.terminate()
        self.progress_dialog.reset()
        QMessageBox.warning(self, "Canceled", "Upload canceled")

 ####补充测试停止
    def run_code(self):
        if self.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please Open Serial Port")
            return False
        else:
            self.com.write("G 8000\r".encode("utf-8"))
            s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            if len(s) == 0 or s[-1] != "#":
                raise Exception("Could not start program. Please reset and try again.")
            self.com.write("BL\r".encode("utf-8"))
            s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            if s == '\r\n#':
                self.com.write("G\r".encode("utf-8"))
                QMessageBox.warning(self, "Warning", "Code is running with out BreakPoint")
            else:
                self.com.write("G\r".encode("utf-8"))
                #QMessageBox.warning(self, "Warning", "Code is running and stop at BreakPoint")
                s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
                self.signal_get_register.emit('Run code then get Reg')
                self.signal_get_IO.emit('Run code then get IO')
                self.signal_get_RAM.emit('Run code then get RAM')
            return
    def run_step_code(self):
        if self.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please Open Serial Port")
            return False
        else:
            self.com.write("T\r".encode("utf-8"))
            s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            if len(s) == 0 or s[-1] != "#":
                raise Exception("Could not start program. Please reset and try again.")
            self.signal_get_register.emit('Run code then get Reg')
            self.signal_get_IO.emit('Run code then get IO')
            self.signal_get_RAM.emit('Run code then get RAM')
            return
    def run_step_function_code(self):
        if self.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please Open Serial Port")
            return False
        else:
            self.com.write("P\r".encode("utf-8"))
            s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            if len(s) == 0 or s[-1] != "#":
                raise Exception("Could not start program. Please reset and try again.")
            self.signal_get_register.emit('Run code then get Reg')
            self.signal_get_IO.emit('Run code then get IO')
            self.signal_get_RAM.emit('Run code then get RAM')
            return
    def get_IO(self):
        if self.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please Open Serial Port")
            return
        else:
            a =''
            self.com.write("DD 80 80\r".encode("utf-8"))#P0
            a += self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            self.com.write("DD 90 90\r".encode("utf-8"))#P1
            a += self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            self.com.write("DD a0 a0\r".encode("utf-8"))#P2
            a += self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            self.com.write("DD b0 b0\r".encode("utf-8"))#P3
            a += self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            self.com.write("DD e8 e8\r".encode("utf-8"))#P4
            a += self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            self.com.write("DD f8 f8\r".encode("utf-8"))#P5
            a += self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            s = a
            #print(s)
            if len(s) == 0 or s[-1] != "#":
                raise Exception("Could not get IO. Please reset and try again.")
            else:
                self.text_receive_IO.emit(s)
        return s
    def get_register(self):
            if self.com.is_open == False:
                QMessageBox.warning(self, "Warning", "Please Open Serial Port")
                return
            else:
                self.com.write('X\r'.encode("utf-8"))
                #self.com.write(0x0D)
                s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
                #print(s)
                #print(self.text_receive_register)
                #self.text_receive = s
                if len(s) == 0 or s[-1] != "#":
                    raise Exception("Could not get registers. Please reset and try again.")
                else:
                    self.text_receive_register.emit(s)
            return s
    def get_RAM(self, Scroll_Value=None):
        if self.com.is_open == False:
            QMessageBox.warning(self, "Warning", "Please Open Serial Port")
            return
        else:
            if Scroll_Value == None :
                self.com.write("DC 0000 003f\r".encode("utf-8"))
                s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
                #print(s)
                #print(self.text_receive_RAM)
                if len(s) == 0 or s[-1] != "#":
                    raise Exception("Could not display program memory area. Please reset and try again.")
                else:
                    self.text_receive_RAM.emit(s)
            else:
                #Scroll_Value=hex(Scroll_Value)
                start = 0x0000 + Scroll_Value*64 #添加偏移
                end = 0x003f + Scroll_Value*64
                start_str = hex(start)[2:] #去掉0x前缀
                end_str = hex(end)[2:]
                start_str=start_str.zfill(4)
                end_str=end_str.zfill(4)
                self.com.write(("DC"+" "+start_str+" "+end_str+"\r").encode("utf-8"))
                s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
                #print(s)
                #print(self.text_receive_RAM)
                if len(s) == 0 or s[-1] != "#":
                    raise Exception("Could not display program memory area. Please reset and try again.")
                else:
                    self.text_receive_RAM.emit(s)
        return s

    def Set_Breakpoint(self, BP_signal=None):
        if BP_signal == '':
            #QMessageBox.critical(self, 'Warning', 'Breakpoint is not defined', )
            return None
        elif BP_signal == 'BPclean':
            self.Com_Send_Data("BK ALL" + '\r')
            s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            #print(s)
        else:
            self.Com_Send_Data("BS "+BP_signal+'\r')
            s = self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
            #print(s)
    def Read_Breakpoint(self, BP_startread_signal=None):
        if BP_startread_signal == '':
            #QMessageBox.critical(self, 'Warning', '', )
            return None
        else:
            if self.com.is_open == False:
                QMessageBox.warning(self, "Warning", "Please Open Serial Port")
            else:
                self.Com_Send_Data('BL\r')
                text_receive_Breakpoint=self.com.read_until(expected="#".encode("utf-8")).decode("utf-8")
                self.text_receive_Breakpoint.emit(text_receive_Breakpoint)
    # 串口发送数据
    def Com_Send_Data(self, message=None):
        txData = self.textEdit_Send.toPlainText()
        if len(txData) == 0 and message == None:
            return
        elif len(txData) == 0 and message != None:
            #message=message+"\r"
            self.com.write(message.encode('UTF-8'))
            return
        elif self.checkBox_HexSend.isChecked() == False:

            self.com.write(txData.encode('UTF-8'))
            self.com.write('\r'.encode('UTF-8'))
        else:
            Data = txData.replace(' ', '')
            # 如果16进制不是偶数个字符, 去掉最后一个, [ ]左闭右开
            if len(Data) % 2 == 1:
                Data = Data[0:len(Data) - 1]
            # 如果遇到非16进制字符
            if Data.isalnum() is False:
                QMessageBox.critical(self, 'Error', 'Contains non-hexadecimal numbers')
            try:
                hexData = binascii.a2b_hex(Data)
            except:
                QMessageBox.critical(self, 'Error', 'Conversion encoding error')
                return
            # 发送16进制数据, 发送格式如 ‘31 32 33 41 42 43’, 代表'123ABC'
            try:
                self.com.write(hexData)
            except:
                QMessageBox.critical(self, 'Abnormal', 'Hexadecimal sending error')
                return

    # 串口接收数据
    def Com_Receive_Data(self):
        if self.com.is_open == True:
            try:
                rxData = bytes(self.com.read_all())
            except:
                QMessageBox.critical(self, 'Fatal error', 'The serial port received wrond data. Please check the serial port connect.')
                self.Com_Close_Button_clicked()
            if self.checkBox_HexShow.isChecked() == False:
                try:
                    self.textEdit_Receive.insertPlainText(rxData.decode('UTF-8'))
                except:
                    pass
            elif self.checkBox_HexShow.isChecked() == True and rxData !=b'' :
                Data = binascii.b2a_hex(rxData).decode('ascii')
                # re 正则表达式 (.{2}) 匹配两个字母
                hexStr = ' 0x'.join(re.findall('(.{2})', Data))
                # 补齐第一个 0x
                hexStr = '0x' + hexStr
                self.textEdit_Receive.insertPlainText(hexStr)
                self.textEdit_Receive.insertPlainText(' ')
            elif rxData == b'':
                return None
        else:
            return None

    # 串口刷新
    def Com_Refresh_Button_Clicked(self):
        self.comboBox_PortName.clear()
        com_list = list(serial.tools.list_ports.comports())
        ports = ""
        for info in com_list:
            #ports.join(info.device)
            #com.setPort(info)
            #if self.SerialManager.open():
            self.comboBox_PortName.addItem(info.device)
        #com.close()

    # 16进制显示按下
    def hexShowingClicked(self):
        if self.checkBox_HexShow.isChecked() == True:
            # 接收区换行
            self.textEdit_Receive.insertPlainText('\n')

    # 16进制发送按下
    def hexSendingClicked(self):
        if self.checkBox_HexSend.isChecked() == True:
            pass

    # 发送按钮按下
    def SendButton_clicked(self):
        self.Com_Send_Data()
        #SendThread_thread=SendThread()
        #SendThread_thread.start()

    # 串口刷新按钮按下
    def Com_Open_Button_clicked(self):
        #open serial signol send then serial_is_open==True
        self.openSerialPort()
        #### com Open Code here ####
        comName = self.comboBox_PortName.currentText()
        comBaud = int(self.comboBox_BaudRate.currentText())
        self.com.port=comName
        self.com.baudrate=comBaud

        try:
            self.com.open()
            # if com.is_open == True:
            #     #QMessageBox.critical(self, 'Fatal error', 'The serial port failed to be opened')
            #     return
        except:
            QMessageBox.critical(self, 'Fatal error', 'The serial port failed to be opened')
            return
        self.pushButton_ClosePort.setEnabled(True)
        self.pushButton_OpenPort.setEnabled(False)
        self.pushButton_Refresh.setEnabled(False)
        self.comboBox_PortName.setEnabled(False)
        self.comboBox_BaudRate.setEnabled(False)
        self.label_IsOpenOrNot.setText('  Opened')
        #self.com.setBaudRate(comBaud)

    def Com_Close_Button_clicked(self):
        if self.com.is_open == True:
            # 先暂停串口读取
            #self.com.blockSignals(True)
            # 关闭串口
            self.com.close()
            print("Serial port closed")
            # 恢复串口读取
            #self.com.blockSignals(False)
        else:
            print("Serial port is not open")

        self.pushButton_ClosePort.setEnabled(False)
        self.pushButton_OpenPort.setEnabled(True)
        self.pushButton_Refresh.setEnabled(True)
        self.comboBox_PortName.setEnabled(True)
        self.comboBox_BaudRate.setEnabled(True)
        self.label_IsOpenOrNot.setText('  Closed')

    def clean_Receive_Zone(self):
        self.textEdit_Receive.clear()

    def closeEvent(self, event):
        # Check if the serial port is open
        if self.com and self.com.isOpen():
            # Serial port is open, hide the window
            event.ignore()  # Ignore the close event
            QMessageBox.critical(self, 'Warning', 'The serial port is still open', )
            self.hide()  # Hide the window
        else:
            # Serial port is not open, close the window
            self.close()  # Accept the close event

#
class UploadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int)
    def __init__(self, com, file_path):
        super().__init__()
        self.com = com
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                total_lines = len(lines)
                for i, line in enumerate(lines):
                    self.com.write(line.encode("utf-8"))
                    #s = self.com.read_until(expected="#".encode("utf-8")).decode("utf--8")
                    #print(s)
                    #time.sleep(0.01)  # Simulate a delay in sending data
                    progress_percent = int((i + 1) / total_lines * 100)
                    print(progress_percent)
                    print(line)
                    self.progress.emit(progress_percent)
                    if progress_percent == 100:
                        self.finished.emit(1)
        except Exception as e:
            print(f"Error: {e}")
            self.progress.emit(-1)  # Emit a special value to indicate an error


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    #PortSelectDialog().listport()
    mainWindow = PortSelectDialog()
    mainWindow.show()
    sys.exit(app.exec_())
