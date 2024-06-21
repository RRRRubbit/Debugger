import binascii
import re
import sys
import serial
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTextEdit, QCheckBox

class ComReceiveThread(QThread):
    data_received = pyqtSignal(bytes)  # Define a signal to emit received data

    def __init__(self, com):
        super().__init__()
        self.com = com
        self.running = True

    def run(self):
        while self.running:
            if self.com.is_open:
                try:
                    rxData = bytes(self.com.read_all())
                    if rxData:
                        self.data_received.emit(rxData)

                except Exception as e:
                    print(f"Error: {e}")
                    self.running = False

    def stop(self):
        self.running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.textEdit_Receive = QTextEdit(self)
        self.checkBox_HexShow = QCheckBox('Hex Show', self)

        self.setCentralWidget(self.textEdit_Receive)

        self.com = serial.Serial('COM4', 9600, timeout=0.1, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)

        self.receive_thread = ComReceiveThread(self.com)
        self.receive_thread.data_received.connect(self.display_data)
        self.receive_thread.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.receive_thread.run)
        self.timer.start(100)

    def display_data(self, rxData):
        if self.checkBox_HexShow.isChecked():
            Data = binascii.b2a_hex(rxData).decode('ascii')
            hexStr = ' 0x'.join(re.findall('(.{2})', Data))
            hexStr = '0x' + hexStr
            self.textEdit_Receive.insertPlainText(hexStr + ' ')
        else:
            try:
                self.textEdit_Receive.insertPlainText(rxData.decode('UTF-8'))
            except UnicodeDecodeError:
                pass

    def closeEvent(self, event):
        self.receive_thread.stop()
        self.com.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
