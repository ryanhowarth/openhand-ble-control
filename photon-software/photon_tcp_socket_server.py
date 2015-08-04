#!/usr/bin/python

import socket
import time
import datetime
import select



class photon_tcp_socket_server():

    s = []
    addr = []
    conn = []
    ready_to_recv = []
    timeout_in_seconds = 1000
    connected = False
    def __init__(self, port=1234, local_ip='192.168.0.105'):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Initialize socket server
        self.s.setblocking(0) #Set to non blocking. Send and recv calls will throw error if not immediately availible
        self.s.bind((local_ip, port))
        print ''
        print 'Opened TCP Socket on port:', port,'. Listening for clients: '
        self.s.listen(5)
        self.connect()

    #@profile
    def connect(self):
        self.ready_to_recv = select.select([self.s], [], [], self.timeout_in_seconds)
        while True:
            if self.ready_to_recv[0]:
                self.conn, self.addr = self.s.accept()
                self.connected = True
                print 'Got connection from', self.addr
                return
    
    #@profile
    def close_connection(self):
        self.conn.close()
        self.connected = False
        print 'Closing the connection.'
        print ''
        print 'Listening for clients: '
        self.connect()

    #@profile
    def close_server(self):
        print 'Closing the TCP Server'
        self.s.shutdown(socket.SHUT_RDWR)
        self.s.close()
    
    #@profile
    def send(self, msg):
        
        #try:
        if not self.connected:
            return False
        self.conn.send(bytearray(msg))
        return self._receive()
    
    #@profile
    def _receive(self):
        done = False
        recv_array = []
        if self.ready_to_recv[0]:
            recv_array = self.conn.recv(1024)
        while not done:
            #print 'len recv: ', len(recv_array)
            if (len(recv_array) < 6):    
                if self.ready_to_recv[0]:
                    recv_array += self.conn.recv(1024)
            elif (len(recv_array) < ( ord(recv_array[3])) + 4 ):
                if self.ready_to_recv[0]:
                    a = [ord(i) for i in recv_array]
                    print 'recv_array in + 4: ', a
                    recv_array += self.conn.recv(1024)
                
            else:
                print 'ord(recv_array[3]): ', ord(recv_array[3])
                done = True
            #print recv_array
        recv_array = [ord(i) for i in recv_array]
        print recv_array
        return recv_array  




