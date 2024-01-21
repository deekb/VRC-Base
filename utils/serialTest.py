"""
This file is just a quick attempt at reverse-engineering the vex brain's communications protocol in order to make a tool that works on linux
I gave up and decided to just use an SD card to transfer programs (hence the deploy.py script), however, if you would like to develop this
into a full project, please contact me and I will help
"""


import time

import serial
import serial.tools.list_ports
import binascii


class DeviceNotFound(serial.SerialException):
    pass


# Parameters to determine if a device is a Vex Brain communications Port
VEX_BRAIN_PROGRAMMER_PORT_VID = 10376
VEX_BRAIN_PROGRAMMER_PORT_PID = 1281
VEX_BRAIN_PROGRAMMER_PORT_DESCRIPTION = "VEX Robotics Communications Port"
VEX_BRAIN_PROGRAMMER_PORT_BAUD_RATE = 115200
VEX_BRAIN_PROGRAMMER_PORT_TIMEOUT = 0.5
VEX_BRAIN_PROGRAMMER_PORT = None

# Iterate through all devices and determine which one (if any) is the vex brain
for device in serial.tools.list_ports.comports():
    if (
        device.interface == VEX_BRAIN_PROGRAMMER_PORT_DESCRIPTION
        and device.vid == VEX_BRAIN_PROGRAMMER_PORT_VID
        and device.pid == VEX_BRAIN_PROGRAMMER_PORT_PID
    ):
        VEX_BRAIN_PROGRAMMER_PORT = device.device

# Ensure that we have a device to operate on
if VEX_BRAIN_PROGRAMMER_PORT is None:
    raise DeviceNotFound(
        "Could not find an attached device with the specified properties"
    )

# Status message constants
STATUS_SUCCESS = 1
STATUS_PROGRAM_NOT_FOUND = 2
STATUS_PACKET_VALIDATION_ERROR = 3
STATUS_UNKNOWN_ERROR = 4

# The identifier used to indicate the start of a message (Not sure of more details on this one)
MESSAGE_START_IDENTIFIER = b"\xc9\x36\xb8\x47\x56\x18\x1a\x01\x00"
STATUS_MESSAGE_PREFIX = b"\xaa\x55\x56\x04\x18"

# A dictionary relating different status messages to their assumed meaning
PROGRAM_START_STATUS = {
    STATUS_MESSAGE_PREFIX + b"\x76\x4b\xa6": STATUS_SUCCESS,
    STATUS_MESSAGE_PREFIX + b"\xff\x4b\x07": STATUS_PROGRAM_NOT_FOUND,
    STATUS_MESSAGE_PREFIX + b"\xce\x6d\x75": STATUS_PACKET_VALIDATION_ERROR,
}

"""
SUCCESS:            01110110 01001011 10100110
NOT FOUND:          11111111 01001011 00000111
VALIDATION ERROR    11001110 01101101 01110101
"""


class VexBrainCommunication(object):
    def __init__(self, port, baud_rate=115200, timeout=0.25):
        self.serial_connection = serial.Serial(port, baud_rate, timeout=timeout)
        print(
            f"VexBrainCommunication: Connected to vex brain on port: {port} with baud rate: {baud_rate}"
        )

    def send(self, data):
        self.serial_connection.write(data)

    def get(self):
        received_message = bytes()
        while True:
            received_message_part = self.serial_connection.read()
            if received_message_part:
                received_message += received_message_part
            else:
                return received_message

    @staticmethod
    def crc16_xmodem(data):
        return binascii.crc_hqx(data, 0)

    def append_crc16_xmodem(self, data):
        # Calculate the CRC (cyclic redundancy check) value for the given bytearray using the crc16_xmodem algorithm
        crc_int = self.crc16_xmodem(data)
        # Convert the crc to hex data
        crc_bytes = crc_int.to_bytes(length=2, byteorder="big")
        # And return the bytearray with the appended CRC
        return data + crc_bytes

    def get_start_program_message(self, slot):
        message = MESSAGE_START_IDENTIFIER

        # Append ___s_{integer left-padded to 2 digits using zeros}.bin to the message
        message += b"___s_" + str(slot - 1).rjust(2, "0").encode() + b".bin"

        message += b"\x00" * 13

        # Ensure we append the CRC to the message
        return self.append_crc16_xmodem(message)

    def start_program(self, slot):
        print(self.get_start_program_message(slot))
        self.send(self.get_start_program_message(slot))
        return PROGRAM_START_STATUS.get(self.get(), STATUS_UNKNOWN_ERROR)

    def close_connection(self):
        print("Closing connection to vex brain")
        self.serial_connection.close()


vex_brain = VexBrainCommunication(
    VEX_BRAIN_PROGRAMMER_PORT,
    VEX_BRAIN_PROGRAMMER_PORT_BAUD_RATE,
    VEX_BRAIN_PROGRAMMER_PORT_TIMEOUT,
)

# print(vex_brain.crc16_xmodem(open("outfile.raw", "rb").read()).to_bytes(length=2, byteorder="big"))

# vex_brain.send(open("Captures/FIRST_3", "rb").read())
# time.sleep(1)
# vex_brain.send(open("Captures/LAST_12", "rb").read())

vex_brain.start_program(1)

# vex_brain.send(open("Captures/1", "rb").read())
# vex_brain.send(open("Captures/2", "rb").read())
# vex_brain.send(open("Captures/3", "rb").read())
# time.sleep(1)
# vex_brain.send(open("Captures/4", "rb").read())
# vex_brain.send(open("Captures/5", "rb").read())
# vex_brain.send(open("Captures/6", "rb").read())
# vex_brain.send(open("Captures/7", "rb").read())
# vex_brain.send(open("Captures/8", "rb").read())
# vex_brain.send(open("Captures/9", "rb").read())
# vex_brain.send(open("Captures/10", "rb").read())
# vex_brain.send(open("Captures/11", "rb").read())
# vex_brain.send(open("Captures/12", "rb").read())
# vex_brain.send(open("Captures/13", "rb").read())
# vex_brain.send(open("Captures/14", "rb").read())
# vex_brain.send(open("Captures/15", "rb").read())


# vex_brain.send(b"\xc9\x36\xb8\x47\x21")
# vex_brain.send(
#     b"\xc9\x36\xb8\x47\x56\x19\x1a\x40\x00\x70\x79\x74\x68\x6f\x6e\x5f\x76\x6d\x2e\x62\x69\x6e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc2\xc6"
# )
# time.sleep(1)
# vex_brain.send(b"\xc9\x36\xb8\x47\x21")
# vex_brain.send(
#     b"\xc9\x36\xb8\x47\x56\x11\x34\x01\x01\x01\x01\x72\x01\x00\x00\x00\x00\x00\x07\xaf\xce\xac\x06\x69\x6e\x69\x00\xce\x83\x6d\x2c\x01\x00\x00\x00\x73\x6c\x6f\x74\x5f\x31\x2e\x69\x6e\x69\x00\x00\x00\x00\x00\x00"
# )
# vex_brain.send(b"\x00\x00\x00\x00\x00\x00\x00\x00\xf9\xc1")
# vex_brain.send(
#     b"\xc9\x36\xb8\x47\x56\x13\x81\x78\x00\x00\x00\x07\x3b\x0a\x3b\x20\x56\x45\x58\x20\x70\x72\x6f\x67\x72\x61\x6d\x20\x69\x6e\x69\x20\x66\x69\x6c\x65\x0a\x3b\x20\x43\x6f\x70\x79\x72\x69\x67\x68\x74\x20\x28\x63\x29\x20\x32\x30\x31\x37\x2d\x32\x30\x32\x31\x20\x56\x45\x58\x20\x52\x6f\x62\x6f\x74\x69\x63\x73\x0a\x3b\x0a\x5b\x70\x72\x6f\x6a\x65\x63\x74\x5d\x0a\x76\x65\x72\x73\x69\x6f\x6e\x20\x20\x20\x20\x20\x20\x3d\x20\x22\x31\x22\x0a\x69\x64\x65\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x3d\x20\x22\x50\x79\x74\x68\x6f\x6e\x22\x0a\x66\x69\x6c\x65\x20\x20\x20\x20\x20\x20\x20\x20\x20\x3d\x20\x22\x6e\x6f\x6e\x65\x22\x0a\x3b\x0a\x5b\x70\x72\x6f\x67\x72\x61\x6d\x5d\x0a\x76\x65\x72\x73\x69\x6f\x6e\x20\x20\x20\x20\x20\x20\x3d\x20\x22\x31\x22\x0a\x6e\x61\x6d\x65\x20\x20\x20\x20\x20\x20\x20\x20\x20\x3d\x20\x22\x56\x45\x58\x63\x6f\x64\x65\x20\x50\x72\x6f\x6a\x65\x63\x74\x22\x0a\x73\x6c\x6f\x74\x20\x20\x20\x20\x20\x20\x20\x20\x20\x3d\x20\x22\x30\x22\x0a\x69\x63\x6f\x6e\x20\x20\x20\x20\x20"
# )
# vex_brain.send(b"\x20\x20\x20\x20\x3d\x20\x22\x55\x53\x45")
# vex_brain.send(
#     b"\x52\x39\x32\x35\x78\x2e\x62\x6d\x70\x22\x0a\x64\x65\x73\x63\x72\x69\x70\x74\x69\x6f\x6e\x20\x20\x3d\x20\x22\x22\x0a\x64\x61\x74\x65\x20\x20\x20\x20\x20\x20\x20\x20\x20\x3d\x20\x22\x32\x30\x32\x33\x2d\x30\x38\x2d\x31\x35\x54\x30\x30\x3a\x33\x31\x3a\x30\x39\x2e\x39\x34\x36\x5a\x22\x0a\x74\x69\x6d\x65\x7a\x6f\x6e\x65\x20\x20\x20\x20\x20\x3d\x20\x22\x2d\x30\x34\x3a\x30\x30\x22\x0a\x3b\x0a\x5b\x63\x6f\x6e\x66\x69\x67\x5d\x0a\x70\x6f\x72\x74\x5f\x32\x32\x20\x20\x20\x20\x20\x20\x3d\x20\x22\x61\x64\x69\x22\x0a\x00\x00\xf4\xff"
# )
# vex_brain.send(b"\xc9\x36\xb8\x47\x56\x12\x01\x03\x56\x51")
# vex_brain.send(b"\xc9\x36\xb8\x47\x21")
# vex_brain.send(
#     b"\xc9\x36\xb8\x47\x56\x11\x34\x01\x01\x01\x01\x24\x00\x00\x00\x00\x00\x00\x07\x92\xb6\x96\x0f\x62\x69\x6e\x61\xcf\x83\x6d\x2c\x01\x00\x00\x00\x73\x6c\x6f\x74\x5f\x31\x2e\x62\x69\x6e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xbd\xce"
# )
# vex_brain.send(
#     b"\xc9\x36\xb8\x47\x56\x13\x28\x00\x00\x00\x07\x43\x4f\x44\x45\x43\x4f\x44\x45\x43\x4f\x44\x45\x43\x4f\x44\x45\x43\x4f\x44\x45\x43\x4f\x44\x45\x43\x4f\x44"
# )
# vex_brain.send(b"\x45\x43\x4f\x44\x45\x43\x4f\x44\x45\xa2\xa0")
# vex_brain.send(
#     b"\xc9\x36\xb8\x47\x56\x15\x1a\x40\x00\x70\x79\x74\x68\x6f\x6e\x5f\x76\x6d\x2e\x62\x69\x6e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x64\x17"
# )
# vex_brain.send(b"\xc9\x36\xb8\x47\x56\x12\x01\x03\x56\x51")


# vex_brain.send(open("Captures/LAST_12", "rb").read())


# start = open("start", "rb").read()
# end = open("all", "rb").read()
# vex_brain.send(start)
# time.sleep(1)
# vex_brain.send(end)


for slot in range(1, 9):
    status = vex_brain.start_program(slot)

    if status == STATUS_SUCCESS:
        print(f"[Brain -> PC](translated): Status: Success")
    elif status == STATUS_PROGRAM_NOT_FOUND:
        print(f"[Brain -> PC](translated): Status: Program does not exist")
    elif status == STATUS_PACKET_VALIDATION_ERROR:
        print(f"[Brain -> PC](translated): Status: Packet validation error")
    elif status == STATUS_UNKNOWN_ERROR:
        print(f"Unrecognized status packet")

vex_brain.close_connection()
