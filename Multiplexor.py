import RPi.GPIO as GPIO #libreria GPIO
import time
from time import sleep
#configura pines
GPIO.setwarnings(False) # Evita errores
GPIO.setmode(GPIO.BCM)# Numeracion de los puertos en formato BCM (por numero GPIO)
#define pines
S0= 5# BIT S0
S1 = 6
#configura pines como salida
GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)

def CanalABin(Canal):
    if Canal == 0:
        GPIO.output(S1, False)#activa mux
        GPIO.output(S0, False)#activa mux
        print("Canal0 seleccionado: GND")
    if Canal == 1:
        GPIO.output(S1, False)#activa mux
        GPIO.output(S0, True)#activa mux
        print("Canal1 seleccionado: SIN")
    if Canal == 2:
        GPIO.output(S1, True)#activa mux
        GPIO.output(S0, False)#activa mux
        print("Canal2 seleccionado")
    if Canal == 3:
        GPIO.output(S1, True)#activa mux
        GPIO.output(S0, True)#activa mux
        print("Canal3 seleccionado: GND")
    
Ecanal = True
while Ecanal == True:
    print("_____________________________________________")
    Canal = int(input("Seleecione un canal del 1 al 3: "))
    if Canal>=0 and Canal<=3:
        CanalABin(Canal)
    else:
        print("¡¡Canal invalido!!")
        Ecanal = False
print('Prueba terminada')
