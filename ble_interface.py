#!/usr/bin/python

import binascii
import struct
import time
import pygatt

#Start BLE Connection
pygatt.util.reset_bluetooth_controller()
bgn = pygatt.pygatt.BluetoothLEDevice('D4:A8:08:F5:B8:0D', 'hci1')
bgn.connect()


#Reads data out of incoming packets
#@profile
def _get_value(data):
    for i in range(10):
        if (int(data[i]) == 1):
            return data[ (i+3) ]


    return -1

#Reads incoming information from the rfduino
#@profile
def read_from_rf():
    i = 0;
    time.sleep(1)
    val = bgn.char_read_uuid(2221)
    while (i < 3):
        val = bgn.char_read_uuid(2221)
        if (len(val) > 0 and i > 0):
            #print('Hex Version: ', val)
            test_array = []
            for j in val:
                test_array.append(j)
        i += 1
        time.sleep(.1)
    print(' ')
    return _get_value(test_array)

#Caulatates Checksum before sendings commands to dynamixel.
def _calc_checksum(msg):
    checksum = 0
    for m in msg:
        checksum += m
    checksum = ( ~checksum ) % 256
    return [checksum]

#Recevices Max Torque Value from command line.
#Converts value to dynamixel syntax and sends the packet to rfduino.
def set_max_torque():
    val = raw_input("Enter Torque Percentage(0-100) Values > 40 can break cables: ")
    if not val.isdigit():
        print 'Invalid input'
        return
    torque_val = min(int(float(val)/100 * 1024), 1024)
    print("val:", torque_val)
    hi,lo = torque_val / 256, torque_val % 256
    set_torque = [255, 255, 1, 5, 3, 34, lo, hi]
    set_torque = set_torque + _calc_checksum(set_torque[2:])
    bgn.char_write(0x0011, bytearray(set_torque))

def print_commands():
    print(' ')
    print('     c,       Close the Hand')
    print('     o,       Open the Hand')
    print('     s,       Set Maximum Torue of Dynamixel')
    print('     1,       Turn Dynamixel LED On')
    print('     0,       Turn Dynamixel LED Off')
    print('     t,       Read the Temperature of Dynamixel')
    print('     l,       Read the Load of Dynamixel')
    print('     t,       Read the Position of Dynamixel')
    print('     quit,    Disconnect Bluetooth connection and end script')
    print('     help,    Print all commands')
    print(' ')


#Main control loop that recevies commands and interprets them.
def main():
    try:
        input_str = ''
        while input_str != 'quit':
            input_str = raw_input("Hand Control Enter Command: ")
        
            led_control = [255, 255, 1, 4, 3, 25, 1, 221] 
            led_control_off = [255, 255, 1, 4, 3, 25, 0, 222] 
            get_temp = [255, 255, 1, 4, 2, 43, 1, 204] 
            get_load = [255, 255, 1, 4, 2, 40, 2, 206]
            get_pos = [255, 255, 1, 4, 2, 36, 2, 210]
            close_h = [255, 255, 1, 5, 3, 30, 111, 11, 94]
            open_h = [255, 255, 1, 5, 3, 30, 36, 4, 176]
            set_torque = [255, 255, 1, 5, 3, 34, 0, 0, ]
            if (input_str == '1'):
                print("-----Turning the LED On-----")
                bgn.char_write(0x0011, bytearray(led_control))
            elif (input_str == '0'):
                print("-----Turning the LED Off-----")
                bgn.char_write(0x0011, bytearray(led_control_off))
            elif (input_str == 'l'):
                print("-----Reading the Load-----")
                bgn.char_write(0x0011, bytearray(get_load))    
                print 'Load: ' + str(read_from_rf())
            elif (input_str == 'p'):
                print("-----Reading the Position-----")
                bgn.char_write(0x0011, bytearray(get_pos))
                print 'Pos: ' + str(read_from_rf())
            elif (input_str == 't'):
                print("------Reading the Temp--------")
                bgn.char_write(0x0011, bytearray(get_temp))
                print 'Temp: ' + str(read_from_rf())
        
            elif (input_str == 'o'):
                print("------Opening the Hand--------")
                bgn.char_write(0x0011, bytearray(open_h))
            elif (input_str == 'c'):
                print("------Closing the Hand--------")
                bgn.char_write(0x0011, bytearray(close_h))
            elif (input_str == 's'):
                set_max_torque()
            elif (input_str == 'help'):
                print_commands()
    finally:
        bgn.stop()
main()



