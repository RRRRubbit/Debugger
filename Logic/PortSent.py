import re
import sys
import binascii
import time
import serial
import serial.tools.list_ports
from PyQt5.QtCore import QTimer, QUrl, pyqtSignal, QObject
from PyQt5.QtWidgets import *
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QThread

#from Gui.ui_BreakPointDialog import *
#from Gui.ui_MainWindow import *
from Gui.ui_PortSelect import *
#from Logic.mainwindow import *




class PortSelectDialog(QtWidgets.QDialog, Ui_Dialog_PortSelect):
    opened = pyqtSignal()
    closed = pyqtSignal()
    readyRead = pyqtSignal()
    def __init__(self, parent=None):
        super(PortSelectDialog, self).__init__(parent)
        self.setupUi(self)
        # 设置实例
        self.CreateItems()
        # 设置信号与槽
        self.CreateSignalSlot()
    def SerialManager(self):
        # 创建串口实例
        #def __init__(self, parent=None):
            #super().__init__(parent)
        def open_port():
            if not self.com or not self.com.isOpen():
                #self.com = serial.Serial(port, baudrate)
                #self.com.open()
                self.opened.emit()
                print("Serial port opened")
        def close_port():
            if not self.com or not self.com.isOpen()():
                self.com.close()
                self.closed.emit()
                print("Serial port closed")

        def run():
            while True:
                if self.com and self.com.is_open:
                    data = self.com.read_all()
                    if data:
                        self.readyRead.emit()
            pass


    def openSerialPort(self):
        global serial_is_open
        serial_is_open = True
    # 设置实例
    def CreateItems(self):
        #Qt 串口类
        #self.com = QSerialPort()
        # # serial串口类
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

    # 显示时间
    def ShowTime(self):
        self.label_Time.setText(time.strftime("%B %d, %H:%M:%S", time.localtime()))

    # 串口发送数据
    def Com_Send_Data(self):
        txData = self.textEdit_Send.toPlainText()
        if len(txData) == 0:
            return
        if self.checkBox_HexSend.isChecked() == False:
            self.com.write(txData.encode('UTF-8'))
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

    def send_from_hex_file(self, hex_file_path):
        # 打开hex文件
        with open(hex_file_path, 'r') as f:
            # 逐行读取hex文件内容
            for line in f:
                # 发送每一行数据（假设每一行都是有效的十六进制数据）
                self.com.write(bytes.fromhex(line.strip()))
                # 延时一段时间（根据需要调整）
                time.sleep(0.1)


    # 串口接收数据
    def Com_Receive_Data(self):

        try:
            rxData = bytes(self.com.read_all())
        except:
            QMessageBox.critical(self, 'Fatal error', 'The serial port received the wrong data')
        if self.checkBox_HexShow.isChecked() == False:
            try:
                self.textEdit_Receive.insertPlainText(rxData.decode('UTF-8'))
            except:
                pass
        else:
            Data = binascii.b2a_hex(rxData).decode('ascii')
            # re 正则表达式 (.{2}) 匹配两个字母
            hexStr = ' 0x'.join(re.findall('(.{2})', Data))
            # 补齐第一个 0x
            hexStr = '0x' + hexStr
            self.textEdit_Receive.insertPlainText(hexStr)
            self.textEdit_Receive.insertPlainText(' ')
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

    def closeEvent(self, event):
        # Check if the serial port is open
        if self.SerialManager.com and self.SerialManager.com.isOpen():
            # Serial port is open, hide the window
            event.ignore()  # Ignore the close event
            QMessageBox.critical(self, 'Warning', 'The serial port is still open', )
            self.hide()  # Hide the window
        else:
            # Serial port is not open, close the window
            self.close()  # Accept the close event

#
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    #PortSelectDialog().listport()
    mainWindow = PortSelectDialog()
    mainWindow.show()
    sys.exit(app.exec_())
