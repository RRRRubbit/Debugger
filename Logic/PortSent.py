import serial
import serial.tools.list_ports
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction, QFileDialog
from PyQt5.QtCore import  *
import os
from PyQt5.QtWidgets import QAction, QFileDialog
from PyQt5.QtCore import *
from Gui.ui_BreakPointDialog import *
from Gui.ui_MainWindow import *
from Gui.ui_PortSelect import *
from Logic.PortSent import *
from Logic.mainwindow import *

port_num="COM3"
portlist=""
class PortSelectDialog(QtWidgets.QDialog, Ui_Dialog_PortSelect):
    Selectedsignal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(PortSelectDialog, self).__init__(parent)
        self.setupUi(self)
        #self.listport()
    def PortSelect_show(self):
        ps = PortSelectDialog()
        ps.exec()

    def listport(self):
        # Get all serial device instances.
        # If no serial device is found, the output: "No serial device." ”
        # If a serial port device is found, the serial slogan and description corresponding to each device are output in turn.
        global portlist
        portlist= list(serial.tools.list_ports.comports())
        if len(portlist) <= 0:
            print("No serial device.")
        else:
            print("The available serial devices are as follows:")
            print(portlist)
            self.comboBox_PortSelect.clear()
            for i in range(0, len(portlist)):
                plist_0 = list(portlist[i])
                self.comboBox_PortSelect.addItem(str(plist_0[0]))
            print("Please choose one serial devices")

    def openport(self):
        # 调用函数接口打开串口时传入配置参数
        global port_num
        port_num = self.comboBox_PortSelect.currentText()
        #PortSent().listport()
        ser = serial.Serial(port_num,9600)  # Open COM1 and set the baud rate to 115200, with the default values for the rest of the parameters
        if ser.isOpen():  # Check whether the serial port is successfully opened
            print("The serial port",port_num," was opened successfully.")
            print(ser.name)  # Output serial port number
        else:
            print("Failed to open the serial port.")
        #port_num = ser.name
        # print(port_num)
        return ser.name
    #def choose_port(self):

    def send(self, message):

        ser = serial.Serial(port_num, 9600, timeout=1)
        ser.write(message)

    def receive(self):

        ser = serial.Serial(port_num, 9600)
        s = ser.read_until(expected="#".encode("utf-8")).decode("utf-8")
        if len(s) == 0 or s[-1] != "#":
            raise Exception("Could not get all register. Please reset and try again.")
        else:
            print(s)
        return s
    def upload51(filename):

        file = open(filename,"r")
        for line in file:
            PortSent.send(port_num,"{}\r".format(line.strip()).encode("utf-8"))
        a =file
        print(a)
        PortSent.send(port_num,a)
    def CleanBreakPoint(self):
        PortSent.send(port_num,"Bk0")
        PortSent.send(port_num, "Bk1")
        PortSent.send(port_num, "Bk2")
        PortSent.send(port_num, "Bk3")
        PortSent.send(port_num, "Bk4")
        PortSent.send(port_num, "Bk5")
        PortSent.send(port_num, "Bk6")
        PortSent.send(port_num, "Bk7")
        PortSent.send(port_num,"Bk8")
        PortSent.send(port_num, "Bk9")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PortSelectDialog().listport()


    mainWindow = PortSelectDialog()
    mainWindow.show()
    sys.exit(app.exec_())