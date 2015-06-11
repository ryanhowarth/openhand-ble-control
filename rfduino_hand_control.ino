

/*


*/

#include <RFduinoBLE.h>

// (shows when the RFduino is advertising or not)
int advertisement_led = 3;

// Shows when connected to device
int connection_led = 2;

// The pin to be used for enable/disable signal
int Txcontrol= 4; 

// Define parameters
int i = 0;
byte startAddress;





void setup() {
  
  //Change the advertisement Interval to be small
  int interval = 20;
  RFduinoBLE.advertisementInterval = interval;
  
  // led used to indicate that the RFduino is advertising
  pinMode(advertisement_led, OUTPUT);
  
  // led used to indicate that the RFduino is connected
  pinMode(connection_led, OUTPUT);

  RFduinoBLE.advertisementData = "temp";
  RFduinoBLE.advertisementData = "-servo";
  
  delay(1000); //Let dynamixel start up 
  
   
  pinMode(Txcontrol, OUTPUT);
  digitalWrite(Txcontrol, LOW);
  pinMode(6, OUTPUT);
  Serial.begin(9600);
  
  // start the BLE stack
  RFduinoBLE.begin();
}

unsigned int hexToDec(String hexString) {
  
  unsigned int decValue = 0;
  int nextInt;
  
  for (int i = 0; i < hexString.length(); i++) {
    
    nextInt = int(hexString.charAt(i));
    if (nextInt >= 48 && nextInt <= 57) nextInt = map(nextInt, 48, 57, 0, 9);
    if (nextInt >= 65 && nextInt <= 70) nextInt = map(nextInt, 65, 70, 10, 15);
    if (nextInt >= 97 && nextInt <= 102) nextInt = map(nextInt, 97, 102, 10, 15);
    nextInt = constrain(nextInt, 0, 15);
    
    decValue = (decValue * 16) + nextInt;
  }
  
  return decValue;
}



void loop() {
  String stringRead;
  byte byteRead;
  if (Serial.available()) {
    stringRead = Serial.readString(); 
  }
  
  byte ff = '\x0d';
  String test = String(ff, DEC);
  int aa = test.toInt();
  
  Serial.println(aa);
  
  //float temp = byteRead;
  float temp = aa;
  
  //const char *hexstring[4];
  //float temp = (float)strtol(hexstring, NULL, 0);
  
  // switch to lower power mode
  //RFduino_ULPDelay(INFINITE);
    // sample once per second
  //RFduino_ULPDelay( SECONDS(1) );
  //float temp = RFduino_temperature(CELSIUS);
  //Serial.println(temp);
  // send the sample to the iPhone
  RFduinoBLE.sendFloat(temp);
}

void RFduinoBLE_onAdvertisement(bool start)
{
  // turn the green led on if we start advertisement, and turn it
  // off if we stop advertisement
  
  if (start)
    digitalWrite(advertisement_led, HIGH);
  else
    digitalWrite(advertisement_led, LOW);
}

void RFduinoBLE_onConnect()
{
  digitalWrite(connection_led, HIGH);
}

void RFduinoBLE_onDisconnect()
{
  digitalWrite(connection_led, LOW);
}



void RFduinoBLE_onReceive(char *data, int len)
{
  
  //Turns tx pin to High at start of packet and Low at end
  if (len == 4) {
    digitalWrite(Txcontrol, HIGH);
    digitalWrite(6, !digitalRead(6));
    //delay(1);    
    //return;

  }
  else if (len == 5){
    delay(3); //Allow last byte to get through
    digitalWrite(Txcontrol, LOW);
    digitalWrite(6, !digitalRead(6));
    //delay(1);
    //return;
  }
  else {
    digitalWrite(Txcontrol, HIGH);
    char control[len];
    for (int i =0; i < len; i++) {
      control[i] = data[i];
    }
    delay(1);
    byte hex_byte = '\x00' + atoi(control);
    Serial.write(hex_byte);
  }
  
  //Serial.println( atoi(data)  + 5 );
  /*
  if (data[0] == '1')
  {
    
    moveServos();
    //digitalWrite(4, HIGH);
  }
  else if (data[0] == '0')
  {
    digitalWrite(4, LOW);
  }*/
}



void moveServos (){
   byte servoID= '\x01';
   byte start_char = '\xFF';
   byte write_cmd = '\x03';
   byte led_control = '\x19';
    
 
   digitalWrite(Txcontrol,HIGH);   // Notify max485 transciever to accept tx 
   digitalWrite(6, HIGH);
   delay(1);                 // Allow this to take effect
  
   byte test  = '\x00' + 255;
   
   Serial.write(test);  // 1.These 2 bytes are 'start message'
   delay(1);
   Serial.write(start_char);  // 2.These 2 bytes are 'start message'
   delay(1);
   Serial.write(servoID);  // 3.Address 1 is target servo or 0xfe which is broadcast mode
   delay(1);
   Serial.write('\x04');  // 4.Length of string
   delay(1);
   Serial.write(write_cmd);  // 5.Ping read write or syncwrite 0x01,2,3,83
   delay(1);
   Serial.write(led_control);  // 6.Start address for data to be written
   delay(1);
   Serial.write('\x01');  //  7.Turning on signal
   delay(1);
   //Serial.write( byte(0x00) ); // In C, '0' as naked constant can be many things. Need to cast as byte
   Serial.write('\xDD'); //8. the notchecksum
   delay(3);
  
   digitalWrite(Txcontrol, LOW);
   digitalWrite(6, LOW);
   /*
   printHex(255, 2);
   delay(10);
   printHex(255, 2);
   delay(10);
   
   printHex(1, 2);
   delay(10);
   printHex(4, 2);
   delay(10);
   
   printHex(3, 2);
   delay(10);
   printHex(25, 2);
   delay(10);
   printHex(1, 2);
   delay(10);
   
   printHex(221, 2);
   delay(10);*/
   
   /*
   Serial.write(start_char);  // 1.These 2 bytes are 'start message'
   Serial.write(start_char);  // 2.These 2 bytes are 'start message'
   Serial.write(servoID);  // 3.Address 1 is target servo or 0xfe which is broadcast mode
   Serial.write(0x05);  // 4.Length of string
   Serial.write(write_cmd);  // 5.Ping read write or syncwrite 0x01,2,3,83
   Serial.write(0x22);  // 6.Start address for data to be written
   Serial.write(0xCC);  //  7.Turning on signal
   Serial.write( byte(0x00) ); // In C, '0' as naked constant can be many things. Need to cast as byte
   Serial.write(0x08); //8. the notchecksum
   
   delay(50);
 
   Serial.write(start_char);  // 1.These 2 bytes are 'start message'
   Serial.write(start_char);  // 2.These 2 bytes are 'start message'
   Serial.write(servoID);  // 3.Address 1 is target servo or 0xfe which is broadcast mode
   Serial.write(0x05);  // 4.Length of string
   Serial.write(write_cmd);  // 5.Ping read write or syncwrite 0x01,2,3,83
   Serial.write(0x0E);  // 6.Start address for data to be written
   Serial.write(0xCC);  //  7.Turning on signal
   Serial.write( byte(0x00) ); // In C, '0' as naked constant can be many things. Need to cast as byte
   Serial.write(0x1C); //8. the notchecksum
 
   delay(50);
 
   Serial.write(start_char);  // 1.These 2 bytes are 'start message'
   Serial.write(start_char);  // 2.These 2 bytes are 'start message'
   Serial.write(servoID);  // 3.Address 1 is target servo or 0xfe which is broadcast mode
   Serial.write(0x05);  // 4.Length of string
   Serial.write(write_cmd);  // 5.Ping read write or syncwrite 0x01,2,3,83
   Serial.write(0x1E);  // 6.Start address for data to be written
   Serial.write(0xD8);  //  7.Turning on signal
   Serial.write(0x0C);
   Serial.write(0xF4); //8. the notchecksum
   */
}
  

