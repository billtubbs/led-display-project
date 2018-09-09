# display1593
Driver code and other documentation for an irregular 1593-LED 
light display screen.

**Construction of irregular LED display**

<IMG SRC="images/160505photo_ledproject03_cropped.jpg" WIDTH=400>

The 1593-LED irregular light array contains two [Teensy 3.1 microcontrollers](https://www.pjrc.com/teensy/teensy31.html) mounted on OctoWS2811 adaptor boards communicating with 16 led strips (8 strips connected to each Teensy).

Each strip contains around 98 to 100 5V [WS2811 RGB LEDs](https://www.aliexpress.com/item/DC5V-WS2811-pixel-node-50node-a-string-non-waterproof-SIZE-13mm-13mm/1624010105.html) arranged in an irregular pattern on a 4x4 foot display (1.2 x 1.2 metres).

## Design documents
* [dwg.150406_final.pdf](https://github.com/billtubbs/led-display-project/blob/master/dwg.150406_final.pdf) - Arrangement drawing of the LED mounting plates

The Teensy driver code uses the OctoWS2811 LED Library by Paul Stoffregen:
* https://www.pjrc.com/teensy/td_libs_OctoWS2811.html

The Teensy microcontrollers are connected to a [Raspberry Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero/).
For a photo of the completed display and more information on the Raspberry Pi code and some of the display projects, see this separate repository:
* https://github.com/billtubbs/display1593/

