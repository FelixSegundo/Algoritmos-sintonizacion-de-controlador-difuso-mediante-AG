import RPi.GPIO as GPIO #libreria GPIO
import time
from time import sleep
#configura pines
GPIO.setwarnings(False) # Evita errores
GPIO.setmode(GPIO.BCM)# Numeracion de los puertos en formato BCM (GPIO)
#define pines
pCont = 5

EnaZ = 16 # pin HABILITA DRIVER EN
DirZ = 20 # PIN DE DIRECCION CW
PulZ = 21 # PIN DE PULSOS/PASOS CLK

GPIO.setup(pCont, GPIO.OUT)
GPIO.output(pCont, GPIO.HIGH)#Apaga con logica inversa

GPIO.setup(EnaZ, GPIO.OUT)
GPIO.setup(DirZ, GPIO.OUT)
GPIO.setup(PulZ, GPIO.OUT)
GPIO.output(EnaZ, GPIO.HIGH)#Deshabilita motorEjeZ
Resolucion = 2.5
pausa = 0.0010

def Rele(estado):
    if(estado==1):
        GPIO.output(pCont, GPIO.LOW)##prende
    if(estado==2):
        GPIO.output(pCont, GPIO.HIGH)#apaga
        
def EjeZ(distancia):
    GPIO.output(EnaZ, GPIO.LOW)#habilita motorEjeZ
    if distancia > 0:
        GPIO.output(DirZ, GPIO.LOW)#Establece direccion DRECHA
    if distancia < 0:
        GPIO.output(DirZ, GPIO.HIGH)#Establece direccion IZQUIERDA
        distancia=distancia*-1
        print("Izquierda")
    pulsos = int(distancia//Resolucion) ###CALCULA CANTIDAD DE PULSOS PARA MOVERSE A LA DISTANCIA DESEADA
    print(pulsos)
    
    for i in range(pulsos):
        GPIO.output(PulZ, GPIO.HIGH)
        sleep(pausa)
        GPIO.output(PulZ, GPIO.LOW)
        sleep(pausa)
    GPIO.output(EnaZ, GPIO.HIGH)#Deshabilita motorEjeZ

a = 1
while a != 0:
    a = int(input("0: Terminar,      1: Prendido,      2 = Apagado >>"))
    Rele(a)
EjeZ(240)