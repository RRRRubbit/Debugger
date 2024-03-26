import re
import sys
import binascii
import time
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from Gui.ui_PortSelect import Ui_Dialog_PortSelect  # Import the UI file

class PortSelectDialog(QDialog, Ui_Dialog_PortSelect):
    def __init__(self, parent=None):
        super(PortSelectDialog, self).__init__(parent)
        self.setupUi(self)

        # Create a SerialManager instance
        self.serial_manager = self.SerialManager()

        # Populate ComboBox with available ports
        self.populate_ports()

        # Connect signals to slots
        self.pushButton_OpenPort.clicked.connect(self.open_port)
        self.pushButton_ClosePort.clicked.connect(self.close_port)
        self.pushButton_Send.clicked.connect(self.send_data)
        self.pushButton_Refresh.clicked.connect(self.refresh_ports)
        self.checkBox_HexSend.stateChanged.connect(self.hex_sending_clicked)
        self.checkBox_HexShow.stateChanged.connect(self.hex_showing_clicked)

        # Create a timer for updating time display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_time)
        self.timer.start(1000)

    def populate_ports(self):
        # Clear the ComboBox
        self.comboBox_PortName.clear()

        # Get available serial ports
        available_ports = QSerialPortInfo.availablePorts()

        # Add port names to the ComboBox
        for port_info in available_ports:
            self.comboBox_PortName.addItem(port_info.portName())

    def open_port(self):
        port_name = self.comboBox_PortName.currentText()
        baud_rate = int(self.comboBox_BaudRate.currentText())
        self.serial_manager.open_port(port_name, baud_rate)

    def close_port(self):
        self.serial_manager.close_port()

    def show_time(self):
        current_time = time.strftime("%B %d, %H:%M:%S", time.localtime())
        self.label_Time.setText(current_time)

    def send_data(self):
        self.serial_manager.send_data(self.textEdit_Send.toPlainText(), self.checkBox_HexSend.isChecked())

    def refresh_ports(self):
        self.populate_ports()

    def hex_showing_clicked(self):
        if self.checkBox_HexShow.isChecked():
            self.textEdit_Receive.insertPlainText('\n')

    def hex_sending_clicked(self):
        pass  # You can add logic here if needed

    class SerialManager:
        def __init__(self):
            self.serial_port = QSerialPort()

        def open_port(self, port, baudrate):
            if not self.serial_port.isOpen():
                self.serial_port.setPortName(port)
                self.serial_port.setBaudRate(baudrate)
                if self.serial_port.open(QSerialPort.ReadWrite):
                    print("Serial port opened")
                    self.serial_port.readyRead.connect(self.receive_data)
                else:
                    print("Failed to open serial port")

        def close_port(self):
            if self.serial_port.isOpen():
                self.serial_port.close()
                print("Serial port closed")

        def send_data(self, data, is_hex):
            if self.serial_port.isOpen():
                if is_hex:
                    try:
                        hex_data = bytes.fromhex(data)
                        self.serial_port.write(hex_data)
                    except ValueError:
                        QMessageBox.critical(None, 'Error', 'Invalid hexadecimal string!')
                else:
                    self.serial_port.write(data.encode())

        def receive_data(self):
            if self.serial_port.isOpen():
                rx_data = self.serial_port.readAll()
                self.handle_received_data(rx_data)

        def handle_received_data(self, data):
            # Handle received data here
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = PortSelectDialog()
    dialog.show()
    sys.exit(app.exec_())
