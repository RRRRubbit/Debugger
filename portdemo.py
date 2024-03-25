import serial


def sendmessage(ser, message):
    ser = serial.Serial('COM1', 9600, timeout=1)
    ser.write(message)

if __name__ == '__main__':
    sendmessage('COM1', '0x03\n'.encode("utf-8"))
    exit(1)