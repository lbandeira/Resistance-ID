from machine import Pin

AUTOY_ON = Pin(34,Pin.IN) 

def main():
    print('\033[90m'+ '=============== SYSTEM TURN ON ===============' +'\033[0;0m')
    if (AUTOY_ON.value()):
        print('\033[92m'+ 'AUTOY IS TURNED ON'+ '\033[0;0m')
        exec(open("autoy-sys.py").read())
        
    else:
        print('\033[91m'+ 'AUTOY IS TURNED OFF' +'\033[0;0m')
        sys.exit()