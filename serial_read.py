#!/usr/bin/python

import serial
import time
ser = serial.Serial("/dev/ttyUSB0", 9600)

while True:
    if ser.inWaiting():
        val = ser.readline(ser.inWaiting())
        print (val)
        #time.sleep(1)
