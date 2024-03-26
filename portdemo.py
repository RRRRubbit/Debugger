from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QAction, QFileDialog, QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal
import os
import serial
from Gui.ui_MainWindow import Ui_MainWindow
from Gui.ui_PortSelect import Ui_Dialog_PortSelect
from Logic.BreakPointDialog import BreakPointDialog
from OpenPhoto import PortSelectDialog

from PyQt5.QtSerialPort import QSerialPortInfo

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sign_one = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.actionUpdateregister.triggered.connect(self.get_register)
        self.actionOpen.triggered.connect(self.gethex)
        self.actionLoad.triggered.connect(self.upload)
        self.actionStep_Run.triggered.connect(self.set_register)
        self.actionList_Port.triggered.connect(self.PortSelect_show)
        self.actionMake_BreakPoint.triggered.connect(self.BreakPointDialog_show)

        # Initialize serial manager
        self.serial_manager = PortSelectDialog()

    def closeEvent(self, event):
        # Close serial port when the main window is closed
        self.serial_manager.close_port()
        event.accept()

    def PortSelect_show(self):
        ps = PortSelectDialog()
        ps.exec()

    def BreakPointDialog_show(self):
        bk = BreakPointDialog()
        bk.show()

    def gethex(self):
        # From disk open file format（*.hex），return dir
        s, _=QFileDialog.getOpenFileName(None, 'Open a hex file', 'C:\\', 'hex files (*.hex)')
        if s == "":
            print("> > > Successful: File '{}' is not found".format(s))
        else:
            print("Successful: File '{}' is open".format(s))
        return s

    def upload(self):
        hexfile_dir = self.gethex()
        if hexfile_dir:
            self.serial_manager.upload51(hexfile_dir)

    def get_register(self):
        self.serial_manager.send("X\r".encode("utf-8"))
        s = self.serial_manager.receive()
        if len(s) == 0 or s[-1] != "#":
            raise Exception("Could not get all register. Please reset and try again.")
        else:
            self.set_register(s)

    def set_register(self, message):
        message = message.replace('\r', '').replace('<\r>', '').replace('<\n>', '\n').replace('C:', '')
        self.label.setText(message)

    def set_RAM(self):
        pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
