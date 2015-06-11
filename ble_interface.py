#!/usr/bin/python

import binascii
import struct
import time
from bluepy.bluepy.btle import UUID, Peripheral

temp_uuid = UUID(0x2221)
led_control = UUID(0x2222)
p = Peripheral("D4:A8:08:F5:B8:0D", "random")

def read_from_rf():
    ch = p.getCharacteristics(uuid=temp_uuid)[0]
    if (ch.supportsRead()):
        val = ch.read()
        print (val)
        val = binascii.b2a_hex(val)
        val = binascii.unhexlify(val)
        val = struct.unpack('f', val)[0]
        print str(val) + " deg C"

try:
    ch = p.getCharacteristics(uuid=led_control)[0]
    input_str = ""
    while input_str != "-1":
        input_str = raw_input("LED Control Enter 1 or 0: ")
        #val = struct.pack('f', float(input_str))
        #input_str = '\x13\0\0\0\x08\0'
        
        test_str = [1, 4, 5]
        #print(type(test_str))
        led_control = ['0000', '255', '255', '1', '4', '3', '25', '1', '221', '00000'] # '0000' Signal packet beginning and end for arduino;
        led_control_off = ['0000', '255', '255', '1', '4', '3', '25', '0', '222', '00000'] 
        get_temp = ['0000', '255', '255', '1', '4', '2', '43', '1', '204', '00000'] 
        if (input_str == '1'):
            for i in led_control:
                ch.write(i)
        elif (input_str == '0'):
            for i in led_control_off:
                ch.write(i)
        else:
            for i in get_temp:
                ch.write(i)
            read_from_rf()



        print("Command Written.")
finally:
    p.disconnect()
