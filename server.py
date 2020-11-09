import serial
from parse import *
ser = serial.Serial('COM4')  # open serial port
speed = 100
while True:
    line = ser.readline().decode("utf-8")
    r = parse("{index}", line)
    index = int(r['index'])
    print(index)

    ser.write('{}\n'.format(speed).encode())

