#!/usr/bin/python

import socket
import time
import datetime
import threading





class photon_tcp_socket_server():

    s = []
    addr = []
    conn = []
    led_on = [255, 255, 1, 4, 3, 25, 1, 221]
    led_off = [255, 255, 1, 4, 3, 25, 0, 222]
    get_temp = [255, 255, 1, 4, 2, 43, 1, 204] 
    connected = True
    def __init__(self, port=1234, local_ip='192.168.0.105'):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.s.bind((local_ip, port))
        print ''
        print 'Opened TCP Socket on port:', port,'. Listening for clients: '
        self.s.listen(5)
        self.connect()

    def connect(self):
        while True:
            self.conn, self.addr = self.s.accept()
            print 'Got connection from', self.addr
            connected = True
            return
    
    def close_connection(self):
        self.conn.close()
        print 'Closing the connection.'
        print ''
        print 'Listening for clients: '
        self.connect()

    def close_server(self):
        print 'Closing the TCP Server'
        self.s.close()
    
    def send(self, msg):
        
        try:
            if not self.connected:
                return False
            self.conn.send(bytearray(msg))
            time.sleep(0.1) #pause to allow dyanmixel to send message back
            recv_array = self.conn.recv(1024)
            recv_array = [ord(i) for i in recv_array]
            print recv_array
            return recv_array
        except:
            print 'Inspect if gets here'
    
    def run(self, msg):
        input_str = raw_input('Enter Message: ')
        try:
            while (input_str != 'q'):
                if (input_str == '1'):
                    conn.send(bytearray(self.led_on))
                elif (input_str == 't'):
                    conn.send(bytearray(self.get_temp))
                else:
                    conn.send(bytearray(self.led_off))
                time.sleep(0.1) #pause to allow dyanmixel to send message back
                print 'Attempting to receive return packet.'
                msg = conn.recv(1024)
                for i in msg:
                    print ord(i)
                print 'msg: ', msg
                input_str = raw_input('Enter Message: ')
        finally:
            #conn.send('0')
            #conn.close()
            print 'Closing the connection.'
            conn.close()
            print ''
            print 'Listening for another client: '



#x = photon_tcp_socket_server()
#x.run()








