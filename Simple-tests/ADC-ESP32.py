
# ###############################################################################
#            TESTE DE LEITURA DE RESISTENCIAS PELO ADC DA ESP32    V1.0.0       #
#                                                                               # 
#                   Para excucao do codigo no picocom, utilize:                 #
#                                                                               #
#                       exec(open("main.py").read())                            #
#                                                                               #
# ###############################################################################


import time
from machine import Pin
from machine import ADC

pinS = [Pin(26,Pin.OUT), Pin(25,Pin.OUT), Pin(33,Pin.OUT), Pin(32,Pin.OUT)]

MIN100 = 4000
MAX100 = 4096
MIN470 = 2900
MAX470 = 3900
MIN1000 = 2500
MAX1000 = 2899
MIN2000 = 1300
MAX2000 = 1999
MIN3300 = 800
MAX3300 = 1299

def calculate_resistor(adc_read):
    if adc_read == 0:
        return 0
    else:
        return 1000 * ((4095 - adc_read)/ adc_read)
def calculate_voltage(adc_read):
    return adc_read * 3.3 / 4095

#### MAPEAMENTO DE LEITURA DE ADC ####
id_resistores = {
    "100": "Laranja",
    "470": "Azul",
    "1000": "Rosa",
    "2000": "Verde",
    "3300": "Roxo"
}

def mapeamento(signal):
    if MIN100 <signal < MAX100:
        return 100
    if MIN470 <signal < MAX470:
        return 470
    if MIN1000 <signal < MAX1000:
        return 1000
    if MIN2000 <signal < MAX2000:
        return 2000
    if MIN3300 <signal < MAX3300:
        return 3300

#

def main():
#
# VERSAO DO CODIGO
#

    print('\033[33m'+'\n=============== VERSAO 1.0.0 ===============\n'+'\033[0;0m')

#
# Inicialização dos pinos e ajuste de atenuacao para que seja lido até 3v3
#
    for i in range(3):
        pinS[i].value(1)

    pinSignal = Pin(35, Pin.IN)
    adc = ADC(pinSignal)
    adc.atten(ADC.ATTN_11DB)

#
# Inicialização dos pinos 
#
    
    print('\033[33m'+'\n============== LEITURAS =============='+'\033[0;0m')
    print('---\t---\t---\t---\t---\t---\t---\t---')
    #
    # Configurando pinos do MUX
    #
    pinS[0].value(0)
    pinS[1].value(0)
    pinS[2].value(1)
    pinS[3].value(1)

    while(1):  
        data_signal = ''
        mapp = ''
        for pin in range(12):
            for i in range(4):
                pinS[i].value(1 if pin & (1 << i) else 0)
            time.sleep(0.2)
            Signal = adc.read()
            mapeando = mapeamento(Signal)
            Resistance = calculate_resistor(Signal)
            map_resistance = id_resistores.get(str(mapeando), 'x')
            data_signal = data_signal  + "{:.0f}".format(pin+1) + ":" + " adc=" + "{:.0f}".format(Signal)  + " Rx: " + "{:.0f}".format(Resistance)  + " |"
            mapp = mapp + "{:.0f}".format(pin+1) + ":" + "{}".format(map_resistance)  + " |"
        # print(data_signal)
        # print("\n")
        print(mapp)
        print("\n")

main()

#+ "->" + "{:.2f}".format(Voltage) + " Rx="+ "{:.0f}".format(Resistance)