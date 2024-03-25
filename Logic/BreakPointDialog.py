from PyQt5.QtWidgets import QAction, QFileDialog
from PyQt5.QtCore import *
from Gui.ui_BreakPointDialog import *
from Gui.ui_MainWindow import *
from Logic.PortSent import *

class BreakPointDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(BreakPointDialog, self).__init__(parent)
        self.setupUi(self)
       # self.cleanAllBreakPoints()
    # 连接语句
        self.lineEdit_00.returnPressed.connect(lambda current_text: self.textChanged_func(current_text))
        #self.lineEdit_00.setInputMask('HHHH;_'),self.lineEdit_01.setInputMask('HHHH;_'),self.lineEdit_02.setInputMask('HHHH;_')
    # 槽函数
    def cleanAllBreakPoints(self):
        PortSent.send(self,"bk1\n")
        return

    def textChanged_func(self, current_text):
        print("文本框内容变化信号", current_text)
        self.textBrowser.append("文本框内容变化信号" + current_text + '\n')

#
#
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     mainWindow = BreakPointDialog()
#     mainWindow.show()
#     sys.exit(app.exec_())


