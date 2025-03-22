#include <FastLED.h>

// Number of leds in the strip
#define NUM_LEDS 100
#define BRIGHTNESS 255
#define BRIGHTNESS_LEVELS 4;
#define NUM_COLORS 7;

const int brightness_levels[] = {25, 50, 85, 150};

// For led chips like WS2812, which have a data line, ground, and power, you just
// need to define data_pin.  For led chipsets that are SPI based (four wires - data, clock,
// ground, and power), like the LPD8806 define both data_pin and clock_pin
// Clock pin only needed for SPI based chipsets when not using hardware SPI
const int data_pin = 2;
const int clock_pin = 13;
const int button_1_pin = 2;

// Define the array of leds
CRGB leds[NUM_LEDS];

// To store last time LED was updated
long previousMillis = 0;

// Sample time (milliseconds)
unsigned long interval = 100;          

void setup() {
  // Uncomment/edit one of the following lines for your leds arrangement.
  // ## Clockless types ##
  // FastLED.addLeds<NEOPIXEL, data_pin>(leds, NUM_LEDS);  // GRB ordering is assumed
  // FastLED.addLeds<SM16703, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<TM1829, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<TM1812, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<TM1809, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<TM1804, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<TM1803, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<UCS1903, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<UCS1903B, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<UCS1904, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<UCS2903, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<WS2812, data_pin, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  // FastLED.addLeds<WS2852, data_pin, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  // FastLED.addLeds<WS2812B, data_pin, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  // FastLED.addLeds<GS1903, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<SK6812, data_pin, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  // FastLED.addLeds<SK6822, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<APA106, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<PL9823, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<SK6822, data_pin, RGB>(leds, NUM_LEDS);
  FastLED.addLeds<WS2811, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<WS2813, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<APA104, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<WS2811_400, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<GE8822, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<GW6205, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<GW6205_400, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<LPD1886, data_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<LPD1886_8BIT, data_pin, RGB>(leds, NUM_LEDS);
  // ## Clocked (SPI) types ##
  // FastLED.addLeds<LPD6803, data_pin, clock_pin, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  // FastLED.addLeds<LPD8806, data_pin, clock_pin, RGB>(leds, NUM_LEDS);  // GRB ordering is typical
  // FastLED.addLeds<WS2801, data_pin, clock_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<WS2803, data_pin, clock_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<SM16716, data_pin, clock_pin, RGB>(leds, NUM_LEDS);
  // FastLED.addLeds<P9813, data_pin, clock_pin, RGB>(leds, NUM_LEDS);  // BGR ordering is typical
  // FastLED.addLeds<DOTSTAR, data_pin, clock_pin, RGB>(leds, NUM_LEDS);  // BGR ordering is typical
  // FastLED.addLeds<APA102, data_pin, clock_pin, BGR>(leds, NUM_LEDS);  // BGR ordering is typical
  // FastLED.addLeds<SK9822, data_pin, clock_pin, RGB>(leds, NUM_LEDS);  // BGR ordering is typical

  // Set up the builtin LED
  pinMode(LED_BUILTIN, OUTPUT);
  // Light the LED on the Teensy board to show the board
  // is working
  digitalWrite(LED_BUILTIN, HIGH);

  // initialize the pushbutton pin as an input:
  pinMode(button_1_pin, INPUT);

  // Set maximum power consumption
  FastLED.setMaxPowerInVoltsAndMilliamps(5, 2000);

}

int i;
int brightness_level = 1;
int button1_state = 0;
int button1_pressed = 0;
int current_color = 0;
uint32_t colors[] = {
  CRGB::Red, CRGB::Green, CRGB::Blue, 
  CRGB::Yellow, CRGB::Magenta, CRGB::Cyan,
  CRGB::White
};


void loop() {

  // read the state of the pushbutton value:
  button1_state = digitalRead(button_1_pin);

  // Check if the pushbutton was pressed. 
  // If it was, the buttonState will be LOW:
  if (button1_state == LOW) {
    // Light LED to confirm button was pressed
    digitalWrite(LED_BUILTIN, HIGH);
    if (button1_pressed == 0) {
      button1_pressed = 1;
    }
  } else {
    // turn LED off:
    digitalWrite(LED_BUILTIN, LOW);
  }

  unsigned long currentMillis = millis();
  if(currentMillis - previousMillis > interval) {

    if (button1_pressed == 1) {
      // Increment brightness level:
      brightness_level = (brightness_level + 1) % BRIGHTNESS_LEVELS;
      button1_pressed = 2;  // button not ready
      if (brightness_level == 0) {
        // Cycle through colors
        current_color = (current_color + 1) % NUM_COLORS;
      }
    } else {
      if (button1_state == HIGH) {
        button1_pressed = 0;  // button reset
      }
    }

    // Set the LED brightness
    FastLED.setBrightness(brightness_levels[brightness_level]);

    // Turn on all LEDs
    for (i=0; i < NUM_LEDS; i++) {
      leds[i] = colors[current_color];
    }
    FastLED.show();

    previousMillis = currentMillis;
  }
}
