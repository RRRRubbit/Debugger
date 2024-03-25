from Gui.ui_MainWindow import  Ui_MainWindow
from Gui import BreakPointDialog
import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets




if __name__ == '__main__':

        import sys

        app = QtWidgets.QApplication(sys.argv)
        widgets = QtWidgets.QMainWindow()
        ui = Debugger51(widgets)
        #ui.setupUi(widgets)
        widgets.show()
        sys.exit(app.exec_())