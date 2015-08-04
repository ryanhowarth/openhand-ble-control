//SYSTEM_MODE(SEMI_AUTOMATIC); //Disables automatic cloud connection.


TCPClient tcp_client;
byte server[] = { 192, 168, 0, 105 }; // From DHCP on macbook. Could change
int port = 1234;
int led = D2;
int txrx_pin = D3;

void setup() {
    //WiFi.on();
    //WiFi.connect();
    
    pinMode(led, OUTPUT);
    pinMode(txrx_pin, OUTPUT); //Controls direction of serial comms dyanmixel.
    Serial.begin(9600);
    Serial1.begin(9600);

    digitalWrite(led, HIGH);
    delay(3000);
    connect();
}

//Connects To TCP Server
void connect() {
    if (tcp_client.connect(server, port))
    {
        Serial.println("connected");
        digitalWrite(led, LOW);
    }
    else
    {
        Serial.println("connection failed");
    }
    Serial.println('Starting the Server');
    
    
}

//Passing alongs packets between computer and dynamixel
void loop() {

    if (tcp_client.available()) {

        dynamixel_send();
        
        dyanmixel_read();
    }
}

//Receives data from the tcp server and sends it to dynamixel.
void dynamixel_send() {
    digitalWrite(txrx_pin, HIGH); //Switch to tx to write packet to dynamixel.
    delay(2); //Allow this to take effect
    while(tcp_client.available()) {
        byte data = int(tcp_client.read()) + '\x00';
        delayMicroseconds(1500); // Need spacing between bytes for some reason?
        Serial1.write(data);
    }
    delayMicroseconds(1200); //Allow last bit to go through before switching to RX (at 9600 baud)
}


//Reads data from the dyanmixel and sends it to computer over tcp.
void dyanmixel_read() {
    digitalWrite(txrx_pin, LOW); //Switch to rx to receive packet back from dynamixel.
    delay(10);// wait for response from dynamixel before reading from serial.
    while(Serial1.available() > 1) {
        byte x = Serial1.read();
        tcp_client.write(x);
        Serial.print(x);
    }
    Serial1.read(); //Read stopbit out of buffer but don't send to server.
    
}

