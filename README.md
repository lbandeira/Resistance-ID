# Resistance-ID
O projeto consiste na leitura de diferentes tensões pela porta ADC da ESP32

## Circuito
O circuito é um conjunto de divisores de tensão, no qual as variações de leituras de cada cartão será gerada pelas diferentes resistências que estão em cada cartão. Para realizar as múltiplas leituras utiliza-se um Módulo Multiplexador analógico Cd74hc4067, como observado na Figura 5.3. abaixo.

![figura15](https://user-images.githubusercontent.com/8952291/213711217-fe114e9e-1315-498e-82c9-c3c7708acc5c.png)

A identificação de diferentes figuras utiliza o princípio de divisor de tensão, o qual pode ser observado na Figura 5.4 e na equação abaixo. Assim, o módulo de controle será responsável por calcular a diferença de potencial entre o Resistor base ($R_b$), o qual possui um valor fixo, e o terra (GND), que será modificada de acordo com o valor do Resistor incógnita ($R_x$) colocado no módulo de leitura.

$$
  V_x = R_b * (\frac {V_{cc}}{R_b + R_x})
$$

![figura16](https://user-images.githubusercontent.com/8952291/213711119-c8ae16eb-e320-4de4-ac24-229fc28b336e.png)

O circuito foi idealizado para que, enquanto uma figura não for colocada, a leitura em $V_x$ será nula. Dessa forma a rede consome menos bateria enquanto está em "standby". O valor de $V_x$, irá para o módulo multiplexador (MUX) e seguirá para o ADC da ESP32, como mostra a Figura 5.3. Para esse sistema, utilizamos o ADC de 12 bits (Resolução = 4096) do ESP32. Sendo assim a leitura da tensão seguirá a seguinte fórmula, onde, $L_{ADC}$ é a leitura digital realizada pelo ADC:

$$   V_x = L_{ADC} * \frac {V_{cc}}{4095}$$

![figura25](https://user-images.githubusercontent.com/8952291/213712437-55442e8e-30f3-429b-bd42-e58d549e3b57.jpg)

# Usando MicroPython na ESP32

## Sections
- [Requerimentos](#requerimentos)
- [Instalando o firmware](#instalando-o-firmware)
- [Testando a instalação](#testando-a-instalação)
- [Enviando arquivos para ESP32](#enviando-arquivos-para-esp32)
- [Blink, O Hello World dos Embarcados](#blink,-o-hello-world-dos-embarcados)
- [Seu melhor amigo](#seu-melhor-amigo)

---

## Requerimentos

- Linux ou WSL no Windows 10
- Programa para acessar porta Serial da ESP32 (Ex:. picocom)
- Esptool - Programa para flashar o firmware do micropython
- Adrafruit Ampy - Programa para transferir arquivos para a ESP

Se você estiver usando uma distro baseada em Ubuntu rode:

    $ sudo apt install picocom python3-pip
    $ pip3 install --user esptool
    $ pip3 install --user adafruit-ampy

Esses comando iram instalar o Esptool e Ampy caso você ainda não tenha

---

## Instalando o firmware

O firmware do micropython só precisa ser instalado uma vez. Caso vocẽ já tenha instalado ele na ESP32 e quer atualizar a versão prossiga com os passos abaixos. caso contrário, pule essa parte.

Primeiro baixe o firmware do micropython para ESP32 [nesse link](https://micropython.org/download/esp32/)

Conecte a ESP32 no seu PC e a procure na pasta  `/dev/` assim:

    # ls -l /dev/tty*

Geralmente ele aparece com o nome `ttyUSB0`. Logo vamos assumir esse nome para os proximos comando, mas é possivel aparecer algo como `ttyUSB1` e outros, então faça as trocas necessarias nos proximos comandos.

Abra o terminal e vá para a pasta que contem o firmware recem baixado. Primeiro vamos apagar a flash e depois instalar o firmware:

    $ esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

Se por alguma razão o script estiver demorando em `"trying to connect..."` você vai provavelmente precisar segurar o botão BOOT da ESP32 enquanto tiver tentando conectar e provavelmente vai funcionar. Se ainda assim não funcionar tente pesquisar por "ESP32 Boot Mode" para entender melhor o que pode estar acontecendo.

Agora vamo instalar o firmware:

    $ esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 firmware_file_name_here.bin

---

## Testando a instalação

Vamos tentar conectar na ESP32 usando o Picocom. Rode:

    $ picocom -b 115200 /dev/ttyUSBO

Primeiro, algumas instruções sobre picocom: CTRL A + CTRL X fecha a conexão serial com a ESP.

Aperte o botão de RESET na ESP32 e você provavelmente verá no seu terminal algumas mensagens de boot e logo após um: `>>>` Que é o interpretador de Python rodando, se quiser você pode ir em frente e brincar um pouco com ele.

---

## Enviando arquivos para ESP32

MicroPython ao dar boot roda automaticamente  2 arquivos chamados `boot.py` e `main.py`. Geralmente nós programos o `main.py` e depois enviamos ele para ESP para testar. Você faz isso dessa forma:

    $ ampy -p /dev/ttyUSB0 -b 115200 put main.py

Você pode fazer outras coisas interessante com Ampy. Se estiver curioso olhe [nesse link](https://github.com/scientifichackers/ampy)

Abra uma conexão serial de novo, aperte o botão reset e logo após as mensagens de boot seu programa estará rodando, e se tiver algum `print()` nele, irá aparecer também.

---

## Blink, O Hello World dos Embarcados

Vamos fazer um simples blink para verificar se está tudo certo. Crie um `main.py` e cole isso:

```python
from machine import Pin
from utime import sleep_ms

LED = Pin(15, Pin.OUT)

while True:
    LED.value(1) # High
    sleep_ms(500)
    LED.value(0) # Low
```

Verifique [ESP32 GPIO Pin Out](https://circuits4you.com/wp-content/uploads/2018/12/ESP32-Pinout.jpg) para escolher qual porta está o led que você está usando. Nesse exemplo usando a porta 15.

Save e rode:

    $ ampy -p /dev/ttyUSB0 -b 115200 put main.py

Reset a placa e seu blink deverá rodar

## Seu melhor amigo

A medida que você vai ficando mais confortavel com o fluxo de trabalho do MicroPython, A pagina de Documentação será seu melhor amigo para lhe ajudar em seus projetos. Dê uma olhada [nesse link](http://docs.micropython.org/en/latest/).
