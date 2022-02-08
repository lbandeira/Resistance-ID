# ###################################################
#            RESISTENCE ID LIB        V1.0.0        #
#                                                   # 
# Programa para identificacao de figuras atraves de #
# diferentes valores de resistencia                 #
#                                                   #
# Autora: Lais Bandeira Miranda                     #
#                                                   #
#       exec(open("main.py").read())                #
#                                                   #
# ###################################################


import struct
import time
from machine import Pin
from helper import ads

NUM_PIN = 2                             # Quantidade de pinos de leitura de tags

#
# Configuracao para seletor do MUX
#

NUM_SEL = 4
pinS = [Pin(26,Pin.OUT), Pin(25,Pin.OUT), Pin(33,Pin.OUT), Pin(32,Pin.OUT)]


#
# Funcao para criacao de identificacao da tag
#

def codification(num):
    
    binary_number = ''.join('{:0>8b}'.format(c) for c in struct.pack('!f', num))
    ID = hex(int(binary_number, 2))             # Conversao de tensao para hex
    ID = ID[2:]                       # Remove 0x para obter a TAG ID
    
    return ID

#
# LOOP PRINCIPAL
#

while True:
    
    #
    # VERSAO DO CODIGO
    #

    print('\033[33m'+'\n=============== VERSAO 1.0.0 ===============\n'+'\033[0;0m')

    data_signal = ""
    resposta = ""
    
    #
    # Inicialização dos pinos de leitura e do mux
    #
    for i in range(3):
        pinS[i].value(1)
    
    #
    # Configurando pinos do MUX
    #
    pinS[0].value(0)
    pinS[1].value(0)
    pinS[2].value(1)
    pinS[3].value(1)
    
    for pin in range(NUM_PIN):
        for i in range(NUM_SEL):
            pinS[i].value(1 if pin & (1 << i) else 0)
        
        time.sleep(0.2)
        # Realizar leitura de tensao e obtem a id
    
        signal = ads.read(0)              # Leitura de tensao na porta selecionada
        Voltage = (signal * 0.125)/1000;  # Conversao para tensao
        TAG_ID = codification(round(Voltage,1))    # Conversao para binario e inicio de codificacao
    
        # Print do sinal lido
        # o codigo principal espera #resposta = "73b892f4%ddb070d5%947ec4be%"
        resposta = resposta + TAG_ID + "%"
        data_signal = data_signal + "A"+ "{:d}".format(pin) + ":" + " TAG_ID: " + TAG_ID +  " V: " + "{:.2f}".format(Voltage) + " | "
    
    print (data_signal)
    print("\n")
    print(resposta)
    print("\n")


    
    # + " adc=" + "{:.0f}".format(signal)  + " | " + " V: " + "{:.2f}".format(Voltage) + " | "
    
        
        
            
        