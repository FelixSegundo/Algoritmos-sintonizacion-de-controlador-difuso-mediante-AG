import RPi.GPIO as GPIO #libreria GPIO
import time
from time import sleep

GPIO.setwarnings(False) # Evita errores
GPIO.setmode(GPIO.BCM)# Numeracion de los puertos en formato BCM (seguir diagrama)

##########################configura pines del sistema mecanico#########################
#define pines
EnaZ = 16 # pin HABILITA DRIVER EN
DirZ = 20 # PIN DE DIRECCION CW
PulZ = 21 # PIN DE PULSOS/PASOS CLK
#configura resolucion de pasos
#1    -> 40, #1/2  -> 20, #1/8  -> 5, #1/16 -> 2.5
Resolucion = 2.5;
#configura pines como salida
GPIO.setup(EnaZ, GPIO.OUT)
GPIO.setup(DirZ, GPIO.OUT)
GPIO.setup(PulZ, GPIO.OUT)
GPIO.output(EnaZ, GPIO.HIGH)#Deshabilita motorEjeZ
pausa = 0.0009
#######################Fin configura pines del sistema mecanico########################      
        
def EjeZ(distancia):
    GPIO.output(EnaZ, GPIO.LOW)#habilita motorEjeZ
    if distancia > 0:
        GPIO.output(DirZ, GPIO.LOW)#Establece direccion DRECHA
        print("Sube")
    if distancia < 0:
        GPIO.output(DirZ, GPIO.HIGH)#Establece direccion IZQUIERDA
        distancia=distancia*-1
        print("Baja")
    pulsos = int(distancia//Resolucion) ###CALCULA CANTIDAD DE PULSOS PARA MOVERSE A LA DISTANCIA DESEADA
    print(pulsos)
    
    for i in range(pulsos):
        GPIO.output(PulZ, GPIO.HIGH)
        sleep(pausa)
        GPIO.output(PulZ, GPIO.LOW)
        sleep(pausa)
    GPIO.output(EnaZ, GPIO.HIGH)#Deshabilita motorEjeZ

#-------------------------------------------------------------------------------------#
#########################-----Inicia el cuerpo del sistema-----#########################
distancia = 1
while distancia != 0:
    #distancia = int(input("Ingresa distancia (um): "))
    distancia = float(input("Ingresa distancia (um): "))
    EjeZ(distancia)
print("Estableciendo IEG 240 um")    
EjeZ(240)#establece IEG 240 um

GPIO.cleanup()
print('Prueba terminada')

