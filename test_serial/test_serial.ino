#define BAUD_RATE 921600
#define THIS_DEVICE_ID '2'  // change these for each device
#define OTHER_DEVICE_ID '1'  // change these for each device
#define SUPERVISOR_DEVICE_ID '3'
#define CONNECTION_REQUEST 'C'
#define CONNECTION_REQUEST_RESPONSE 'R'

// Pin number for on-board LED
#define BOARDLED 13

bool comms_established = false;
uint8_t inByte = 0;  // incoming serial byte

// Board led state
int boardLedState = HIGH;

void setup() {
  delay(1000);

  // Setup board LED pin
  pinMode(BOARDLED, OUTPUT);

  // Initialize serial communication
  Serial.begin(BAUD_RATE);

  // Short timeout for responsiveness
  Serial.setTimeout(50);

  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  establishCommunication();  // send a byte to establish contact until receiver responds	
}

int i = 0;

void loop() {

  // Check if data is available
  while (Serial.available() > 0) {
    uint8_t inByte = Serial.read();
    // do nothing with it
  }
  Serial.print(i);
  i = (i + 1) % 10;
  delay(1000);
}

void establishCommunication() {
  while (comms_established == false) {
    // Send connection request char until other device responds
    while (Serial.available() <= 0) {
      digitalWrite(BOARDLED, boardLedState);
      Serial.print(CONNECTION_REQUEST);
      delay(500);
      // if the LED is off turn it on and vice-versa:
      boardLedState = (boardLedState == LOW) ? HIGH : LOW;
    }
    inByte = Serial.read();
    if (inByte == CONNECTION_REQUEST) {
      // Send response char and device id to acknowledge request
      Serial.write(CONNECTION_REQUEST_RESPONSE);
      Serial.write(THIS_DEVICE_ID);
      comms_established = true;
    }
    else {
      // Read and ignore all data in buffer
      while (Serial.available() > 0) {
        inByte = Serial.read();
      }
    }
  }
}
