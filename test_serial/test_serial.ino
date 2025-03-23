#define BAUD_RATE 921600

// change this to match the currently connected device
#define TEENSY1

// Serial communication codes
#define CONNECTION_REQUEST 'C'
#define DEVICE_ID 'D'
#define READY_TO_RECEIVE 'R'
#define READY_TO_TRANSMIT 'T'
#define ERROR 'E'

// Error codes
#define SUCCESS 0
#define FAIL 1
#define WRONG_RESPONSE 100
#define WRONG_DEVICE_ID 101

// Pin number for on-board LED
#define BOARDLED 13

#ifdef TEENSY1
#define THIS_DEVICE_ID '1'
#define OTHER_DEVICE_ID '2'
#endif

#ifdef TEENSY2
#define THIS_DEVICE_ID '2'
#define OTHER_DEVICE_ID '1'
#endif

#define SUPERVISOR_DEVICE_ID '3'

bool comms_established = false;
uint8_t inByte;  // incoming serial byte
char command;  // command code for serial communication
char inChar;  // incoming serial char
bool newData = false;  // incoming serial byte

// Board led state
int boardLedState = LOW;

void setup() {

  // Setup board LED pin
  pinMode(BOARDLED, OUTPUT);

  // Initialize serial communication
  Serial.begin(BAUD_RATE);

  // Short timeout for responsiveness
  Serial.setTimeout(50);

  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  Serial.println("Serial port connected");

  establishCommunication();  // send a byte periodically until receiver responds
  Serial.println("Communication established");
}

int i = 0;

void loop() {

  // Check if data is available
  while (Serial.available() > 0) {
    uint8_t inByte = Serial.read();
    // do nothing with it
  }
  Serial.println(i);
  i = (i + 1) % 10;
  delay(1000);
}

void emptyInputBuffer() {
  while (Serial.available() > 0) {
      Serial.read();
  }
}

void readChar() {
    if (Serial.available() > 0) {
        inChar = Serial.read();
        newData = true;
    }
}

void readByte() {
    if (Serial.available() > 0) {
        inByte = Serial.read();
        newData = true;
    }
}

void readCommandWithOneChar()
  readChar()
  if (newData) {
    command = inChar;
    readChar()
    if (newData) {
        return SUCCESS;
    }
  }
  return FAIL;
}

void toggleBoardLed() {
  // if the LED is off turn it on and vice-versa:
  boardLedState = (boardLedState == LOW) ? HIGH : LOW;
  digitalWrite(BOARDLED, boardLedState);
}

void sendErrorMessage(uint8_t e) {
  Serial.print(ERROR);
  Serial.println(e);
}

void establishCommunication() {
  while (!comms_established) {

    // Wait until supervisor device is not sending data
    while (Serial.available() > 0) {
      Serial.println("Emptying input buffer");
      emptyInputBuffer();
      delay(100);
    }

    // Send connection request char repeatedly and wait for response
    while (Serial.available() == 0) {
      toggleBoardLed();
      Serial.println(CONNECTION_REQUEST);
      delay(1000);
    }

    // Check 
    inChar = Serial.read();
    Serial.print("Received char: ");
    Serial.println(inChar);

    // Read response
    if (inChar == DEVICE_ID) {
      // Read next char which should be device's id
      inChar = Serial.read();
      if (inChar == SUPERVISOR_DEVICE_ID) {
        comms_established = true;
        Serial.print(DEVICE_ID);
        Serial.println(THIS_DEVICE_ID);
      }
      else {
        sendErrorMessage(WRONG_DEVICE_ID);
      }
    }
    else {
      sendErrorMessage(UNEXPECTED_RESPONSE);
    }
  }
}
