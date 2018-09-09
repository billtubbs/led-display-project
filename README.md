# display1593
Driver code and other documentation for an irregular 1593-LED 
light display screen.

**Construction of irregular LED display**

<IMG SRC="images/160505photo_ledproject03_cropped.jpg" WIDTH=400>

The 1593-LED irregular light array contains two [Teensy 3.1 microcontrollers](https://www.pjrc.com/teensy/teensy31.html) mounted on OctoWS2811 adaptor boards communicating with 16 led strips (8 strips connected to each Teensy).

Each strip contains around 98 to 100 DC5V WS2811 RGB LEDs arranged in an irregular pattern on a 5 x 5 foot display.

The Teensy driver code uses the OctoWS2811 LED Library by Paul Stoffregen:
* https://www.pjrc.com/teensy/td_libs_OctoWS2811.html

The Teensy microcontrollers are connected to a [Raspberry Pi Zero](https://www.raspberrypi.org/products/raspberry-pi-zero/).
For more information on the Raspberry Pi code and some of the display projects, see this separate repository:
* https://github.com/billtubbs/display1593/

