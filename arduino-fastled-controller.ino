#include <FastLED.h>

// Display configuration
#define LED_PIN     6       // Pin connected to the LED strip
#define NUM_LEDS    1600    // 40x40 = 1600 LEDs
#define LED_TYPE    WS2812B // Change to your LED type (WS2812B, APA102, etc.)
#define COLOR_ORDER GRB     // Change if your LEDs have different color order

// Frame rate control
#define TARGET_FPS  24

// Serial communication settings
#define BAUD_RATE   1000000 // High baud rate for faster data transfer
#define HEADER_MARKER 0xAB  // Marker to identify start of frame

// LED array
CRGB leds[NUM_LEDS];

// Buffer for incoming data
uint8_t serialBuffer[NUM_LEDS * 3 + 1]; // RGB data + header
uint16_t bufferIndex = 0;
bool frameStarted = false;

void setup() {
  // Initialize FastLED
  FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(50); // Set initial brightness (0-255)
  FastLED.clear();
  FastLED.show();
  
  // Initialize serial communication
  Serial.begin(BAUD_RATE);
  Serial.setTimeout(50); // Short timeout for responsiveness
  
  // Signal we're ready
  Serial.write('R');
}

void loop() {
  // Check if data is available
  while (Serial.available() > 0) {
    uint8_t inByte = Serial.read();
    
    // Check for header marker
    if (inByte == HEADER_MARKER && !frameStarted) {
      frameStarted = true;
      bufferIndex = 0;
      continue;
    }
    
    // Store byte in buffer
    if (frameStarted && bufferIndex < NUM_LEDS * 3) {
      serialBuffer[bufferIndex++] = inByte;
      
      // If we've received a complete frame
      if (bufferIndex >= NUM_LEDS * 3) {
        processFrame();
        frameStarted = false;
        
        // Signal ready for next frame
        Serial.write('A'); // ACK
        break;
      }
    }
  }
}

void processFrame() {
  // Transfer data from buffer to LED array
  for (uint16_t i = 0; i < NUM_LEDS; i++) {
    uint16_t pixelIndex = i * 3;
    leds[i].r = serialBuffer[pixelIndex];
    leds[i].g = serialBuffer[pixelIndex + 1];
    leds[i].b = serialBuffer[pixelIndex + 2];
  }
  
  // Update the display
  FastLED.show();
}
