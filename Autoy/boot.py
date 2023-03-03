import read
import machine
import time
import random
import _thread
from machine import SoftI2C
from utime import sleep_ms
from machine import Pin
from micropython import const
import utils
import bt
import os

#Initial state da state machine
# Global variables and constants
CHECK           = const(0x00)
WAITSEND        = const(0x01)
INITIALIZATE    = const(0x02)
WAIT            = const(0x03)
ERROR           = const(0x04)
SENDBT          = const(0x05)
ACTIVITY        = const(0x06)
ACTIVITYNOSAVE  = const(0x07)
REGISTERACTIVITY= const(0x08)
CONFIRMSEQ      = const(0x09)
CONFIRMPAR      = const(0x10)
STATE =CHECK
FILENAME      = "atividades.txt"
#R14 G12 B15
#To stop the code, press Ctrl + C on picocom TWO TIMES(one to each thread)
red = machine.Pin(13)
pwmRed = machine.PWM(red)
green = machine.Pin(14)
pwmGreen= machine.PWM(green)
blue = machine.Pin(12)
pwmBlue = machine.PWM(blue)

MIN_ANALOG = 1023
MAX_ANALOG = 0
MIN_COLOR  = 0
MAX_COLOR  = 255

BT_NAME   = 'AUTECLA01'
flagEnvioBT     = 0
flagCadastroSeq = 0
flagCadastroPar = 0
flagSalvaCadastroAtvdd = 0

#roxo, vermelho, amarelo,  verde, branco
purple = 148, 0, 211
red = 250, 0, 0
yellow = 255, 255, 0
green = 0, 255, 0
white = 255, 255, 255
blue = 0, 0, 255
#Defines the lock of the threads
lockTest =_thread.allocate_lock()

#Defines the configurations tags
tagActivityRegister = "0x947ec4be"
tagActivityTest = "0x73b892f4"

#declarando i2c e bluetooth
global bluetooth
i2c       = None
bluetooth = None

MINI_ADDR = 0x01
gabaritoCrianca = " "


# I2C settings
i2c = SoftI2C(scl=machine.Pin(22), sda=machine.Pin(21))

#Defines a thread to always read the RFID and update the tags values
def readRFIDS():
    try:
        while True:
            lockTest.acquire()
            global tagRight 
            tagRight = read.do_read(5)
            global tagLeft 
            tagLeft= read.do_read(4)
            #print("Minha tag eh " +str(tagRight))
            lockTest.release() 
    except KeyboardInterrupt:
        print("Bye") 
        lockTest.release()

#Change the led color
def ledColor(r,g,b):
    pwmRed.duty(r)
    pwmGreen.duty(g)
    pwmBlue.duty(b)

#Checa se o arquivo existe, se nao, cria o arquivo
#Retorna um ponteiro pro arquivo
def checkFile():
    try:
        file = open(FILENAME)
        file.close()
    except: 
        file = open (FILENAME, 'x')
        file.close()
#Recebe o ponteiro pro arquivo e checa o tamanho dele, retorna 0 se esta cheio e 1 se esta OK    
def checkFileSize():
    try: 
        file = open(FILENAME, 'r') 
        FileSize = len(file.readlines())

        if FileSize > 0:
            return 0
        else:
            return 1
    except: 
        print("Erro: checkFileSize() ")

#Checa se todos os RFIDs estao ok, e retorna 0 caso haja algum ruim e 1 caso esteja tudo ok
def checkRFIDS():
    #retornei 1 apenas pra testar no hardware
    return 1
    #toImplement
def writeActivity(childFeedback):
    file = open(FILENAME, "r") # Abrindo somente para copiar o conteúdo
    text = file.readlines()
    file.close()

    open(FILENAME, 'w').close() # Apagando o conteúdo do arquivo

    file = open(FILENAME, "w") # Abrindo para gravar o novo conteúdo
    text.append(str(childFeedback) + "\n")
    for i in text:
        print(i)
        file.write(i)
    file.close()

def bytearray_to_string(data):
    s = ""
    for x in data:
        if x != 0xFF:
            s += chr(x)
    return s

# store_tags receives a string of tags like "a%b%c%d"
# and stores the lags in a list of lists
def store_tags(tags, index):
    global TEMP_TAGS
    if (len(TEMP_TAGS) == 0):
        # initialize a empty list
        TEMP_TAGS = ['','','']
    TEMP_TAGS[index] = tags.split('%')

def atividade(resposta, teste, stringError):
    #NAO PRECISA RECEBER A RESPOSTA!
    #recebe a resposta da atividade e uma flag onde 0 = atividade que apenas retorna as repostas
    #1 = acende led para indicar q a atividade esta certa ou nao
    #faz um laco que fica recebendo recebendo no i2c ate a tag right == 0x00...

    #RESPOSTA FICTICIA PARA TESTAR
    #resposta        = "73b892f4%ddb070d5%947ec4be%"

    
    respostaCrianca = ['','','','','','','','','','','','']
    auxCrianca=0
    #print(resposta," minha reposta")
    global i2c
    msg=""
    MINI_ADDR = 1
    numMensagem=1
    while MINI_ADDR <=3:
        if (auxCrianca ==12):
            auxCrianca=0
        try:
            msg = i2c.readfrom(MINI_ADDR, 19) #TODO: probably can ask for less bytes than 32
            #msg2 = i2c.readfrom(MINI_ADDR, 32)
            #TODO: probably those tag storing dont need to be inside a try
            #   msg = bytearray_to_string(msg)
            #store_tags(msg[:-1], (MINI_ADDR - 1))
            print("mnsg ",numMensagem," mini", MINI_ADDR)
            msg = bytearray_to_string(msg)
            #print(msg[:-1])
            msg= msg.split("%")
            print("minha mensagem ",msg[:-1])
            myLen = len(msg[:-1])
            if(myLen==2):
                respostaCrianca[auxCrianca]   =msg[0]
                respostaCrianca[auxCrianca+1] =msg[1]
            elif(myLen==1):
                respostaCrianca[auxCrianca]   =msg[0]
                respostaCrianca[auxCrianca+1] = "00000000"
            else:
                respostaCrianca[auxCrianca]   = "00000000"
                respostaCrianca[auxCrianca+1] = "00000000"
            auxCrianca+=2
        except:
            print('error while reading Pro Mini', MINI_ADDR)
            respostaCrianca[auxCrianca]   = stringError
            respostaCrianca[auxCrianca+1] = stringError
            auxCrianca+=2

            # Debug message
        if numMensagem==1:
            numMensagem=2
        else:
            numMensagem=1   
            MINI_ADDR +=1
            
    print("MENSAGEM FINAL ", respostaCrianca) 
    return respostaCrianca  
    if teste== 0:
        #acende led quando atividade estiver completamente correta
        pass
    else:
        return  respostaCrianca
        #cria a tupla q sera retornada.
        pass 
    

    #retorna uma tupla que contem tudo oq eh relevante salvar da atividade 
    #(resposta colocada, quantos acertos, tempo de realizacao,...)
    #coloquei return para testes
    return (" ",1)
    #toImplement   
def comparaResposta(resposta,gabaritoCriancaFunc):
    print("MEU TIPO DE RESPOSTA: ", resposta[0])
    if (resposta[0]=='Sequencia'):
        listaAux = resposta[1:]
        count = 0
        for i in range(0, len(listaAux)):
            if (listaAux[i]==gabaritoCriancaFunc[i]):
                count+=1
        print("acertos: ",count)
        return str(count),"Sequencia"
    elif (resposta[0]=='Pareament'):
        listaAux = resposta[1:]
        count = 0
        for i in range(0, len(listaAux),2):
            for j in range(0, len(gabaritoCriancaFunc),2):
                if (listaAux[i]==gabaritoCriancaFunc[j] and listaAux[i+1]==gabaritoCriancaFunc[j+1]):
                    count+=1
                    break
        print("acertos: ",count)
        return str(count),"Pareament"
    return "error"
    
def iniciarAtividade(resposta, idCrianca, save):
    if(save==0):
        start = time.time()
        gabarito = atividade(resposta,1, "x")
        end = time.time()
        print(end - start)
        return gabarito
    elif(save==1):
        #chama a funcao gravarAtividade passando a string da resposta recebida
        
        #print("minha respota: ",resposta)
        gabaritoCriancaFunc = atividade(resposta,0, "x")
        
        #print(end - start)

        numAcertos, tipoAtvdd = comparaResposta(resposta, gabaritoCriancaFunc)
        blocoRespostas = idCrianca + ";" +tipoAtvdd+ ";"+ numAcertos +";" + str(gabaritoCriancaFunc) +";"
        #Devemos saber o numero de acertos aqui
        return blocoRespostas
        
    
    #toImplement

#envia reposta para o banco de dados
def enviaBT():
    f = open(FILENAME, 'r')
    matriz_lista = []
    for line in f:
        linhas = line.split()
        print("linhas: ", linhas)
        matriz_lista.append(linhas)
        print("teste"+str(linhas))
        tamLinha = len(str(linhas))
        for i in range(0,tamLinha,20):
            if ((i+20)<=tamLinha):
                #print(str(linhas)[i:(i+20)])
                bluetooth.write(str(linhas)[i:(i+20)] + "\n")
                time.sleep_ms(500)
            else:

                #print("teste2" +str(linhas)[i:])
                linhaFinal =str(linhas)[i:]
                numAuxFinal=20-len(linhaFinal)
                for j in range(0,numAuxFinal):
                    linhaFinal = linhaFinal +"%"
                bluetooth.write(linhaFinal + "\n")
                time.sleep_ms(500)
    pass

def formataCadastro(cadastrar):
    cadastrar = str(cadastrar)[1:-1]
    cadastrar = cadastrar.split(',')
    print(cadastrar)
    a=""
    for i in cadastrar:
        i= i.replace(" ","")
        if (i == "''"):
            a = a+"00000000%"
        else:
            a = a + i[1:-1]+"%"
    a = a[:-1]
    return a

def cadastraAtvdd():
    cadastro = atividade("",1, "")
    return cadastro

try:
    bluetooth = bt.BLEUART(name=BT_NAME)
    def on_rx():
        global flagEnvioBT
        global flagCadastroSeq
        global flagCadastroPar
        global flagSalvaCadastroAtvdd
        try:
            dados = bluetooth.read().decode().strip()
            print("rx: ", dados)
            if(dados== '0'):
                flagEnvioBT=1
            #OP_ID = COLOR_ID #TODO: dont know if color OP its really 0
            elif(dados == '1'):
                #OP_ID = SEQ_ID
                flagCadastroSeq=1
            elif(dados == '2'):
                #OP_ID = SEQ_ID
                flagCadastroPar=1
            elif(dados == '3'):
                flagSalvaCadastroAtvdd=1
            else:
                print("eh int")
        except KeyboardInterrupt:
            print("Bye")
            #exit(0)
            lockTest.release()
    
    bluetooth.irq(handler=on_rx)


    #print("AAAAAAAAAAAAAAAAAA")
    # Setting above functions as IRQ Handlers
    #bluetooth.irq(
    #    rx_callback=rx_handler,
    #    conn_callback=conn_handler,
    #    rxend_callback=rx_end_handler
    #)
    #General state machine based on ESP RFID's 
    while(True):
        #print("na maquina de estados")
        if STATE == CHECK:
            checkFile()
            status = checkFileSize()
            if status == 0:
                STATE = WAITSEND
            elif status == 1:
                STATE = INITIALIZATE
        elif STATE == WAITSEND:
            print("purple")
            r,g,b = purple
            ledColor(r,g,b)
            #LED ROXO ALGUNS SEGUNDOS,E  PASSA PRO INITIALIZATE
            STATE=INITIALIZATE
        elif STATE == INITIALIZATE:
            #TENTA INICIALIZAR THREAD E TESTAR RFIDS
            #TESTAR SE A THREAD INICIALIZOU MSM(NAO SEI FAZER)
            _thread.start_new_thread(readRFIDS, ())
            status = checkRFIDS()
            if status == 1:
                STATE = WAIT
            elif status==0:
                STATE = ERROR

        elif STATE == ERROR:
            #LED VERMELHO TRAVADO
            print("red")
            r,g,b = red
            ledColor(r,g,b)
            pass
        elif STATE == WAIT:
            #LED VERDE E APENAS ESPERA.
            print("green")
            r,g,b = green
            ledColor(r,g,b)
            time.sleep_ms(20)
            lockTest.acquire()
            if flagEnvioBT == 1:
                STATE = SENDBT
                lockTest.release()
            elif flagCadastroSeq == 1:
                STATE = REGISTERACTIVITY
                lockTest.release()
            elif flagCadastroPar == 1:
                STATE = REGISTERACTIVITY
                lockTest.release()
                
            #TO TEST
            #elif (str(tagLeft)!= "0x00000000"):
            #    utils.write_ans("a13298e5%ac2370d5%ddb070d5%cc6d785%717b1a2b%954ffc45%7bfd28db%4d211b2b%acfc73d5%c33a192b%794b1a2b%d157192b",4)    
            #    #utils.write_ans_type("Sequencia",4)
            #    utils.write_ans_type("Pareament",4)
            #    time.sleep_ms(2000)
            #    lockTest.release()
                
            #elif (str(tagRight)!= "0x00000000"): 
            #    print(utils.read_ans(5))
            #    lockTest.release() 

            elif (str(tagRight) != "0x00000000" and str(tagLeft)== tagActivityTest):
                #inicia atividade mas diz para nao salvar
                STATE = ACTIVITYNOSAVE
                gabaritoTag = str(utils.read_ans(5))
                #gabaritoTag = str(utils.read_ans(5))
                gabaritoTag = gabaritoTag.split("%")
                gabaritoTag = gabaritoTag[:-1]
                #retirar espacos em branco
                try:
                    while(1):
                        gabaritoTag.remove('')
                except:
                    print("sem 0")
                start = time.time()
                lockTest.release()   
            elif (str(tagRight) != "0x00000000" and str(tagLeft)!= "0x00000000"):
                #inicia a atividade e manda salvar
                start = time.time()
                STATE = ACTIVITY
                gabaritoTag = str(utils.read_ans(5))
                gabaritoTag = gabaritoTag.split("%")
                gabaritoTag = gabaritoTag[:-1]
                #retirar espacos em branco
                try:
                    while(1):
                        gabaritoTag.remove('')
                except:
                    print("mostrar ", gabaritoTag)
                
                start = time.time()
                lockTest.release() 
            else:
                lockTest.release() 
            
        elif STATE == SENDBT:
            print("yellow")
            r,g,b = yellow
            ledColor(r,g,b)
            flagEnvioBT = 0
            enviaBT()
           # os.remove(FILENAME)
            checkFile()
            STATE = WAIT
            pass
        elif STATE == REGISTERACTIVITY:
            print("yellow")
            r,g,b = yellow
            ledColor(r,g,b)
            
            cadastrar = cadastraAtvdd()
            if (str(tagRight) != "0x00000000" and flagSalvaCadastroAtvdd==1):
                if (flagCadastroSeq==1):
                    flagCadastroSeq = 0
                    STATE = CONFIRMSEQ
                elif(flagCadastroPar==1):
                    flagCadastroPar = 0
                    STATE = CONFIRMPAR
            #STATE = WAIT
            pass
        elif STATE == CONFIRMSEQ:
            #CADASTRANDO seq
            print("yellow")
            r,g,b = yellow
            ledColor(r,g,b)
            flagSalvaCadastroAtvdd = 0
            lockTest.acquire()
            cadastrar = formataCadastro(cadastrar)
            print("cadastrando ", str(cadastrar))
            utils.write_ans(str(cadastrar),5)  
            print("cadastro tipo: seq ")    
            utils.write_ans_type("Sequencia",5)
            
            r,g,b = purple
            ledColor(r,g,b)
            time.sleep_ms(1000)

            lockTest.release()
            STATE = WAIT
            pass
        elif STATE == CONFIRMPAR:
            #CADASTRANDO par
            print("yellow")
            r,g,b = yellow
            ledColor(r,g,b)
            flagSalvaCadastroAtvdd = 0
            lockTest.acquire()
            cadastrar = formataCadastro(cadastrar)
            print("cadastrando ", str(cadastrar))
            utils.write_ans(str(cadastrar),5)  
            print("cadastro tipo: par ")  
            utils.write_ans_type("Pareament",5)
            
            r,g,b = purple
            ledColor(r,g,b)
            time.sleep_ms(1000)

            lockTest.release()
            STATE = WAIT
            pass    
        elif STATE == ACTIVITY:
            print("blue")
            r,g,b = green
            ledColor(r,g,b)
            #DELAY APENAS PARA TESTE
            #time.sleep_ms(250)
            lockTest.acquire()
            if (str(tagRight) != "0x00000000" and str(tagLeft)!= "0x00000000"):
                STATE = ACTIVITY
                idCrianca = str(tagLeft)
                lockTest.release()
                gabaritoCrianca = iniciarAtividade(gabaritoTag,idCrianca,1)
            else:
                lockTest.release()
                end = time.time()
                gabaritoCrianca = gabaritoCrianca+str(end-start) +"Sec"
                print("Gravando no arquivo: ",gabaritoCrianca)
                writeActivity(gabaritoCrianca)
                STATE = WAIT
   
        elif STATE == ACTIVITYNOSAVE:
            print("white")
            r,g,b = white
            ledColor(r,g,b)
            #DELAY APENAS PARA TESTE
            #time.sleep_ms(250)
            lockTest.acquire()
            if (str(tagRight) != "0x00000000" and str(tagLeft)!= "0x00000000"):
                STATE = ACTIVITYNOSAVE
                idCrianca = str(tagLeft)
                lockTest.release()
                iniciarAtividade(gabaritoTag,idCrianca,0)
            else:
                lockTest.release() 
                STATE = WAIT 
    
    
except KeyboardInterrupt:
    print("Bye")
    #exit(0)
    lockTest.release()
    