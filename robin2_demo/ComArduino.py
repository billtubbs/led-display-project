"""This Python script was converted from a JRuby program by Robin2 in March
2014 and shared on the Arduino forum. I converted it to Python 3.

Bill Tubbs
4 Apr 2025


This is designed to work with ... ArduinoPC.ino ...

The purpose of this program and the associated Arduino program is to 
    demonstrate a system for sending and receiving data between a PC and an 
    Arduino.

The key functions are:
    sendToArduino(ser, str) which sends the given string to the Arduino. The 
        string may contain characters with any of the values 0 to 255.

    recvFromArduino(ser) which returns an array.
        The first element contains the number of bytes that the Arduino said 
            it included in message. This can be used to check that the full 
            message was received.
        The second element contains the message as a string.

The overall process followed by the demo program is as follows
    open the serial connection to the Arduino - which causes the Arduino to 
        reset.
    wait for a message from the Arduino to give it time to reset.
    loop through a series of test messages
        send a message and display it on the PC screen
        wait for a reply and display it on the PC.

To facilitate debugging the Arduino code this program interprets any message 
    from the Arduino with the message length set to 0 as a debug message which
    is displayed on the PC screen.

The actual process of sending a message to the Arduino involves
    prefacing the message with a byte value of 254 (START_MARKER)
    following that START_MARKER with a byte whose value is the number of 
        characters in the original message
    then the message follows any bytes in the message with values of 253, 254
        or 255 into a pair of bytes  253 0   253 1  or 253 2 as appropriate
    suffixing the message with a byte value of 255 (END_MARKER).

Receiving a message from the Arduino involves
    waiting until the START_MARKER is detected
    saving all subsequent bytes until the end marker is detected
    converting the pairs of bytes (253 0 etc) back into the intended single 
        byte.


NOTES
    This program does not include any timeouts to deal with delays in 
        communication.

    For simplicity the program does NOT search for the comm port - the user 
        must modify the code to include the correct reference.
        search for the line "ser = serial.Serial("/dev/ttyS80", 57600)"

    The function bytesToString(str) is just a convenience to show the contents
        of a string as a series of byte values to make it easy to verify data
        with non-ascii characters.

    This program does NOT include a checkbyte that could be used to verify
        that there are no errors in the message. This could easily be added.

    As written the Arduino program can only receive a maximum of 16 bytes.
        This must include the start- and end-markers, the length byte and any
            extra bytes needed to encode values of 253 or over.
        the arduino program could easily be modified to accept longer messages
            by changing the line:
                #define maxMessage 16

    As written the Arduino program does NOT check for messages that are too 
        long
        it is assumed that the PC program will ensure compliance
        extra code could be added to the Arduino program to deal with too-
            long messages but it would add a lot of code that may confuse 
            this demo.

"""

import serial
import time


START_MARKER = 254
END_MARKER = 255
SPECIAL_BYTE = 253


#=====================================
#    Function Definitions
#=====================================

def sendToArduino(ser, sendStr):
    global START_MARKER, END_MARKER
    txLen = len(sendStr).to_bytes(length=1, byteorder='big')
    adjSendStr = encodeHighBytes(sendStr)
    adjSendStr = bytes([START_MARKER]) + txLen + adjSendStr + bytes([END_MARKER])
    ser.write(adjSendStr)


def recvFromArduino(ser):

    global START_MARKER, END_MARKER

    ck = []
    byteCount = -1  # the last increment will be one too many

    # wait for the start character
    while True:
        b = ser.read()
        if ord(b) == START_MARKER:
            break

    # save data until the end marker is found
    while True:
        ck.append(b)
        b = ser.read()
        byteCount += 1
        if ord(b) == END_MARKER:
            break

    # save the end marker byte
    ck.append(b)
    ck = b''.join(ck)

    returnData = []
    returnData.append(ck[1])
    returnData.append(decodeHighBytes(ck))
    # print(f"RETURNDATA {returnData[0]:s}")

    return(returnData)


def encodeHighBytes(inStr):

    global SPECIAL_BYTE

    outStr = []
    for x in inStr:
        if x >= SPECIAL_BYTE:
             outStr.append(SPECIAL_BYTE)
             outStr.append(x - SPECIAL_BYTE)
        else:
             outStr.append(x)
    outStr = bytes(outStr)

    # print("encINSTR    " + bytesToString(inStr))
    # print("encOUTSTR " + bytesToString(outStr))

    return(outStr)


def decodeHighBytes(inStr):

    global SPECIAL_BYTE

    outStr = []
    n = 0

    while n < len(inStr):
         if inStr[n] == SPECIAL_BYTE:
                n += 1
                x = SPECIAL_BYTE + inStr[n]
         else:
                x = inStr[n]
         outStr.append(x)
         n += 1
    outStr = bytes(outStr)

    print(f"decINSTR  {bytesToString(inStr):s}")
    print(f"decOUTSTR {bytesToString(outStr):s}")

    return(outStr)


def displayData(data):

    print(f"NUM BYTES SENT->   {data[1]:d}")
    print(f"DATA RECVD -> {bytesToString(data[2:-1]):s}")
    print(f"DATA RECVD BYTES-> {data[2: -1]!r}")


def bytesToString(data):

    return "-".join(str(x) for x in data)


def displayDebug(debugStr):

    print(f"DEBUG MSG-> {debugStr[2:-1]!r}")


def waitForArduino(ser):
    """Wait until the Arduino sends 'Arduino Ready' - allows time for Arduino
    reset. It also ensures that any bytes left over from a previous message are
    discarded.
    """

    global END_MARKER

    while True:

        while ser.in_waiting == 0:
            pass

        # wait until an end marker is received from the Arduino to make sure it is ready to proceed
        msg = []
        while True:  # gets the initial debugMessage
            x = ser.read()
            msg.append(x)
            if ord(x) == END_MARKER:
                break

        msg = b''.join(msg)
        displayDebug(msg)
        print()

        if msg.find(b"Arduino Ready") != -1:
            break


#======================================
# THE DEMO PROGRAM STARTS HERE
#======================================

def main():

    for _ in range(10):
        try:
            # NOTE the user must ensure that the next line refers to the correct comm port
            ser = serial.Serial("/dev/tty.usbmodem112977801", 57600)
            break
        except serial.serialutil.SerialException:
            print("Failed to open serial connection. Waiting to try again...")
            time.sleep(1)
    else:
        raise Exception("Could not establish serial connection. Gave up.")

    print("Waiting for Arduino...")
    waitForArduino(ser)

    print("Arduino is ready")

    testData = [
        b"abcde",
        b"zxcv1234",
        b"a" + bytes([16, 32, 0, 203]),
        b"b" + bytes([16, 32, 253, 255, 254, 253, 0]),
        b"fghijk"
    ]

    numLoops = len(testData)
    n = 0
    waitingForReply = False

    while n < numLoops:
        print(f"LOOP {n:d}")

        if ser.in_waiting == 0 and waitingForReply is False:
            teststr = testData[n]
            sendToArduino(ser, teststr)
            print("=====sent from PC==========")
            print(f"LOOP NUM {n:d}")
            print(f"DATA SENT -> {bytesToString(teststr):s}")
            print(f"TEST BYTES {teststr!r}")
            print("===========================")
            waitingForReply = True


        if ser.in_waiting > 0:
            dataRecvd = recvFromArduino(ser)

            if dataRecvd[0] == 0:
                displayDebug(dataRecvd[1])

            if dataRecvd[0] > 0:
                displayData(dataRecvd[1])
                assert teststr == dataRecvd[1][2:-1]
                print("Reply Received")
                n += 1
                waitingForReply = False

            print("\n===========\n")

            time.sleep(0.3)

    ser.close


if __name__ == "__main__":
    main()
