## openhand-ble-control

Wireless control of openhand using an RFduino with ble to send and receive commands from the Dynamixel.

### Setup

This setup was tested with Xubuntu 14.04 and Bluez 5.21

Upload *rfduino_hand_control.ino* to your RFduino.

Install pygatt to magange the BLE connection: https://github.com/ampledata/pygatt
Using pip:
```shell
pip install pygatt
```

Bluez version > 5.5 is needed for pygatt. This must be installed from source on Ubuntu. Download: http://www.bluez.org/download/

 Install Dependencies:
```shell
sudo apt-get install libglib2.0-dev libdbus-1-dev libusb-dev libudev-dev libical-dev systemd libreadline-dev
```

 Run Configuration Script:
 
   *--enable-library* Builds bluez 4 compatible version which some applications could depend on.
   
   *--disable-systemd* Needed if systemd is not installed.
   
```shell
./configure --enable-library --prefix=/usr --mandir=/usr/share/man --sysconfdir=/etc --localstatedir=/var --disable-systemd
```

 Compile and install using checkinstall:
```shell
make
sudo checkinstall
```

 Gatttool does not work correctly right away. Need to copy gatttool to /usr/local/bin/:
```shell
sudo cp attrib/gatttool /usr/local/bin/
```


### Usage
Start device advertising and run ble_interface.py to send and receive hand commands. Enter help to see possible commands. 

```shell
sudo hcitool lescan
python ble_interface.py
```
