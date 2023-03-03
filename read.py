from time import sleep_ms
from machine import Pin, SoftSPI
import mfrc522

sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.OUT)
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)



def do_read(SlaveSelect):
            sda = Pin(SlaveSelect, Pin.OUT)
    
            rdr = mfrc522.MFRC522(spi, sda)
            uid = ""
            (stat, tag_type) = rdr.request(rdr.REQIDL)
            if stat == rdr.OK:
                (stat, raw_uid) = rdr.anticoll()
                if stat == rdr.OK:
                    uid = ("0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
                    print("Slave Cs=",SlaveSelect)
                    print(uid)
                    print(" ")
                    sleep_ms(100)
                    return uid
            print("Slave Cs=",SlaveSelect)
            print("0x00000000")
            print(" ")
            return "0x00000000"
    
