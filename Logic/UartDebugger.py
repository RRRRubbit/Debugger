from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import time
from Gui.WinControl import Ui_WinControl
import sys
# from datetime import datetime
import serial
import serial.tools.list_ports
import threading


class MainWindow(QtWidgets.QMainWindow, Ui_WinControl):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        # 类内全局变量
        self.btn_sta = True  # 打开串口按钮状态标识
        self.g_bExit = False  # 线程是否退出状态标识
        self.g_SendFuncID = 0  # 通信查询功能标识
        self.g_ThrFlag = 0  # 线程运转摆动标志。

        # 串口无效
        self.ser = None
        self.send_num = 0
        self.receive_num = 0

        # 显示发送与接收的字符数量
        dis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
        # self.statusBar.showMessage(dis)

        # 刷新一下串口的列表
        self.refresh()
        # 波特率控件
        self.cmbBaudRate.addItem('115200')
        self.cmbBaudRate.addItem('57600')
        self.cmbBaudRate.addItem('56000')
        self.cmbBaudRate.addItem('38400')
        self.cmbBaudRate.addItem('19200')
        self.cmbBaudRate.addItem('14400')
        self.cmbBaudRate.addItem('9600')
        self.cmbBaudRate.addItem('4800')
        self.cmbBaudRate.addItem('2400')
        self.cmbBaudRate.addItem('1200')
        self.cmbBaudRate.setCurrentIndex(8)
        # 数据位控件
        self.cmbDataLen.addItem('8')
        self.cmbDataLen.addItem('7')
        self.cmbDataLen.addItem('6')
        self.cmbDataLen.addItem('5')

        # 停止位控件
        self.cmbStopBit.addItem('1')
        self.cmbStopBit.addItem('1.5')
        self.cmbStopBit.addItem('2')
        # 校验位控件
        self.cmbCheckBit.addItem('NONE')
        self.cmbCheckBit.addItem('ODD')
        self.cmbCheckBit.addItem('EVEN')
        # #对testEdit进行事件过滤
        # self.textBrowser.installEventFilter(self)
        # 实例化一个定时器
        self.timer = QTimer(self)
        self.timer_send = QTimer(self)
        # 定时器调用读取串口接收数据
        self.timer.timeout.connect(self.recv)
        # 定时发送
        self.timer_send.timeout.connect(self.send)
        # 发送数据按钮
        self.butSend_2.clicked.connect(self.send)
        #
        # 打开关闭串口按钮
        self.butOpenPort.clicked.connect(self.open_close)
        # 清除窗口
        self.butClear.clicked.connect(self.clear)

        # 连接向上键点击的事件
        self.pB_Up.pressed.connect(self.butUpPress)
        # 连接向上键释放事件
        self.pB_Up.released.connect(self.butRelease01)
        # 连接向下键点击事件
        self.pB_Down.pressed.connect(self.butDownPress)
        # 连接向下键释放事件
        self.pB_Down.released.connect(self.butRelease01)
        # 连接向左键点击事件
        self.pB_Left.pressed.connect(self.butLeftPress)
        # 连接向左键释放事件
        self.pB_Left.released.connect(self.butRelease01)
        # 连接向右键的点击事件
        self.pB_Right.pressed.connect(self.butRightPress)
        # 连接向右键释放事件
        self.pB_Right.released.connect(self.butRelease01)

        # 定时发送
        # self.checkBox_2.clicked.connect(self.send_timer_box)

    # 向右按钮被点击触发的事件
    def butRightPress(self):
        '''
        向右按钮被点击触发的事件，发送FF0100022F0032 ,云云台向左运动
        :return:
        '''
        input_s = 'FF0100022F0032'
        # 发送十六进制数据

        self.sendData(input_s)

    # 向左按钮被点击触发的事件
    def butLeftPress(self):
        '''
        向左按钮被点击时触发的事件，发送FF0100042F0034,云台向左运动
        :return:
        '''
        input_s = 'FF0100042F0034'
        # 发送十六进制数据
        self.sendData(input_s)

    # #向上按钮被按下触发的事件
    def butUpPress(self):
        '''
        向上按钮被按下触发的事件，发送FF010008002F38命令，云台向上运动
        :return:
        '''
        input_s = 'FF010008002F38'
        # 发送十六进制数据
        self.sendData(input_s)

    # #按钮弹起事件
    def butRelease01(self):
        '''
        向上按钮弹起触发事件。发送FF010000000001命令，云台停止转动
        :return:
        '''
        input_s = 'FF010000000001'
        # 发送十六进制数据
        self.sendData(input_s)

    # 向下南牛点击事件槽函数
    def butDownPress(self):
        '''
        向下按钮点击时触发的事件 发送FF010010002F40,云台向下运动
        :return:
        '''
        input_s = 'FF010010002F40'
        # 发送十六进制数据
        self.sendData(input_s)

    # 查询云台当前的垂直角
    def query_Vertical_Angle(self):
        '''
        查询云台当前的垂直角
        :return:
        '''
        self.g_SendFuncID = 2
        input_s = 'FF010053000054'
        # 发送十六进制数据
        self.sendData(input_s)

    # 查询云台当前的水平角度
    def query_Horizontal_Angle(self):
        '''
        查询云台当前的水平角度
        :return:
        '''
        self.g_SendFuncID = 1
        input_s = 'FF010052000052'
        self.sendData(input_s)

    # 刷新一下串口
    def refresh(self):
        # 查询可用的串口
        plist = list(serial.tools.list_ports.comports())

        if len(plist) <= 0:
            print("No used com!");
            # self.statusBar.showMessage('没有可用的串口')


        else:
            # 把所有的可用的串口输出到comboBox中去
            self.cmbPortNum.clear()

            for i in range(0, len(plist)):
                plist_0 = list(plist[i])
                self.cmbPortNum.addItem(str(plist_0[0]))

    # 事件过滤
    def eventFilter(self, obj, event):
        # 处理textEdit的键盘按下事件
        if event.type() == event.KeyPress:

            if self.ser != None:
                # 获取按键对应的字符
                char = event.text()

                num = self.ser.write(char.encode('utf-8'))
                self.send_num = self.send_num + num
                dis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
                self.statusbar.showMessage(dis)
            else:
                pass
            return True
        else:

            return False

    # 重载窗口关闭事件
    def closeEvent(self, e):

        # 关闭定时器，停止读取接收数据
        self.timer_send.stop()
        self.timer.stop()
        self.g_bExit = True  # 退出线程
        time.sleep(0.5)
        # 关闭串口
        if self.ser != None:
            self.ser.close()

    # # 定时发送数据
    # def send_timer_box(self):
    #     if self.checkBox_4.checkState():
    #         time = self.lineEdit_2.text()
    #
    #         try:
    #             time_val = int(time, 10)
    #         except ValueError:
    #             QMessageBox.critical(self, 'pycom', '请输入有效的定时时间!')
    #             return None
    #
    #         if time_val == 0:
    #             QMessageBox.critical(self, 'pycom', '定时时间必须大于零!')
    #             return None
    #         # 定时间隔发送
    #         self.timer_send.start(time_val)
    #
    #     else:
    #         self.timer_send.stop()
    #
    #     # 清除窗口操作
    def clear(self):
        self.textEdit.clear()
        self.send_num = 0
        self.receive_num = 0
        dis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
        self.statusBar.showMessage(dis)

    #
    # 串口接收数据处理
    def recv(self):
        '''
         串口接收数据处理
        :return:
        '''
        try:
            num = self.ser.inWaiting()
        except:

            self.timer_send.stop()
            self.timer.stop()
            # 串口拔出错误，关闭定时器
            self.ser.close()
            self.ser = None

            # 设置为打开按钮状态
            self.pushButton_2.setChecked(False)
            self.pushButton_2.setText("打开串口")
            print('serial error!')
            return None
        if (num > 0):
            # 有时间会出现少读到一个字符的情况，还得进行读取第二次，所以多读一个
            data = self.ser.read(num)

            # 调试打印输出数据
            # print(data)
            num = len(data)
            # 十六进制显示
            if self.checkBox_3.checkState():
                out_s = ''
                for i in range(0, len(data)):
                    out_s = out_s + '{:02X}'.format(data[i]) + ' '

                self.textEdit.insertPlainText(out_s)

            else:
                # 串口接收到的字符串为b'123',要转化成unicode字符串才能输出到窗口中去
                self.textEdit.insertPlainText(data.decode('iso-8859-1'))

            # 统计接收字符的数量
            self.receive_num = self.receive_num + num
            dis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
            self.statusbar.showMessage(dis)

            ################当发送一个次读取云台水平角度和垂直角度的时候，对反回的数据进行处理
            if (self.receive_num >= 14 and self.g_SendFuncID == 1):  # 查询水平角度接受到的数据处理
                self.label_Vertical.setText(data.decode('iso-8859-1'))
                self.receive_num = 0  # 接收完一个被查询数据后接收数量清零。
            elif (self.receive_num >= 14 and self.g_SendFuncID == 2):  # 查询垂直角度接收到的数据处理
                self.label_Horizontal.setText(data.decode('iso-8859-1'))
                self.receive_num = 0  # 接收完一个被查询数据后接收数量清零。
            ###########################

            # 获取到text光标
            textCursor = self.textEdit.textCursor()
            # 滚动到底部
            textCursor.movePosition(textCursor.End)
            # 设置光标到text中去
            self.textEdit.setTextCursor(textCursor)
        else:
            pass

    # 串口发送数据处理
    def send(self):
        if self.ser != None:
            input_s = self.lineEdit_Send.text()
            if input_s != "":

                # 发送字符
                if (self.checkBox_3.checkState() == False):
                    # if self.checkBox_2.checkState():
                    # 发送新行
                    input_s = input_s + '\r\n'
                    input_s = input_s.encode('utf-8')

                else:
                    # 发送十六进制数据
                    input_s = input_s.strip()  # 删除前后的空格
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)

                        except ValueError:
                            print('input hex data!')
                            QMessageBox.critical(self, 'pycom', '请输入十六进制数据，以空格分开!')
                            return None

                        input_s = input_s[2:]
                        input_s = input_s.strip()

                        # 添加到发送列表中
                        send_list.append(num)
                    input_s = bytes(send_list)
                print(input_s)
                # 发送数据
                try:
                    num = self.ser.write(input_s)
                except:

                    self.timer_send.stop()
                    self.timer.stop()
                    # 串口拔出错误，关闭定时器
                    self.ser.close()
                    self.ser = None

                    # 设置为打开按钮状态
                    self.pushButton_2.setChecked(False)
                    self.pushButton_2.setText("打开串口")
                    print('serial error send!')
                    return None

                self.send_num = self.send_num + num
                dis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
                self.statusbar.showMessage(dis)
                # print('send!')
            else:
                print('none data input!')

        else:
            # 停止发送定时器
            self.timer_send.stop()
            QMessageBox.critical(self, 'pycom', '请打开串口')

    # 发送数据的通用函数
    def sendData(self, Data, isHex=True):
        '''
        :param Data: 需要发送的数据集
        :param isHex: 是否用十六进制发送或者用字符串发送，默认为十六进制
        :return: 无
        '''
        if self.ser != None:
            input_s = Data
            if input_s != "":

                # 发送字符
                if (isHex == False):
                    # if self.checkBox_2.checkState():
                    # 发送新行
                    input_s = input_s + '\r\n'
                    input_s = input_s.encode('utf-8')

                else:
                    # 发送十六进制数据
                    input_s = input_s.strip()  # 删除前后的空格
                    send_list = []
                    while input_s != '':
                        try:
                            num = int(input_s[0:2], 16)

                        except ValueError:
                            print('input hex data!')
                            QMessageBox.critical(self, 'pycom', '请输入十六进制数据，以空格分开!')
                            return None

                        input_s = input_s[2:]
                        input_s = input_s.strip()

                        # 添加到发送列表中
                        send_list.append(num)
                    input_s = bytes(send_list)
                print(input_s)
                # 发送数据
                try:
                    num = self.ser.write(input_s)
                except:

                    self.timer_send.stop()
                    self.timer.stop()
                    # 串口拔出错误，关闭定时器
                    self.ser.close()
                    self.ser = None

                    # 设置为打开按钮状态
                    self.open_close().setChecked(False)
                    self.open_close.setText("打开串口")
                    print('serial error send!')
                    return None

                self.send_num = self.send_num + num
                dis = '发送：' + '{:d}'.format(self.send_num) + '  接收:' + '{:d}'.format(self.receive_num)
                self.statusbar.showMessage(dis)
                print('send!')
            else:
                print('none data input!')

        else:
            # 停止发送定时器
            self.timer_send.stop()
            QMessageBox.critical(self, 'pycom', '请打开串口')

    # 打开关闭串口
    def open_close(self):

        if self.btn_sta == True:
            try:
                # 输入参数'COM13',115200
                print(int(self.cmbBaudRate.currentText()))
                self.ser = serial.Serial(self.cmbPortNum.currentText(), int(self.cmbBaudRate.currentText()),
                                         timeout=0.1)
            except:
                QMessageBox.critical(self, 'pycom', '没有可用的串口或当前串口被占用')
                return None
            # 字符间隔超时时间设置
            self.ser.interCharTimeout = 0.001
            self.g_bExit = False
            try:
                hThreadHandle = threading.Thread(target=self.work_thread, args=())  # 声明雷内线程变量
                hThreadHandle.start()
            except:
                print("error: unable to start thread")
            # 1ms的测试周期
            self.timer.start(2)
            self.butOpenPort.setText("关闭串口")
            self.btn_sta = False
            print('open!')
        else:
            # 关闭定时器，停止读取接收数据
            self.timer_send.stop()
            self.timer.stop()
            self.g_bExit = True  # 退出线程循环的标志。
            time.sleep(0.5)
            try:
                # 关闭串口
                self.ser.close()
            except:
                QMessageBox.critical(self, 'pycom', '关闭串口失败')
                return None

            self.ser = None

            self.butOpenPort.setText("打开串口")
            self.btn_sta = True
            print('close!')

    # 监控云台当前坐标的线程
    def work_thread(self):
        '''
        监控云台当前坐标的线程函数
        :return:
        '''
        # 循环内不停的读取云台坐标。
        while True:
            time.sleep(0.3)  # 每隔0.2秒查询一次
            if (self.g_ThrFlag == 0):
                self.query_Vertical_Angle()
                self.g_ThrFlag = 1
            elif (self.g_ThrFlag == 1):
                self.query_Horizontal_Angle()
                self.g_ThrFlag = 0

            if self.g_bExit == True:
                break


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())