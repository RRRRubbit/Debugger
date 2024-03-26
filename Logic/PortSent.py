import re
import sys
import binascii
import time
import serial
from PyQt5.QtCore import QTimer, QUrl
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
    class SerialManager(QThread):
        opened = pyqtSignal()
        closed = pyqtSignal()

        def __init__(self, parent=None):
            super(SerialManager, self).__init__(parent)
            self.serial_port = None

        def open_port(self, port, baudrate):
            if not self.serial_port or not self.serial_port.isOpen():
                self.serial_port = serial.Serial(port, baudrate)
                self.opened.emit()
                print("Serial port opened")

        def close_port(self):
            if self.serial_port and self.serial_port.isOpen():
                self.serial_port.close()
                self.closed.emit()
                print("Serial port closed")

        def run(self):
            # Your serial port operations here
            pass

    def __init__(self, parent=None):
        super(PortSelectDialog, self).__init__(parent)
        self.setupUi(self)
        self.serial_manager = self.SerialManager()  # 实例化SerialManager类
        #Open Serial Port signal

        # 设置实例
        self.CreateItems()
        # 设置信号与槽
        self.CreateSignalSlot()
    def openSerialPort(self):
        global serial_is_open
        serial_is_open = True
    # 设置实例
    def CreateItems(self):
        # Qt 串口类
        self.com = QSerialPort()
        # Qt 定时器类
        self.timer = QTimer(self)  # 初始化一个定时器
        self.timer.timeout.connect(self.ShowTime)  # 计时结束调用operate()方法
        self.timer.start(100)  # 设置计时间隔 100ms 并启动

    # 设置信号与槽
    def CreateSignalSlot(self):
        self.pushButton_OpenPort.clicked.connect(self.Com_Open_Button_clicked)
        self.pushButton_ClosePort.clicked.connect(self.Com_Close_Button_clicked)
        self.pushButton_Send.clicked.connect(self.SendButton_clicked)
        self.pushButton_Refresh.clicked.connect(self.Com_Refresh_Button_Clicked)
        self.com.readyRead.connect(self.Com_Receive_Data)  # 接收数据
        self.checkBox_HexShow.stateChanged.connect(self.hexShowingClicked)
        self.checkBox_HexSend.stateChanged.connect(self.hexSendingClicked)


    # 跳转到 GitHub 查看源代码
    def Goto_GitHub(self):
        self.browser = QWebEngineView()
        self.browser.load(QUrl('https://github.com/Oslomayor/PyQt5-SerialPort-Stable'))
        self.setCentralWidget(self.browser)

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



    # 串口接收数据
    def Com_Receive_Data(self):

        try:
            rxData = bytes(self.com.readAll())
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
        com = QSerialPort()
        com_list = QSerialPortInfo.availablePorts()
        for info in com_list:
            com.setPort(info)
            if com.open(QSerialPort.ReadWrite):
                self.comboBox_PortName.addItem(info.portName())
                com.close()

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
        self.com.setPortName(comName)
        try:
            if self.com.open(QSerialPort.ReadWrite) == False:
                QMessageBox.critical(self, 'Fatal error', 'The serial port failed to be opened')
                return
        except:
            QMessageBox.critical(self, 'Fatal error', 'The serial port failed to be opened')
            return
        self.pushButton_ClosePort.setEnabled(True)
        self.pushButton_OpenPort.setEnabled(False)
        self.pushButton_Refresh.setEnabled(False)
        self.comboBox_PortName.setEnabled(False)
        self.comboBox_BaudRate.setEnabled(False)
        self.label_IsOpenOrNot.setText('  已打开')
        self.com.setBaudRate(comBaud)

    def Com_Close_Button_clicked(self):
        if self.com.isOpen():
            # 先暂停串口读取
            self.com.blockSignals(True)
            # 关闭串口
            self.com.close()
            print("Serial port closed")
            # 恢复串口读取
            self.com.blockSignals(False)
        else:
            print("Serial port is not open")

        self.pushButton_ClosePort.setEnabled(False)
        self.pushButton_OpenPort.setEnabled(True)
        self.pushButton_Refresh.setEnabled(True)
        self.comboBox_PortName.setEnabled(True)
        self.comboBox_BaudRate.setEnabled(True)
        self.label_IsOpenOrNot.setText('  已关闭')

    # def Com_Close_Button_clicked(self):
    #     if self.com.isOpen():
    #         self.com.close()
    #         print("Serial port closed")
    #     else:
    #         print("Serial port is not open")
    #
    #     self.pushButton_ClosePort.setEnabled(False)
    #     self.pushButton_OpenPort.setEnabled(True)
    #     self.pushButton_Refresh.setEnabled(True)
    #     self.comboBox_PortName.setEnabled(True)
    #     self.comboBox_BaudRate.setEnabled(True)
    #     self.label_IsOpenOrNot.setText('  已关闭')

    # def closeEvent(self, event):
    #     # Check if the serial port is open
    #     if self.com.isOpen():
    #         # Serial port is open, hide the window
    #         event.ignore()  # Ignore the close event
    #         QMessageBox.critical(self, 'Warning', 'The serial port keep opened',)
    #         self.hide()  # Hide the window
    #     else:
    #         # Serial port is not open, close the window
    #         event.accept()  # Accept the close event

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
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     #PortSelectDialog().listport()
#     mainWindow = PortSelectDialog()
#     mainWindow.show()
#     sys.exit(app.exec_())
