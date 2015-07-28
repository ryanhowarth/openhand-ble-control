#!/usr/bin/python

import socket
import time
import datetime






class Photon_TCP_Socket_Server():



    s = []
    conn = []
    addr = []

    def __init__(self, port=1234, local_ip='192.168.0.105'):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        self.s.bind((local_ip, port))
        print ''
        print 'Opened TCP Socket on port:', port, '. Listening for clients: '
        self.s.listen(5)

    def main(self):
        while 1:
            self.conn, self.addr = self.s.accept()
            print 'Got connection from', self.addr
            input_str = ""
            while (input_str != 'q'):
                input_str = raw_input('Enter Message: ')
                a2 = time.time()
                self.conn.send(input_str)
                msg = self.conn.recv(1024)
                b2 = time.time()
                c2 = b2 - a2
                print 'msg: ', msg
                print "Ping time in seconds (Method #2): ", (c2)


x = Photon_TCP_Socket_Server()
x.main()
