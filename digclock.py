# Code to load digit data and light
# leds

from scipy import misc
import display1593 as display
import pickle
from datetime import datetime

with open('digdata.pickle', 'rb') as handle:
    dig_data = pickle.load(handle)

print "data for %d digit segments unpickled." % (len(dig_data))

d_chars = {
        0: [0, 1, 2, 4, 5, 6],
        1: [5, 6],
        2: [1, 2, 3, 4, 5],
        3: [2, 3, 4, 5, 6],
        4: [0, 3, 5, 6],
        5: [0, 2, 3, 4, 6],
        6: [0, 1, 2, 3, 4, 6],
        7: [2, 5, 6],
        8: [0, 1, 2, 3, 4, 5, 6],
        9: [0, 2, 3, 4, 5, 6],
        10: [7]
        }


# Initialise display memory
smem = [0]*1593
smem_prev = [-1]*1593

# Digits
#  dig_data[1]
#  dig_data[2]
#  dig_data[3]
#  dig_data[4]
# Points:
#  dig_data[0]

# brightness values
bcycle = {
    0: 9,
    1: 9,
    2: 9,
    3: 9,
    4: 9,
    5: 9,
    6: 9,
    7: 8,
    8: 7,
    9: 6,
    10: 5,
    11: 4,
    12: 4,
    13: 4,
    14: 4,
    15: 4,
    16: 5,
    17: 6,
    18: 7,
    19: 8,
    20: 9,
    21: 9,
    22: 9,
    23: 9
}

# Get current time
t = datetime.now().time()
hr, min = (t.hour, t.minute)
d4, d3 = (hr / 10), (hr % 10)
d2, d1 = (min / 10), (min % 10)

# Connect to Teensies
tys = display.connect()

# Set display dimmer level
bness = bcycle[hr % 24]

# Set colour for points
for n in range(2):
    for i, x in dig_data[0][n].iteritems():
        smem[i] = x/bness

# Set colour for digit 4
for n in d_chars[d4]:
    for i, x in dig_data[1][n].iteritems():
        smem[i] += x/bness

# Set colour for digit 3
for n in d_chars[d3]:
    for i, x in dig_data[2][n].iteritems():
        smem[i] += x/bness

# Set colour for digit 2
for n in d_chars[d2]:
    for i, x in dig_data[3][n].iteritems():
        smem[i] += x/bness

while True:

    # Set colour for digit 1
    for n in d_chars[d1]:
        for i, x in dig_data[4][n].iteritems():
            smem[i] += x/bness

    for i in range(1593):
        if smem[i] != smem_prev[i]:
            display.setLed(tys, i, (smem[i], 0, 0))
            smem_prev[i] = smem[i]

    t = datetime.now().time()
    min = t.minute
    hr = t.hour
    s = t.second

    print "%2d:%2d " % (hr, min)

    while t.minute == min:
        while datetime.now().time().second == s:
            pass
        for n in range(2):
            for i, x in dig_data[0][n].iteritems():
                display.setLed(tys, i, ((s % 2)*x/bness, 0, 0))
        t = datetime.now().time()
        s = t.second

    min = (min + 1) % 60
    if min == 0:
        hr = (hr + 1) % 24

    # Set value for digits 1
    d1 = (min % 10)

    if d1 == 0:

        # Set value for digits 1
        d2 = (min / 10)

        for n in range(7):
            for i, x in dig_data[3][n].iteritems():
                smem[i] = 0

        for n in d_chars[d2]:
            for i, x in dig_data[3][n].iteritems():
                smem[i] = x/bness

    if min == 0:

        # Set display dimmer level
        bness = bcycle[hr % 24]

        # Set values for digits 3 and 4
        d4, d3 = (hr / 10), (hr % 10)

        for n in range(7):
            for i, x in dig_data[2][n].iteritems():
                smem[i] = 0

        for n in d_chars[d3]:
            for i, x in dig_data[2][n].iteritems():
                smem[i] = x/bness

        for n in range(7):
            for i, x in dig_data[1][n].iteritems():
                smem[i] = 0

        for n in d_chars[d4]:
            for i, x in dig_data[1][n].iteritems():
                smem[i] = x/bness

    for n in range(7):
        for i, x in dig_data[4][n].iteritems():
            smem[i] = 0