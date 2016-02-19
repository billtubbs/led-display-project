# This script loads an image from the current working
# directory and translates it into LED intensity array
# for display on the 1593 LED irregular display I
# built



# Teensy command list

# 'I' - Send identification message in response
# 'S' - Set the colour of one LED
# 'N' - Update a batch of n LED colours
# 'A' - Update all LED colours
# 'G' - Get the colour of an LED and return it
# 'C' - Clear screen (to black)

import serial
import time
import numpy as np
from scipy import ndimage
from scipy import misc
from scipy import version

from itertools import izip
import image_data
import ledArray_data_1593 as leds


class Teensy(object):

    def __init__(self, address, baud=38400):

        self.address = address
        self.baud = baud
        self.serial = None
        self.name = None

    def connect(self):

        # Establish connection
        self.serial = serial.Serial(self.address, self.baud)
        self.serial.open()

        # Request identification
        self.serial.write('ID\n')

        result = False
        try:
            response = self.serial.readline().rstrip()
        except:
            print "Connection to", self.address, "failed."
            self.serial.close()
            return result

        if response.startswith("Teensy"):
            self.name = response
            print "Connection to", self.address, "(" + \
                  response + ") successful."
            result = True

        return result

    def __repr__(self):

        return "Teensy('%s', baud=%d)" % (self.address, self.baud)


# Connection details

# These are specific to the computer you are running
# this code on

# To identify new devices connected to Raspberry Pi USB ports
# type lsusb into the shell

# Example:
# Bus 001 Device 006: ID 16c0:0483 VOTI Teensyduino Serial
# Bus 001 Device 005: ID 16c0:0483 VOTI Teensyduino Serial

# To find the port name of each Teensy use the following with
# and without the Teensies plugged in:
# ls /dev/tty*

addresses = ('/dev/ttyACM0', '/dev/ttyACM1')

def setLed(controllers, led, col):
    """Set colours of an individual LED."""

    ledRef = leds.ledIndex[led]
    id = ledRef[1]
    controllers[ledRef[0]].serial.write('T' + chr(id >> 8) + chr(id % 256) \
        + chr(col[0]) + chr(col[1]) + chr(col[2]) +'\n')
    #print "Led %d set to 0x%2x%2x%2x [t%d: %d]" % (led, col[0], col[1], col[2], ledRef[0], id)


def setLeds(controllers, ledIDs, cols):
    """Set colours of a batch of n LEDs."""

    if len(cols) != len(ledIDs):
        print "ERROR: ledIDs and cols must be sequences of equal length."
        return False

    # prepare two lists to accumulate colour values
    # destined for each controller and a count of each
    s = [[0, list()], [0, list()]]

    for i, col in izip(ledIDs, cols):
        #ledRef = leds.ledIndex[i]
        ledRef = i
        s[ledRef[0]][0] += 1
        id = ledRef[1]
        s[ledRef[0]][1].append(chr(id >> 8))
        s[ledRef[0]][1].append(chr(id % 256))
        for c in range(3):
            s[ledRef[0]][1].append(chr(col[c]))

    for i in range(leds.numberOfControllers):
        n = s[i][0]
        controllers[i].serial.write('N' + chr(n >> 8) + chr(n % 256))
        controllers[i].serial.write("".join([item for item in s[i][1]]))

        print s[i][0], "leds set on Teensy", i

    return s


def setAllLeds(controllers, cols):

    if len(cols) != leds.numCells:
        print "ERROR: setAllLeds() requires a sequence of", \
            leds.numCells, "colours."
        return False

    start = 0

    for controller in controllers:
        controller.serial.write('A')

        finish = start + leds.numLeds[controller]
        for col in cols[start:finish]:

            controller.serial.write(chr(col[0]) + chr(col[1]) + chr(col[2]))
            n += 1

    print finish, "leds set"

    return True


def clearLeds(controllers):

    for controller in controllers:
        controller.serial.write('C')


def connect(addresses=addresses):

    print "Trying to connect to Teensies..."

    tys = []
    for a in addresses:
        tys.append(Teensy(a))

    for t in tys:
        t.connect()

    if tys[0].name == 'Teensy2':
        tys[0], tys[1] = (tys[1], tys[0])
        print "(Teensies swapped)"

    if (tys[0].name, tys[1].name) != ('Teensy1', 'Teensy2'):
        print "Correct teensies not found."
        quit()

    return tys

def process_image(image):

    print "Processing image ", image.shape

    # Find out how many layers the image has
    image_shape = image.shape[:2]
    if len(image.shape)>2:
        imageCols = image.shape[2]
    else:
        imageCols = 1

    data_type = image.dtype

    # Reduce redundant layers - if imageCols > 1,
    # assume first three are red, green, blue and
    # ignore the rest

    if imageCols > 3:
        image = image[:,:,:3]
        imageCols = image.shape[2]
        print "Image reduced to %d layers (R, G, B)" % imageCols

    # Determine smallest dimension (x or y)
    imageSize = min(image_shape)

    if not image_shape[0] == image_shape[1]:
        if image_shape[0] > imageSize:
            print "Image is not square.  Y-axis will be cropped."
            y = (image_shape[0] - imageSize)/2
            image = image[:][y:y+imageSize]
        elif image_shape[1] > imageSize:
            print "Image is not square.  X-axis will be cropped."
            x = (image_shape[1] - imageSize)/2
            image = image[:, x:x+imageSize, :]

        imageShape = image.shape[:2]
        print "Cropped image size: %dx%d" % (image_shape[0], image_shape[1])

    # Define arrays for maximum colour intensities
    # of final image

    cols = ['red', 'green', 'blue']

    if imageCols > 1:
        maxInt = np.zeros((imageCols), dtype = 'uint8')
        for i in range(imageCols):
            selCol = np.array([i], dtype=np.intp)
            colMin = image[:, :, selCol].min()
            colMax = image[:, :, selCol].max()
            print "Colour %d range: %d to %d" % (i, \
                colMin, colMax)
            maxInt[i] = max(255,colMax)
    else:
        print "This is a black and white image."
        print "Intensity range: %d to %d" % (image.min(), image.max())
        print "Specify RGB intensities for final image (0-31):"

        maxInt = np.zeros((3), dtype = 'uint8')
        for i, c in enumerate(cols):
            while True:
                s = raw_input(c + ": ")
                try:
                    f = float(s)
                except:
                    print "Enter a number between 0 and 255"
                    continue
                maxInt[i] = f
                break
    # Re-size image to required pixel size for super-sampling
    # algorithm

    pixels = 256

    # Re-size image for super-sampling
    s_image = misc.imresize(
        image,
        (pixels, pixels),
        interp='bilinear',
        mode=None
    )
    print "Image re-sized:", s_image.shape[:2]

    # Initialise LED Display variables
    numCells = 1593
    width, height = (2000, 2000)
    if imageCols > 1:
        z = np.zeros((imageCols, numCells), dtype = int)
    else:
        z = np.zeros((3, numCells), dtype = int)


    # load masks containing mapping information from module file
    import masks

    print "Image masks loaded"

    # Process led intensities using mapping arrays
    for i in range(numCells):
        if imageCols > 1:
            for c in range(imageCols):
                l = ((masks.i_mask[0] == i)*s_image[:, :, c]).sum()/masks.pixel_counts[i]
                z[c][i] = l/255*maxInt[c]
        else:
            l = ((masks.i_mask[0] == i)*s_image[:, :]).sum()/masks.pixel_counts[i]
            for c in range(3):
                z[c][i] = l/255*maxInt[c]

    print "LED intensities calculated"

    for i in range(imageCols):
        colMin = z.min()
        colMax = z.max()
        print "Colour %d range: %d to %d" % (i, \
            colMin, colMax)


    return z


# --------------------- START OF MAIN FUNCTION ---------------------


def main():

    print "------------ LED Display Controller Test ------------"

    print "Numpy version", np.version.version
    print "Scipy version", version.version

    tys = connect()

    filename = 'map.png'

    img = ndimage.imread(filename)

    z = process_image(img)

    #z = image_data.map

    print "Array loaded:", z.shape

    np.savetxt("image_digits.txt", z, fmt='%d')

    i = 0
    str = ""
    col = 0

    #z = np.loadtxt("image_data.txt")

    for j in range(1593):

        r = int(z[0][j])/2
        g = int(z[1][j])/2
        b = int(z[2][j])/3

        setLed(tys, j, (r, g, b))


# ------------------------- END OF MAIN CODE ------------------------


if __name__ == '__main__':  main()



