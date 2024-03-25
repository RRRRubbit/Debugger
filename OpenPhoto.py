import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class fileDialogdemo(QWidget):
    def __init__(self,parent=None):
        super(fileDialogdemo, self).__init__(parent)

        #垂直布局
        layout=QVBoxLayout()

        #创建按钮，绑定自定义的槽函数，添加到布局中
        self.btn=QPushButton("Upload Hex File")
        self.btn.clicked.connect(self.gethex)
        layout.addWidget(self.btn)

        #创建标签，添加到布局中
        self.le=QLabel('')
        layout.addWidget(self.le)


        #设置主窗口的布局及标题
        self.setLayout(layout)
        self.setWindowTitle('File Dialog 例子')

    def gethex(self):
        #从C盘打开文件格式（*.jpg *.gif *.png *.jpeg）文件，返回路径
        hex_file,_=QFileDialog.getOpenFileName(self,'Open file','C:\\','hex files (*.hex)')

if __name__ == '__main__':
    app=QApplication(sys.argv)
    ex=fileDialogdemo()
    ex.show()
    sys.exit(app.exec_())
