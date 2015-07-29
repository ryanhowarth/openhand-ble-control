#!/usr/bin/python

import binascii
import struct
import time
import photon_tcp_socket_server as tcp 



#This class interfaces with a RFduino over BLE to Control an Openhand
#using a Dynamixel servo.
class openhand_control():

    servo_id = [1] #default
    max_torque = 0.3
    tcp_client = [] 
     
    #Commands supported by this class.
    led_on = [3, 25, 1] 
    led_off = [3, 25, 0] 
    temperature = [2, 43, 1] 
    load = [2, 40, 2]
    position = [2, 36, 2]
    speed = [2, 38, 2]
    #close_hand = [3, 71, 100, 5]
    close_hand = [3, 30, 0, 7]
    open_hand = [3, 30, 0, 1]
    set_torque = [3, 34, 0, 0]
    set_torque_eeprom = [3, 14, 0, 0]
    
    def __init__(self, port=1234, local_ip='192.168.0.105'):
        #Start wifi connection.
        self.tcp_client = tcp.photon_tcp_socket_server()

    #Reads data out of incoming packets.
    #@profile
    def _get_value(self, data):
        for i in range(8):
            if (int(data[i]) == 1):
                return data[ (i+3) ]
        return -1

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
        print (packet)
        print (str(packet))
        return self.tcp_client.send(packet)

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
        print('     v,       Read the Speed of Dynamixel')
        print('     close,   Close connection between clients. (TCP Server continues to run and listen for clients.)')
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
                    return_packet = self.send_packet(self.load)
                    print 'Load: ' + str(self._get_value(return_packet))
                elif (input_str == 'p'):
                    print("-----Reading the Position-----")
                    return_packet = self.send_packet(self.position)
                    print 'Pos: ' + str(self._get_value(return_packet))
                elif (input_str == 't'):
                    print("------Reading the Temp--------")
                    return_packet = self.send_packet(self.temperature)
                    print 'Temp: ' + str(self._get_value(return_packet))
                elif (input_str == 'v'):
                    print("------Reading the Speed--------")
                    return_packet = self.send_packet(self.speed)
                    print 'Speed: ' + str(self._get_value(return_packet))
            
                elif (input_str == 'o'):
                    print("------Opening the Hand--------")
                    self.send_packet(self.open_hand)
                elif (input_str == 'c'):
                    print("------Closing the Hand--------")
                    self.send_packet(self.close_hand)
                elif (input_str == 's'):
                    val = raw_input("Enter Torque Percentage(0-100) Values > 40 can break cables: ")
                    self.set_max_torque(val)
                elif (input_str == 'close'):
                    self.tcp_client.close_connection()
                elif (input_str == 'help'):
                    self.print_commands()
        finally:
            self.tcp_client.close_server()


x = openhand_control()
x.main()

