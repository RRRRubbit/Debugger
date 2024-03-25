import threading

import serial.tools.list_ports
from time import sleep
import keyboard

class DetectPort:

    def check_valid_uart():
        ports_value = []
        ports_list = serial.tools.list_ports.comports()
        for i in range(len(ports_list)):
            ports_value.append(ports_list[i][0])
        print("ports_value is ", ports_value)

        if len(ports_value) == 0:
            print("无法找到串口.")
            self.comboBox_uart.clear()
            self.comboBox_uart.setCurrentIndex(-1)
        else:
            for i in range(len(ports_value)):
                index = self.comboBox_uart.findText(ports_value[i], qc.Qt.MatchFixedString)
                if index < 0:
                    self.comboBox_uart.addItem(ports_value[i])
                else:
                    print("当前串口为 ", self.comboBox_uart.currentText())


    # 开启监听线程
    def gui_status_thread():
        print("开始 gui_status_thread 线程.")
        while True:
            check_valid_uart()
            sleep(3)

if __name__ == "__main__":
    DetectPort.check_valid_uart()
    while True:
        # do something

        # 检测是否按下了esc键
        if keyboard.is_pressed('esc'):
            #break  # 退出循环
         quit()  # 退出程序