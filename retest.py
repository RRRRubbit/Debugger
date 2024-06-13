# -*- coding: utf-8 -*-


from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QPushButton, QMainWindow, QProgressDialog
import time
from PyQt5 import QtCore, QtWidgets
import sys


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(722, 362)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout.setObjectName("formLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.pushButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 722, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBar)
        self.toolBar_2 = QtWidgets.QToolBar(MainWindow)
        self.toolBar_2.setObjectName("toolBar_2")
        MainWindow.addToolBar(QtCore.Qt.RightToolBarArea, self.toolBar_2)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "PushButton"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.toolBar_2.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.pushButton.clicked.connect(self.progress)

    def progress(self):
        global global_jindu
        global_jindu = 0
        try:
            self.progress_bar = progre()  # 该progre线程开启后不再关闭，后续只对其初始化
        except:
            pass
        self.progress_bar.start()  # 初始化progre线程，令进度为0
        self.work = working()
        self.work.start()
        self.find_jindu = find_jindu()
        self.find_jindu.start()
        self.find_jindu.sinOut.connect(self.update)  # 接收到信号并执行update

    def update(self, s):
        s = int(eval(s))
        print(s)
        self.progress_bar.progress.setValue(s)


class progre(QThread):  # 创建线程类
    def __init__(self):
        super(progre, self).__init__()
        self.progress = QProgressDialog('', '', 0, 0, MainWindow)
        self.progress.setFixedSize(400, 200)
        self.progress.setWindowTitle('处理中')
        self.progress.setLabelText('当前进度值')
        self.progress.setCancelButtonText('取消')
        self.progress.setRange(0, 100)
        self.progress.canceled.connect(lambda: print('进度对话框被取消'))
        self.progress.setAutoClose(True)  # value为最大值时自动关闭

    def run(self):  # 重写run，为了第二次启动时初始化做准备
        self.progress.setValue(0)


class working(QThread):
    def __init__(self):
        super(working, self).__init__()

    def run(self):
        for i in range(1, 100 + 1):
            time.sleep(0.2)
            global global_jindu
            global_jindu = i


class find_jindu(QThread):
    sinOut = pyqtSignal(str)  # 定义自定义信号

    def __init__(self):
        super(find_jindu, self).__init__()

    def run(self):
        while True:
            time.sleep(0.1)
            global global_jindu
            self.sinOut.emit(str(global_jindu))  # 向主线程发送信号
            if global_jindu == 100:
                print("break")
                break
        return


global_jindu = 0
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
MainWindow.show()

sys.exit(app.exec())