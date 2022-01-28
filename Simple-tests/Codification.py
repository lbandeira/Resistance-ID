import struct
def binary(num):
    return ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))

ID = hex(int(num, 2)) #Getting the voltage in hex number as an ID
TAG_ID = ID[2:] # Remove 0x to get the TAG ID

