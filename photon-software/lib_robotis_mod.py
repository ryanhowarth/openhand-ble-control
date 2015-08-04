#!/usr/bin/python
# Copyright (c) 2009, Georgia Tech Research Corporation
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Georgia Tech Research Corporation nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY GEORGIA TECH RESEARCH CORPORATION ''AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL GEORGIA TECH BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

## Controlling Robotis Dynamixel RX-28 & RX-64 servos from python
## using the Particle Photon Wifi Microcontroller.

## Authors: Travis Deyle, Advait Jain & Marc Killpack (Healthcare Robotics Lab, Georgia Tech.)

##MOD VERSION: 2013, some additional modifications made to make appropriate for both MX/RX series (Raymond R. Ma)

##MOD Version 2015, Added class to interface with Particle Photon Microcontroller (Ryan Howarth).
import serial
import time
import thread
import sys, optparse
import os
import math
import photon_tcp_socket_server as tcp 


#Not used any more. Replaced by photon device class.
class USB2Dynamixel_Device():
    ''' Class that manages serial port contention between servos on same bus
    '''
    def __init__( self, dev_name = '/dev/ttyUSB0', baudrate = 9600 ):
        print("Baudrate: " + str(baudrate)) #Added by Ryan for debugging
        print("Device Name: " + dev_name)   #Added by Ryan for debugging
        
        ''' Commented out code below stores the device name incorrectly on Ubuntu 12.04. 
            Gives runtime error: "Could not find ID on bus" later on in program. -Ryan 5/15/15
        ''' 
        try:
            self.dev_name = string.atoi( dev_name ) # stores the serial port as 0-based integer for Windows
        except:
            self.dev_name = dev_name # stores it as a /dev-mapped string for Linux / Mac
        #if os.name == 'posix':
        #    self.dev_name = dev_name # stores it as a /dev-mapped string for Linux / Mac
        #else:
        #    self.dev_name = string.atoi( dev_name ) # stores the serial port as 0-based integer for Windows

        self.mutex = thread.allocate_lock()	#helps ensure that only a single port is used?
        self.servo_dev = None

        self.acq_mutex()
        self._open_serial( baudrate )
        self.rel_mutex()

    def acq_mutex(self):
        self.mutex.acquire()

    def rel_mutex(self):
        self.mutex.release()

    def send_serial(self, msg):
        # It is up to the caller to acquire / release mutex
        self.servo_dev.flushInput()		#added to remove extra bytes from input buffer
        print ('Send Serial: ' , msg, type(msg)) 
        self.servo_dev.write( msg )

    def read_serial(self, nBytes=1):
        # It is up to the caller to acquire / release mutex
        rep = self.servo_dev.read( nBytes )
        #print ('Read Serial: ' , rep, type(rep)) 
        return rep

    def _open_serial(self, baudrate):
        try:
            self.servo_dev = serial.Serial(self.dev_name, baudrate, timeout=1.0)
            # Closing the device first seems to prevent "Access Denied" errors on WinXP
            # (Conversations with Brian Wu @ MIT on 6/23/2010)
            self.servo_dev.close()  
            self.servo_dev.setParity('N')
            self.servo_dev.setStopbits(1)
            self.servo_dev.open()

            self.servo_dev.flushOutput()
            self.servo_dev.flushInput()

        except (serial.serialutil.SerialException), e:
            raise RuntimeError('lib_robotis: Serial port not found!\n')
        if(self.servo_dev == None):
            raise RuntimeError('lib_robotis: Serial port not found!\n')


#Class to send and read to photon device. Tcp connection should not be shared 
class Photon_Device():

    tcp_client = []
    packet_recv = []
    index = 0

    def __init__(self, port=1234, local_ip='192.168.0.105'):
        #Start wifi connection.
        self.tcp_client = tcp.photon_tcp_socket_server()
    
    def send_serial(self, msg):
        print ('Send Serial: ' , msg, type(msg))
        self.index = 0 
        self.packet_recv = self.tcp_client.send( msg )
        print 'Packet Recv: ', self.packet_recv

    def read_serial(self, nBytes=1):
        temp = []
        print 'nBytes: ', nBytes
        print 'index: ', self.index
        for i in range(nBytes):
            temp.append(self.packet_recv[self.index + i])
        self.index += nBytes

        print 'temp in read serail: ', temp
        return temp

class Robotis_Servo():
    ''' Class to use a robotis RX-28 or RX-64 servo.
    '''
    def __init__(self, Photon_Device, servo_id, series = None ):
        ''' Photon_Device- Photon Wifi Microcontroller that sends and receives
                            packets over a tcp sockets and passes them along to the Dynamixel.
            servo_id - servo ids connected to USB2Dynamixel 1,2,3,4 ... (1 to 253)
                       [0 is broadcast if memory serves]
            series - Just a convenience for defining "good" defaults on MX series.
                     When set to "MX" it uses these values, otherwise it uses values
                     better for AX / RX series.  Any of the defaults can be overloaded
                     on a servo-by-servo bases in servo_config.py
        '''
        
	self.series = series;	#record dynamixel series
        self.return_delay = 250 * 2e-6	#default return delay
        # To change the defaults, load some or all changes into servo_config.py
        if series == 'MX':			#MX series generally has 4x the travel and maximums of RX
            defaults = {
                'home_encoder': 0x7FF,
                'max_encoder': 0xFFF,
                'rad_per_enc': math.radians(360.0) / 0xFFF, 
                'max_ang': math.radians(180),
                'min_ang': math.radians(-180),
                'flipped': False,
                'max_speed': math.radians(100)
                }
        else: # Common settings for RX-series.  Can overload in servo_config.py
            defaults = {
                'home_encoder': 0x200,
                'max_encoder': 0x3FF,  # Assumes 0 is min.
                'rad_per_enc': math.radians(300.0) / 1024.0, 
                'max_ang': math.radians(148),
                'min_ang': math.radians(-148),
                'flipped': False,
                'max_speed': math.radians(100)
                }
                

        # Error Checking
        #if USB2Dynamixel == None:
        #    raise RuntimeError('lib_robotis: Robotis Servo requires USB2Dynamixel!\n')
        #else:
        self.dyn = Photon_Device
        #    self.dyn.servo_dev.flush()

        # ID exists on bus?
        self.servo_id = servo_id
        #try:
        #    self.read_address(3)
        #except Exception as inst:
        #    raise RuntimeError('lib_robotis: Error encountered.  Could not find ID (%d) on bus (%s), or USB2Dynamixel 3-way switch in wrong position.\n' %
        #                       ( servo_id, self.dyn.dev_name ))

        # Set Return Delay time - Used to determine when next status can be requested
        data = self.read_address( 0x05, 1)
        self.return_delay = data[0] * 3e-6

        self.settings = {}
        #removed external servo settings file to simplify things (we usually only deal with MX or RX, and both settings are included above)

        # Set to default any parameter not specified in servo_config
        for key in defaults.keys():
            if self.settings.has_key( key ):
                pass
            else:
                self.settings[ key ] = defaults[ key ]	#defaults dict moved into settings component

    def init_cont_turn(self):
        '''sets CCW angle limit to zero and allows continuous turning (good for wheels).
        After calling this method, simply use 'set_angvel' to command rotation.  This 
        rotation is proportional to torque according to Robotis documentation.
        '''
        self.write_address(0x08, [0,0])

    #UPDATED: set limits based on servo max encoder, reset speed to 0
        #should work properly for both RX/MX series
    def kill_cont_turn(self):
        '''resets CCW angle limits to allow commands through 'move_angle' again
        '''

	max_encoder = self.settings['max_encoder']
	hi,lo = max_encoder / 256, max_encoder % 256	#addition made to reset encoder appropriately for both series
        self.write_address(0x08, [lo,hi])

    def is_moving(self):
        ''' returns True if servo is moving.
        '''
        data = self.read_address( 0x2e, 1 )
        return data[0] != 0

    def read_voltage(self):
        ''' returns voltage (Volts)
        '''
        data = self.read_address( 0x2a, 1 )
        return data[0] / 10.

    def read_temperature(self):
        ''' returns the temperature (Celcius)
        '''
        data = self.read_address( 0x2b, 1 )
        return data[0]

    def read_load(self):
        ''' number proportional to the torque applied by the servo.
            sign etc. might vary with how the servo is mounted.
        '''
        data = self.read_address( 0x28, 2 )
        load = data[0] + data[1] * 256
        if load>1024:
            return 1024-load
        else:
            return load

    #ADDED: current functionality only available for MX-64 series:
    def read_current(self):
        if self.series=='MX':
            data = self.read_address( 0x44, 2 )	#current spans addresses 0x44 and 0x45
            curr = data[0] + data[1] * 256
            return 4.5*(curr-2048)		#in mA
        else:
            return 0.

    #ADDED: speed address same for both MX/RX series
    def read_speed(self):
        data = self.read_address( 0x26, 2 )
        speed = data[0] + data[1] * 256
        if speed>1024:
            return float(1024-speed)/1024.0
        else:
            return float(speed)/1024.0

    #both moving speed in joint mode (between designated positions) as well as wheel mode (which only sets direction in operation)
    def apply_speed(self,amnt):
        amnt = max(0.,min(abs(amnt),1.0))
        speed_val = int(amnt*1023)
        if speed_val < 0:
            speed_val = speed_val+1024
        hi,lo = speed_val / 256, speed_val % 256
        self.write_address(0x20,[lo,hi])

    def read_encoder(self):
        ''' returns position in encoder ticks
        '''
        data = self.read_address( 0x24, 2 )
        enc_val = data[0] + data[1] * 256
        return enc_val

    def read_target_encoder(self):
        data = self.read_address( 0x1e, 2 )
        enc_val = data[0] + data[1] * 256
        return enc_val

    def read_angle(self):	#based entirely off of the encoder setting
        ''' returns the current servo angle (radians)
        '''
        ang = (self.read_encoder() - self.settings['home_encoder']) * self.settings['rad_per_enc']
        if self.settings['flipped']:
            ang = ang * -1.0
        return ang

    #ADDED: reading/setting the max torque output (at different addresses)
    def read_max_torque(self):	#set twice, but we'll read the first instance
        data = self.read_address( 0x0e, 2 )
        torque = data[0] + data[1] * 256
        return torque

    def apply_max_torque(self,val):	#unlike speed, 0 is not max torque; no mode dependencies to use/set
	amnt = max(0.,min(abs(val),1.0))
	n = int(amnt*1023)
        n = min(max(n,0), 1023)		#no scaling issues between MX and RX like with position
        hi,lo = n / 256, n % 256
        print("hi, lo: ",lo,hi)
        self.write_address( 0x22, [lo,hi])
        return self.write_address( 0x0e, [lo,hi])

    #alternative approach to move_to_encoder, except w/ arbitrary angle setting
    def move_angle(self, ang, angvel=None, blocking=True):
        ''' move to angle (radians)
        '''
        if angvel == None:
            angvel = self.settings['max_speed']

        if angvel > self.settings['max_speed']:
            print 'lib_robotis.move_angle: angvel too high - %.2f deg/s' % (math.degrees(angvel))
            print 'lib_robotis.ignoring move command.'
            return

        if ang > self.settings['max_ang'] or ang < self.settings['min_ang']:
            print 'lib_robotis.move_angle: angle out of range- ', math.degrees(ang)
            print 'lib_robotis.ignoring move command.'
            return
        
        self.set_angvel(angvel)

        if self.settings['flipped']:
            ang = ang * -1.0
        enc_tics = int(round( ang / self.settings['rad_per_enc'] ))
        enc_tics += self.settings['home_encoder']
        self.move_to_encoder( enc_tics )

        if blocking == True:
            while(self.is_moving()):
                continue

    def move_to_encoder(self, n):
        ''' move to encoder position n
        '''
        # In some border cases, we can end up above/below the encoder limits.
        #   eg. int(round(math.radians( 180 ) / ( math.radians(360) / 0xFFF ))) + 0x7FF => -1
        n = min( max( n, 0 ), self.settings['max_encoder'] ) 
        hi,lo = n / 256, n % 256
        return self.write_address( 0x1e, [lo,hi] )

    #ADDED: reading the goal encoder position that the user has specified    
        #useful for slow motions or torque-limited motions to find distance to goal
    def read_goal(self):
        data = self.read_address( 0x1e, 2)
        enc_val = data[0] + data[1] * 256
        return enc_val

    #ADDED: enabling torque control mode for the MX-64 series and above ONLY:
    def enable_torque_mode(self):
        if self.series=='MX':
            return self.write_address(0x46, [1])
        else:
            return 0
    def disable_torque_mode(self):
        if self.series=='MX':
            return self.write_address(0x46, [0])
        else:
            return 0
    def apply_torque(self,amnt):
        if self.series=='MX':
            amnt = max(0.,min(abs(amnt),1.0))
            torque_val = int(amnt*1023)
            if torque_val < 0:
                torque_val = torque_val+1024
            hi,lo = torque_val / 256, torque_val % 256
            return self.write_address(0x47,[lo,hi])
        else:
            return 0

    #disabling/enabling address 18 effectively shuts down motor output
        #different from torque mode that's available in the MX models
        #USE ONLY AS ON/OFF quick shutdown control
    def enable_torque(self):
        return self.write_address(0x18, [1])

    def disable_torque(self):
        return self.write_address(0x18, [0])

    #same as apply_speed, except set rad/sec as opposed to single value scalar
    def set_angvel(self, angvel):
        ''' angvel - in rad/sec
        '''     
        rpm = angvel / (2 * math.pi) * 60.0
        angvel_enc = int(round( rpm / 0.111 ))
        if angvel_enc<0:
            hi,lo = abs(angvel_enc) / 256 + 4, abs(angvel_enc) % 256
        else:
            hi,lo = angvel_enc / 256, angvel_enc % 256
        
        return self.write_address( 0x20, [lo,hi] )

    def write_id(self, id):
        ''' changes the servo id
        '''
        return self.write_address( 0x03, [id] )

    def __calc_checksum(self, msg):
        chksum = 0
        for m in msg:
            chksum += m
        chksum = ( ~chksum ) % 256
        return chksum

    def ping(self):
        return self.read_address(self,0x01,nBytes=1)

    def read_address(self, address, nBytes=1):
        ''' reads nBytes from address on the servo.
            returns [n1,n2 ...] (list of parameters)
        '''
        msg = [ 0x02, address, nBytes ]
        return self.send_instruction( msg, self.servo_id )

    def write_address(self, address, data):
        ''' writes data at the address.
            data = [n1,n2 ...] list of numbers.
            return [n1,n2 ...] (list of return parameters)
        '''
        msg = [ 0x03, address ] + data
        return self.send_instruction( msg, self.servo_id )

    def send_instruction(self, instruction, id):
        time.sleep(self.return_delay)	#helps w/ communication consistency?

        msg = [ id, len(instruction) + 1 ] + instruction # instruction includes the command (1 byte + parameters. length = parameters+2)

        chksum = self.__calc_checksum( msg )
        msg = [ 0xff, 0xff ] + msg + [chksum]
        
        print (type(msg))
        print 'send_instruction: ' , msg
        #elf.dyn.acq_mutex()
        
        self.send_serial( msg )
        data, err = self.receive_reply()
        #except Exception as inst:
        #    self.dyn.rel_mutex()
        #    raise RuntimeError(repr(str(inst)))
        #self.dyn.rel_mutex()
        
        if err != 0:
            self.process_err( err )
        
        return data

    def process_err( self, err ):
        raise RuntimeError('lib_robotis: An error occurred: %d\n' % err)

    def receive_reply(self):
        start = self.dyn.read_serial( 2 )	#from pydynamixel: possible that these contain empty bytes
        servo_id = self.dyn.read_serial( 1 )

        while servo_id=='\xff':
            servo_id = self.dyn.read_serial( 1 )	#on Sparkfun USB-to-RS485 chip, more than 3 header bytes are sometimes set - apparently not an issue with the USB2Dynamixel

        #if type(servo_id) is not str or len(servo_id)!=1:
        #    raise RuntimeError('lib_robotis: Invalid message headers, got servo id of type: '+repr(type(servo_id))+' and length: '+repr(len(servo_id)))
        #if ord(servo_id) != self.servo_id:
        #    raise RuntimeError('lib_robotis: Incorrect servo ID received')
        data_len = self.dyn.read_serial( 1 )
        print 'data_len: ', data_len
        print 'str(data_len): ', str(data_len), (data_len[0])
        err = self.dyn.read_serial( 1 )
        print 'err: ', err
        print ord(str(data_len[0]))
        data = self.dyn.read_serial( int(str(data_len[0])) - 2 )
        print 'data: ', data
        checksum = self.dyn.read_serial( 1 ) 		#checksum is read but never compared...(by design, according to original lib_robotis.py)
        #print( "Receive reply: ", [ord(str(v)) for v in data], ord(str(err)))
        return [int(str(v)) for v in data], int(str(err[0]))
        

    def send_serial(self, msg):
        """ sends the command to the servo
        """
        out = ''
        for m in msg:
            out += chr(m)
        self.dyn.send_serial( out )

#def find_servos(dyn):
#    ''' Finds all servo IDs on the USB2Dynamixel '''
#    servos = []
#    dyn.servo_dev.setTimeout( 0.03 ) # To make the scan faster
#    for i in xrange(254):
#        try:
#            s = Robotis_Servo( dyn, i )
#            print '\n FOUND A SERVO @ ID %d\n' % i
#            servos.append( i )
#        except:
#            pass
#    dyn.servo_dev.setTimeout( 1.0 ) # Restore to original
#    return servos


def recover_servo(dyn):
    ''' Recovers a bricked servo by booting into diagnostic bootloader and resetting '''
    raw_input('Make sure only one servo connected to USB2Dynamixel Device [ENTER]')
    raw_input('Disconnect power from the servo, but leave USB2Dynamixel connected to USB. [ENTER]')

    dyn.servo_dev.setBaudrate( 57600 )
    
    print 'Get Ready.  Be ready to reconnect servo power when I say \'GO!\''
    print 'After a second, the red LED should become permanently lit.'
    print 'After that happens, Ctrl + C to kill this program.'
    print
    print 'Then, you will need to use a serial terminal to issue additional commands.',
    print 'Here is an example using screen as serial terminal:'
    print
    print 'Command Line:  screen /dev/robot/servo_left 57600'
    print 'Type: \'h\''
    print 'Response: Command : L(oad),G(o),S(ystem),A(pplication),R(eset),D(ump),C(lear)'
    print 'Type: \'C\''
    print 'Response:  * Clear EEPROM '
    print 'Type: \'A\''
    print 'Response: * Application Mode'
    print 'Type: \'G\''
    print 'Response:  * Go'
    print
    print 'Should now be able to reconnect to the servo using ID 1'
    print
    print
    raw_input('Ready to reconnect power? [ENTER]')
    print 'GO!'

    while True:
        s.write('#')
        time.sleep(0.0001)


if __name__ == '__main__':

    p = optparse.OptionParser()
    p.add_option('-d', action='store', type='string', dest='dev_name',
                 help='Required: Device string for USB2Dynamixel. [i.e. /dev/ttyUSB0 for Linux, \'0\' (for COM1) on Windows]')
    p.add_option('--scan', action='store_true', dest='scan', default=False,
                 help='Scan the device for servo IDs attached.')
    p.add_option('--recover', action='store_true', dest='recover', default=False,
                 help='Recover from a bricked servo (restores to factory defaults).')
    p.add_option('--ang', action='store', type='float', dest='ang',
                 help='Angle to move the servo to (degrees).')
    p.add_option('--ang_vel', action='store', type='float', dest='ang_vel',
                 help='angular velocity. (degrees/sec) [default = 50]', default=50)
    p.add_option('--id', action='store', type='int', dest='id',
                 help='id of servo to connect to, [default = 1]', default=1)
    p.add_option('--baud', action='store', type='int', dest='baud',
                 help='baudrate for USB2Dynamixel connection [default = 57600]', default=57600)

    opt, args = p.parse_args()

    if opt.dev_name == None:
        p.print_help()
        sys.exit(0)

    dyn = USB2Dynamixel_Device(opt.dev_name, opt.baud)

    if opt.scan:
        find_servos( dyn )

    if opt.recover:
        recover_servo( dyn )

    if opt.ang != None:
        servo = Robotis_Servo( dyn, opt.id )
        servo.move_angle( math.radians(opt.ang), math.radians(opt.ang_vel) )
