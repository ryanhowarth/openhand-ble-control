## openhand-wifi-control

Wireless control of openhand using an Particle Photon Microcontroller with WiFi to send and receive commands from the Dynamixel.

### Setup
This setup was tested with Xubuntu 14.04 and TL-WR841N Wireless Router.

Connect the Photon to a Wifi Network using the Particle CLI or using the Particle Mobile App.

Connect your computer to the same network and note your computer's local IP Address. Replace the server_IP address at the top of the *photon_hand_control.ino* script with the your own local address. Flash this scipt to the photon. 

### Usage
Start the TCP Socket Server by running the following python script. Next, turn on the Photon. The Photon should connect to the TCP Server shortly after booting. If the Photon starts blinking red, it has failed to connect to the server and will try again shortly.


```shell
python openhand_control.py

If this script is stopped, the Photon must be power cycled in order to reconnect to a new TCP Server. 

