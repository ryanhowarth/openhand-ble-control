

/*
RFdunio sketch that sends and recevies commands to a dynamixel.

*/

#include <RFduinoBLE.h>

// (shows when the RFduino is advertising or not)
int advertisement_led = 3;

// Shows when connected to device
int connection_led = 2;

// The pin to be used for enable/disable signal
int txrx_pin = 4;

// Debug pins
int debug = 6;
int debugtwo = 5;

//Detmines whether the hand is currently closing.
boolean closing =  false;

void setup() {

  //Change the advertisement Interval to be small
  int interval = 20;
  RFduinoBLE.advertisementInterval = interval;

  // led used to indicate that the RFduino is advertising
  pinMode(advertisement_led, OUTPUT);

  // led used to indicate that the RFduino is connected
  pinMode(connection_led, OUTPUT);

  delay(500); //Let dynamixel start up

  // Pin to control direction of information (TX/RX)
  pinMode(txrx_pin, OUTPUT);
  digitalWrite(txrx_pin, LOW);

  //Debugging Pins
  pinMode(debug, OUTPUT);
  pinMode(debugtwo, OUTPUT);

  //Start Serial Connection
  Serial.begin(9600);

  // start the BLE stack
  RFduinoBLE.begin();


}

void loop() {
  //No delay (Constantly Looping)
  RFduino_ULPDelay(0);

  //Better to start the control loop here than in the interupt function.
  if (closing)
  {
    control_loop();
  }

  //Reads commands from Dynamixel and sends them over BLE to Laptop
  if (Serial.available() > 0 && !closing ) {
    digitalWrite(txrx_pin, LOW); //Switch to receive data from dynamixel
    char dataRead[8] = {};
    Serial.readBytes(dataRead, 8);
    RFduinoBLE.send(dataRead, 8);
  }

  // switch to lower power mode
  //RFduino_ULPDelay(INFINITE);
  // sample once per second
  //RFduino_ULPDelay( SECONDS(1) );
}

//Monitors position and/or load on the hand while the hand is closing or opening. 
void control_loop()
{
  while (closing)
  {
    check_speed();
    delay(25); //Weird behavior without this delay
    if (Serial.available() > 0) {
      digitalWrite(txrx_pin, LOW);
      char dataRead[8] = {};
      Serial.readBytes(dataRead, 8);

      int speed_val = get_value(dataRead);
      if (speed_val < 5)
      {
        digitalWrite(debugtwo, !digitalRead(debugtwo));
        closing = false;
      }
      else if (speed_val > 5) {
        digitalWrite(debug, !digitalRead(debug));
      }
      delay(25);
    }
  }

}

//Take packets and return the relevent information. (Even if some of beginning bytes are missing).
int get_value(char *dataRead)
{
  int servo_id = 1;
  for (int i = 0; i < sizeof(dataRead) / sizeof(char); i++) {
    int value  = int(dataRead[i]);
    if (value == servo_id) {
      int data = int(dataRead[i + 3]);
      if (data > 20) {
        //digitalWrite(debug, HIGH);
      }
      return data;
    }
  }
  return -1;
}

void RFduinoBLE_onAdvertisement(bool start)
{
  // turn the red led on if we start advertisement, and turn it
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

/*
  Recevies Commands from Computer and Sends them to Dynamixel
  This is an interrupt function. Strange things occur if program spends too much time in here.
*/
void RFduinoBLE_onReceive(char *data, int len)
{

  uint8_t a = data[0];
  byte hex_byte[len];
  for (int i = 0; i < len; i++) {
    hex_byte[i] = '\x00' + int(data[i]);
  }

  if (int(data[5]) == 30) {
    send_to_servo(hex_byte, len);
    check_speed();
    //digitalWrite(debug, HIGH);
    closing = true;

    //digitalWrite(debug, HIGH);
  }
  else
  {
    send_to_servo(hex_byte, len);
  }
}

void send_to_servo(byte *data, int len)
{
  digitalWrite(txrx_pin, HIGH); //Switch to TX mode before sending data
  delay(10);                    //Allow this to take effect
  for (int i = 0; i < len; i++) {
    delay(1); // Need spacing between bytes for some reason?
    Serial.write(data[i]);
  }
  delayMicroseconds(1200); //Allow last bit to go through before switching to RX (at 9600 baud)
  digitalWrite(txrx_pin, LOW);
}

void check_load()
{
  byte load_packet[] = {'\xff', '\xff', '\x01', '\x04', '\x02', '\x28', '\x02', '0xCE'};
  send_to_servo(load_packet, sizeof(load_packet) / sizeof(byte) );
}

void check_speed()
{
  byte speed_packet[] = {'\xff', '\xff', '\x01', '\x04', '\x02', '\x26', '\x02', '\xD0'};
  send_to_servo(speed_packet, sizeof(speed_packet) / sizeof(byte) );
}


