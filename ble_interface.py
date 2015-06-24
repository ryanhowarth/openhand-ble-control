#!/usr/bin/python

import binascii
import struct
import time
import pygatt




#This class interfaces with a RFduino over BLE to Control an Openhand
#using a Dynamixel servo.
class BLE_Hand_Control():

    servo_id = [1] #default
    max_torque = 0.3
    ble = None
    
    #Commands supported by this class.
    led_on = [3, 25, 1] 
    led_off = [3, 25, 0] 
    temperature = [2, 43, 1] 
    load = [2, 40, 2]
    position = [2, 36, 2]
    close_hand = [3, 30, 111, 11]
    open_hand = [3, 30, 36, 4]
    set_torque = [3, 34, 0, 0]
    set_torque_eeprom = [3, 14, 0, 0]
    def __init__(self, mac_addr = 'D4:A8:08:F5:B8:0D', dev = 'hci1'):
        #Start BLE Connection.
        pygatt.util.reset_bluetooth_controller()
        self.ble = pygatt.pygatt.BluetoothLEDevice(mac_addr, dev)
        self.ble.connect()


    #Reads data out of incoming packets.
    #@profile
    def _get_value(self, data):
        for i in range(10):
            if (int(data[i]) == 1):
                return data[ (i+3) ]
        return -1

    #Reads incoming information from the rfduino.
    #@profile
    def read_from_rf(self):
        i = 0;
        time.sleep(1)
        val = self.ble.char_read_uuid(2221)
        while (i < 3):
            val = self.ble.char_read_uuid(2221)
            if (len(val) > 0 and i > 0):
                test_array = []
                for j in val:
                    test_array.append(j)
            i += 1
            time.sleep(.1)
        print(' ')
        return self._get_value(test_array)

    #Caulatates Checksum before sendings commands to dynamixel.
    def _calc_checksum(self, msg):
        checksum = 0
        for m in msg:
            checksum += m
        checksum = ( ~checksum ) % 256
        return [checksum]

    #Recevices Max Torque Value from command line.
    #Converts value to dynamixel syntax and sends the packet to rfduino.
    def set_max_torque(self, val):
        if not val.isdigit():
            print 'Invalid input'
            return
        
        torque_val = min(int(float(val)/100 * 1024), 1024) #percentage to dynamixel scale (0 - 1024)
        hi,lo = torque_val / 256, torque_val % 256
        self.set_torque[2:4] = [lo, hi]
        self.set_torque_eeprom[2:4] = [lo, hi]
        self.send_packet(self.set_torque)
        self.send_packet(self.set_torque_eeprom)
    
    #Takes command and appends the start address, servo ID, and checksum.
    #Then sends it to the rf duino
    def send_packet(self, command):
        start_address = [255, 255]
        cmd_length = [len(command) + 1]
        packet = start_address + self.servo_id + cmd_length + command
        packet = packet + self._calc_checksum(packet[2:])
        self.ble.char_write(0x0011, bytearray(packet))

    #Prints all possible commands to command line.
    def print_commands(self):
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

#Main control loop that recevies commands from command line and interprets them.
    def main(self):
        try:
            input_str = ''
            while input_str != 'quit':
                input_str = raw_input("Hand Control Enter Command: ") 
                if (input_str == '1'):
                    print("-----Turning the LED On-----")
                    self.send_packet(self.led_on)
                elif (input_str == '0'):
                    print("-----Turning the LED Off-----")
                    self.send_packet(self.led_off)
                elif (input_str == 'l'):
                    print("-----Reading the Load-----")
                    self.send_packet(self.load)
                    print 'Load: ' + str(self.read_from_rf())
                elif (input_str == 'p'):
                    print("-----Reading the Position-----")
                    self.send_packet(self.position)
                    print 'Pos: ' + str(self.read_from_rf())
                elif (input_str == 't'):
                    print("------Reading the Temp--------")
                    self.send_packet(self.temperature)
                    print 'Temp: ' + str(self.read_from_rf())
            
                elif (input_str == 'o'):
                    print("------Opening the Hand--------")
                    self.send_packet(self.open_hand)
                elif (input_str == 'c'):
                    print("------Closing the Hand--------")
                    self.send_packet(self.close_hand)
                elif (input_str == 's'):
                    val = raw_input("Enter Torque Percentage(0-100) Values > 40 can break cables: ")
                    self.set_max_torque(val)
                elif (input_str == 'help'):
                    self.print_commands()
        finally:
            self.ble.stop()

x = BLE_Hand_Control()
x.main()

