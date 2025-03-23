#include <FastLED.h>

#define LED_PIN     6
#define NUM_LEDS    7
#define PATTERN_LEN 6
#define BRIGHTNESS  32
#define LED_TYPE    WS2811
#define COLOR_ORDER RGB

// If you want the pattern to move across the strip, change this to
// a number greater than zero
#define UPDATES_PER_SECOND 1


CRGB leds[NUM_LEDS];
CRGB pattern[PATTERN_LEN] = { CRGB::Red, CRGB::Green, CRGB::Blue, CRGB::Yellow, CRGB::Cyan, CRGB::Magenta };

void setup() {
    delay( 3000 ); // power-up safety delay
    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
    FastLED.setBrightness( BRIGHTNESS );
}

void loop()
{
    // Start at the first LED
    static uint8_t startIndex = 0;

    // Apply the pattern repeating across all LEDs
    for( int i = 0; i < NUM_LEDS; i++) {
        leds[i] = pattern[(startIndex + i) % PATTERN_LEN];
    }

    // Apply the colors to the LED strip     
    FastLED.show();
    FastLED.delay(1000);

    if (UPDATES_PER_SECOND == 0) {
        // static display, sleep one second then
        // essentially apply the same LED settings
        // again
        FastLED.delay(1000);
    } else {
        // moving pattern 
        FastLED.delay(1000 / UPDATES_PER_SECOND);
        startIndex = (startIndex + 1) % NUM_LEDS;
    }
}