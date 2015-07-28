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
    //Spark.variable("temperature", &temperature, INT);
    //pinMode(A0, INPUT)
    
    //digitalWrite(led, HIGH);
    
    if (client.connect(server, 1234))
    {
        Serial.println("connected");
        //client.println("GET /search?q=unicorn HTTP/1.0");
        //client.println("Host: www.google.com");
        //client.println("Content-Length: 0");
        //client.println();
    }
    else
    {
        Serial.println("connection failed");
    }
    
    //delay(7000);
    //delay(7000);
    //delay(7000);
    //delay(7000);
    //digitalWrite(led, HIGH);
    
    Serial.println('Starting the Server');
    digitalWrite(led, LOW);
    
    

    IPAddress localIP = WiFi.localIP();
    Serial.print(localIP);
    Serial.print('\n');
    
    
}

void loop() {
    
    //client = server.available();
    if (client.available()) {
        char c = client.read();
        Serial.print(c);
        
        byte led_on[] = {'\xff', '\xff', '\x01', '\x04', '\x03', '\x19', '\x01', '\xDD'};
        digitalWrite(txrx_pin, HIGH);
        delay(50);                    //Allow this to take effect
        for (int i = 0; i < 8; i++) {
            delay(1); // Need spacing between bytes for some reason?
            Serial1.write(led_on[i]);
        }
        //delayMicroseconds(1200); //Allow last bit to go through before switching to RX (at 9600 baud)
        
        delay(50);
        digitalWrite(txrx_pin, LOW);
        
        
        
        
        
        char msg = 'a';
        client.write(msg);
        //digitalWrite(led, HIGH);
        //Serial.print("Client Found");
    }
    
    
    
    
    
    /*
    digitalWrite(led, HIGH);
    delay(1000);
    digitalWrite(led, LOW);
    delay(1000);
    temperature += 1;
    */
    //Serial.print("Test Print");
    //delay(2000);
    //Serial.print('\n');
}










