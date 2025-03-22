import serial
import time
from serial import SerialException


DEFAULT_BAUD_RATE = 921600
CONNECTION_REQUEST = ord('C')
CONNECTION_REQUEST_RESPONSE = ord('R')


def open_serial_connections(ports, baud_rate=DEFAULT_BAUD_RATE):
    serial_conns = {}
    for i, port in ports.items():
        try:
            ser = serial.Serial(
                port=port, baudrate=baud_rate, timeout=2.0
            )
        except SerialException:
            continue
        serial_conns[i] = ser
    return serial_conns


def wait_for_serial_input(ser, timeout=5.0):
    t = time.time()
    while ser.in_waiting == 0:
        if time.time() - t > timeout:
            return 1, "timeout"
    return 0, ""


def establish_communication(
    ser,
    conn_code=CONNECTION_REQUEST,
    conn_response_code=CONNECTION_REQUEST_RESPONSE,
    timeout=5.0
):
    ser.reset_input_buffer()
    status, msg = wait_for_serial_input(ser, timeout=timeout)
    if status == 1:
        return 1, None, "gave up waiting for device to send data"
    b = int.from_bytes(ser.read())
    if b == conn_code:
        ser.write(conn_code.to_bytes())
        status, msg = wait_for_serial_input(ser, timeout=timeout)
        if status == 1:
            return 2, None, "gave up waiting for response to connection request"
        c, device_id = ser.read(2)
        if c != CONNECTION_REQUEST_RESPONSE:
            return 3, None, "incorrect response to connection request"
        return 0, device_id, ""
    return 2, None, "device sending data but not requesting new connection"


def serial_monitor(serial_conns):
    while True:
        for i, ser in serial_conns.items():
            if ser.in_waiting > 0:
                b = int.from_bytes(ser.read())
                print(f"{i}: {chr(b)}")
