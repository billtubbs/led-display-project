/*  This is a variation on the Basic RGB LED Test provided
    by Paul Stoffregen:
    http://www.pjrc.com/teensy/td_libs_OctoWS2811.html

    This scipt listens for commands coming in on the serial port 
    (e.g. from a Raspberry Pi) and makes updates to the LED 
    display accordingly.
    
    The 1593-LED irregular light array contains two Teensy 3.1
    microcontrollers mounted on OctoWS2811 Adaptor boards for 
    communication with the 16 led strips (8 on each Teensy) 
    containing 98 to 100 LEDs per strip. 

    Required Connections
    --------------------
      pin 2:  LED Strip #1    OctoWS2811 drives 8 LED Strips.
      pin 14: LED strip #2    All 8 are the same length.
      pin 7:  LED strip #3
      pin 8:  LED strip #4    A 100 ohm resistor should used
      pin 6:  LED strip #5    between each Teensy pin and the
      pin 20: LED strip #6    wire to the LED strip, to minimize
      pin 21: LED strip #7    high frequency ringing & noise.
      pin 5:  LED strip #8
      pin 15 & 16 - Connect together, but do not use
      pin 4 - Do not use
      pin 3 - Do not use as PWM.  Normal use is ok.

*/

// REMEMBER TO CHANGE THE FOLLOWING LINE WHEN COMPILING AND 
// UPLOADING THIS CODE TO THE TEENSY.
// Set which Teensy controller the code is for (1 or 2)
#define TEENSY1

#include <OctoWS2811.h>
#include <avr/pgmspace.h>
#include <stdio.h>

// Include constants and data describing the LED 
// arrangement etc.
#include "arraydata.h"

// Define display refresh rate (ms)
#define INTERVAL 100

// Pin number for on-board LED
#define BOARDLED 13

// These constants reflect my LED strip setup for
// Teensy Number 1:

#ifdef TEENSY1
// The following data is specific to the LEDS
// connected to Teensy #1
const unsigned short numLeds = 798;
const unsigned short numberOfStrips = 8;
const unsigned short ledsPerStrip[] = {100, 98, 100, 100, 100, 100, 100, 100};
const unsigned short firstLedOfStrip[] = {0, 100, 198, 298, 398, 498, 598, 698, 798};
const unsigned short maxLedsPerStrip = 100;

// Lookup array to translate a display led number 
// (range 0 to 1592) to a teensy led number (range
// 0 to 799 for Teensy #1, 0 to 797 for Teensy #2).
const unsigned short lookupTable[] = {
  0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
  20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 
  40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 
  60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 
  80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 
  100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 
  116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 
  132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 
  148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 
  164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 
  180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 
  196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 
  212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 
  228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 
  244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 
  260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 
  276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 
  292, 293, 294, 295, 296, 297, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 
  310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 
  326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 
  342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 
  358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 
  374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 
  390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 
  406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 
  422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 
  438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 
  454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 
  470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 
  486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 
  502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 
  518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 
  534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 
  550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 
  566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 
  582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 
  598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 
  614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 
  630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 
  646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 
  662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 
  678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 
  694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 
  710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 
  726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 
  742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 
  758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 
  774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 
  790, 791, 792, 793, 794, 795, 796, 797, 798, 799
};

#endif


// These constants reflect my LED strip setup for
// Teensy Number 2:

#ifdef TEENSY2
// The following data is specific to the LEDS
// connected to Teensy #1
const unsigned short numLeds = 795;
const unsigned short numberOfStrips = 8;
const unsigned short ledsPerStrip[] = {99, 99, 100, 100, 99, 100, 100, 98};
const unsigned short firstLedOfStrip[] = {0,  99, 198, 298, 398, 497, 597, 697, 795};
const unsigned short maxLedsPerStrip = 100;

// Lookup array to translate a display led number 
// (range 0 to 1592) to a teensy led number (range
// 0 to 799 for Teensy #1, 0 to 797 for Teensy #2).
const unsigned short lookupTable[] = {
  0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
  20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 
  40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 
  60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 
  80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 100, 
  101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 
  117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 
  133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 
  149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 
  165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 
  181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 
  197, 198, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 
  214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 
  230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 
  246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 
  262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 
  278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 
  294, 295, 296, 297, 298, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 
  311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 
  327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 
  343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 
  359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 
  375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 
  391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 
  407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 
  423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 
  439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 
  455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 
  471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 
  487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 
  503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 
  519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 
  535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 
  551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 
  567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 
  583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 
  599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 
  615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 
  631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 
  647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 
  663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 
  679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 
  695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 
  711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 
  727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 
  743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 
  759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 
  775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 
  791, 792, 793, 794, 795, 796, 797
};

#endif

DMAMEM int displayMemory[maxLedsPerStrip*6];
int drawingMemory[maxLedsPerStrip*6];

// Make sure this configuration is right for your LED strips
const int config = WS2811_RGB | WS2811_800kHz;

OctoWS2811 leds(maxLedsPerStrip, displayMemory, drawingMemory, config);

// Variables to track time and flash the board led:
int ledState = LOW;         // ledState used to set the LED
long previousMillis = 0;    // will store last time display was refreshed



void setup() {
  
  // Setup code (only runs once at startup)
  
  // Initialize serial communication and set baud rate
  Serial.begin(38400);
  
  // Setup pins
  pinMode(BOARDLED, OUTPUT);
  
  leds.begin();
  leds.show();

}


unsigned short incomingByte = 0;
unsigned short ledNum;
char colR, colG, colB;
unsigned int col;


void loop() {
  
  short unsigned i, n;
  const unsigned short *p;
  
  // Check if data received on serial port
  // and if so read it in
  if (Serial.available()) {
    incomingByte = Serial.read();  // will not be -1
  
    switch(incomingByte)  // see what was sent to the board
    {

      // Update one LED value if the 
      // character 'S' was sent
      case 'S':
        ledNum = int((Serial.read() << 8) + Serial.read());
        colR = int(Serial.read());
        colG = int(Serial.read());
        colB = int(Serial.read());
        leds.setPixel(lookupTable[ledNum], colR, colG, + colB);
        break;
        
      // Update one LED value if the 
      // character 'T' was sent - uses teensy led number 
      case 'T':
        ledNum = int((Serial.read() << 8) + Serial.read());
        colR = int(Serial.read());
        colG = int(Serial.read());
        colB = int(Serial.read());
        leds.setPixel(ledNum, colR, colG, + colB);
        break;
        
      // Update all LED values (on this Teensy)
      // if the character 'A' was sent
      case 'A':
        for(i = 0, p = lookupTable; i<numLeds; i++, p++) {
          colR = int(Serial.read());
          colG = int(Serial.read());
          colB = int(Serial.read());
          leds.setPixel(*p, colR, colG, colB);
        }
        break;

      // Update a batch of n LED values if the 
      // character 'N' was sent
      case 'N':
        n = int((Serial.read() << 8) + Serial.read());
        for(i = 0; i<n; i++) {
          ledNum = int((Serial.read() << 8) + Serial.read());
          colR = int(Serial.read());
          colG = int(Serial.read());
          colB = int(Serial.read());
          leds.setPixel(lookupTable[ledNum], colR, colG, colB);
        }
        break;

      // Get the value of an LED and return it
      // if the character 'G' was sent
      case 'G':
        ledNum = int((Serial.read() << 8) + Serial.read());
        col = leds.getPixel(lookupTable[ledNum]);
        Serial.write((col >> 16) & 0xff);
        Serial.write((col >> 8) & 0xff);
        Serial.write(col & 0xff);

      // Clear screen (to black) if the 
      // character 'C' was sent
      case 'C':
        for(i = 0; i<(numberOfStrips*maxLedsPerStrip); i++) {
          leds.setPixel(i, 0);
        }
        break;
    
      // Send identification message in response
      // if the character 'I' was sent
      case 'I':
        n = Serial.read();
        if(n == 'D') {

          #ifdef TEENSY1
          Serial.write("Teensy1\n");
          #endif

          #ifdef TEENSY2
          Serial.write("Teensy2\n");
          #endif         

        }
        break;
      
    }
    
  }
  
  // check to see if it's time to begin a new
  // refresh of the LEDs (and blink the LED)
  unsigned long currentMillis = millis();
  
  if(currentMillis - previousMillis > INTERVAL) {
    // save the last time the LED blinked 
    previousMillis = currentMillis;   
    
    // Begin update of LEDs
    leds.show();
  
    // if the LED is off turn it on and vice-versa:
    ledState = (ledState == LOW)? HIGH : LOW;
    
    // set the LED with the ledState of the variable:
    digitalWrite(BOARDLED, ledState);
  }
  
}

