//SYSTEM_MODE(MANUAL); //Disables automatic cloud connection.



//TCPServer server = TCPServer(12345);
TCPClient client;
byte server[] = { 192, 168, 0, 105 }; // From DHCP on macbook. Could change

int led = D2;
int txrx_pin = D3;
int temperature = 0;


void setup() {
    pinMode(led, OUTPUT);
    pinMode(txrx_pin, OUTPUT);
    Serial.begin(9600);
    Serial1.begin(9600);
    
    //delay(25000);
    digitalWrite(led, HIGH);
    delay(3000);
    Serial.print('\n');
    connect();
    
    
}

//Connects To TCP Server
void connect() {
    if (client.connect(server, 1234))
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
    
    //client = server.available();
    if (client.available()) {
        int len = client.available();
        
        Serial.println("Serial.availible(): ");
        Serial.println(len);
        
        byte hex_byte[len];
        for (int i = 0; i < len; i++) {
            uint8_t data = client.read();
            hex_byte[i] = '\x00' + int(data);
        }

        
        digitalWrite(txrx_pin, HIGH);
        delay(10);
        //Serial1.write(hex_byte[0]);

        for (int i = 0; i < len; i++) {
            delay(2); // Need spacing between bytes for some reason?
            Serial1.write(hex_byte[i]);
            //Serial.print(hex_byte[i]);
            
        }
        delayMicroseconds(1200); //Allow last bit to go through before switching to RX (at 9600 baud)
        read_data();
        

    }
    //check_connection();


}
//Reads data from the dyanmixel.
void read_data() {
    digitalWrite(txrx_pin, LOW);
    delay(10);
    Serial.print("Ser1.aval: ");
    Serial.println(Serial1.available());
    if (Serial1.available() > 0) {
        while(Serial1.available() > 0) {
            byte x = Serial1.read();
            client.write(x);
            Serial.print(x);
            
        }
    }
    
}


void check_connection() {
    //client.flush();
    //client.read();
    
    if (!client.connected()) {
        Serial.print("Client.connected: ");
        Serial.println(client.connected());
        client.stop();
        connect();
    }
}







