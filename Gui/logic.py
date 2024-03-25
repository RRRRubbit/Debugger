# -*- coding: utf-8 -*-
# @Time    : 2021/4/2 22:23
# @Author  : Zeeland
# @File    : FunEdit.py
# @Software: PyCharm

from PyQt5.QtWidgets import QWidget,QApplication,QFileDialog,QMessageBox
from UiForm import Ui_Form
import sys,time
import Gui.untitled


def gethex(self):
    # 从C盘打开文件格式（*
    # hex_file, _=
    print("ok")

class FunEdit(QWidget,Ui_Form):
    '''
    初始化各方面信息
    '''
    def __init__(self):
        super(FunEdit, self).__init__()
        self.setupUi(self)#Ui初始化
        self.init()

    '''
    该方法用于信号与槽的绑定
    '''
    def init(self):
        self.btn_readMusic.clicked.connect(self.readMusic)
        self.btn_play.clicked.connect(self.start)
        self.btn_pause.clicked.connect(self.pause)

    '''
    读取音频
    '''
    def readMusic(self):
        #读取特定格式的文件,传入一个self,"标题名","初始显示文件夹的路径","特定格式(以两个分号区分)"
        #该方法返回一个Tuple,分别为str类型的路径名和file的type(eg:MP3)
        self.fdir,self.ftype =QFileDialog.getOpenFileName(self,"Open File","","Mp3(*.mp3);;Wav(*.wav)")

        # 判断是否为空路径，如果为空路径，则不能加载音频，否则会闪退
        if self.fdir=="":
            print("没有选择文件")
            return

        print(self.fdir)
        pygame.init()#初始化音乐播放装置，初始化后才可以使用
        self.track =pygame.mixer.music.load(str(self.fdir))#加载音频文件(放入缓存池)
        self.label_MusicMessage.setText(str(self.fdir))


    '''
    播放
    '''
    def start(self):
        if self.label_MusicMessage.text()=='暂无':
            QMessageBox.about(self,'message','当前暂无播放的音乐')
            return
        pygame.mixer.music.play()#播放


    '''
    停止播放
    '''
    def pause(self):
        if self.label_MusicMessage.text()=='暂无':
            QMessageBox.about(self,'message','当前暂无播放的音乐')
            return
        pygame.mixer.music.stop()#暂停
        self.label_MusicMessage.setText("暂停中")


'''
主方法运行入口
'''
if __name__ == '__main__':
    untitled
