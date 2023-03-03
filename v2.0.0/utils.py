import mfrc522
import math
import time
from os import uname
from machine import Pin, SoftSPI

# Base functions
sck = Pin(18, Pin.OUT)
mosi = Pin(23, Pin.OUT)
miso = Pin(19, Pin.OUT)
spi = SoftSPI(baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

    
            
def do_read_block(block,rfidAtual):
	sda = Pin(rfidAtual, Pin.OUT)
	if uname()[0] == 'WiPy':
		rdr = mfrc522.MFRC522("GP14", "GP16", "GP15", "GP22", "GP17")
	elif uname()[0] == 'esp8266':
		rdr = mfrc522.MFRC522(0, 2, 4, 5, 14)
	elif uname()[0] == 'esp32':
		rdr = mfrc522.MFRC522(spi, sda)
	else:
		raise RuntimeError("Unsupported platform")

	print("")
	print("Place card before reader to read from address 0x08")
	print("")

	try:
		(stat, tag_type) = rdr.request(rdr.REQIDL)

		if stat == rdr.OK:
			(stat, raw_uid) = rdr.anticoll()
			if stat == rdr.OK:
				#print("New card detected")
				#print("  - tag type: 0x%02x" % tag_type)
				#print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
				#print("")
				
				if rdr.select_tag(raw_uid) == rdr.OK:

					key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
						
					if rdr.auth(rdr.AUTHENT1A, block, key, raw_uid) == rdr.OK:
						raw_data = rdr.read(block)
						changer = [chr(x) for x in raw_data]
						data = ""
						data = data.join(changer)
						#print(changer, data)
						rdr.stop_crypto1()
						return data
					else:
						print("Authentication error")

				else:
					print("Failed to select tag")
		time.sleep_ms(100)
		
			

	except KeyboardInterrupt:
		print("Bye")


def do_write(block, stringToRecord, rfidAtual):
	sda = Pin(rfidAtual, Pin.OUT)
	if uname()[0] == 'WiPy':
		rdr = mfrc522.MFRC522("GP14", "GP16", "GP15", "GP22", "GP17")
	elif uname()[0] == 'esp8266':
		rdr = mfrc522.MFRC522(0, 2, 4, 5, 14)
	elif uname()[0] == 'esp32':
		rdr = mfrc522.MFRC522(spi, sda)
	else:
		raise RuntimeError("Unsupported platform")

	if len(stringToRecord) < 16 :
		complete = 16 - len(stringToRecord)
		for i in range(complete):
			stringToRecord = stringToRecord + "%"

	print("")
	print("Place card before reader to write address 0x08")
	print("")

	try:

		(stat, tag_type) = rdr.request(rdr.REQIDL)

		if stat == rdr.OK:

			(stat, raw_uid) = rdr.anticoll()

			if stat == rdr.OK:
				print("New card detected")
				print("  - tag type: 0x%02x" % tag_type)
				print("  - uid	 : 0x%02x%02x%02x%02x" % (raw_uid[0], raw_uid[1], raw_uid[2], raw_uid[3]))
				print("")

				if rdr.select_tag(raw_uid) == rdr.OK:

					key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
					if rdr.auth(rdr.AUTHENT1A, block, key, raw_uid) == rdr.OK:

						stat = rdr.write(block, stringToRecord.encode())
						rdr.stop_crypto1()
						if stat == rdr.OK:
							print("Data written on block %x => %c", block, stringToRecord.encode())
						else:
							print("Failed to write data to card")
					else:
						print("Authentication error")
				else:
					print("Failed to select tag")

	except KeyboardInterrupt:
		print("Bye")
# "%7a9a9085%f3f291f4%29948d85%84f427d0%64052e78%4649b52d%457111a5%a3f38bf4%3f65340%a45dcedb%c32392f4%134d8ef4%"


# Get the answer string and format in a list with 
def Answer2List(ansString):
	countBlock = len(ansString) / 16
	countBlock = math.ceil(countBlock) 

	print (countBlock)
	ansList = []
	p = 0
	for i in range(countBlock):
		ansList.append(ansString[p:p+16])
		p += 16

	return countBlock, ansList

def write_ans_type(type_str,rfidAtual):
	do_write(4, type_str,rfidAtual)
	print ("OK!")

def write_ans(stringToRecord,rfidAtual):
    countBlock, answer = Answer2List(stringToRecord)
    blocks = [5,6,8,9,10,12,13]
    j = 0
	
    for i, j in zip(blocks, range(countBlock)):
		#print(answer[j])
        do_write(i, answer[j],rfidAtual)
        time.sleep_ms(100)

def read_ans(rfidAtual):
	data = []
	
	blocks = [4,5,6,8,9,10,12,13]
	for i, j in zip(blocks, range(0,8)):
		print(i)
		data.insert(j, do_read_block(i,rfidAtual))
		time.sleep_ms(100)

	answer = ''.join([str(x) for x in data])

	return answer
