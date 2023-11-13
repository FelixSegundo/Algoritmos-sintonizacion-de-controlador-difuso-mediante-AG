import RPi.GPIO as GPIO #libreria GPIO
import time
from time import sleep
#configura pines
GPIO.setwarnings(False) # Evita errores
GPIO.setmode(GPIO.BCM)# Numeracion de los puertos en formato BCM (por numero GPIO)
####################(Multiplexor)####################
S0= 5           #Bit A de slelccion en el mux
S1 = 6          #Bit B de seleccion en el mux
#configura pines A y B como salida
GPIO.setup(S0, GPIO.OUT)
GPIO.setup(S1, GPIO.OUT)
#selecciona el canal 0 del mux, señal nula
GPIO.output(S1, True)
GPIO.output(S0, True)
def CanalABin(Canal):
    if Canal == 0:      #Canal = 0, entonces BA=00
        GPIO.output(S1, False)
        GPIO.output(S0, False)
        print("Canal 0 seleccionado:SINOSOIDAL")
    if Canal == 1:      #Canal = 1, entonces BA=01
        GPIO.output(S1, False)
        GPIO.output(S0, True)
        print("Canal 1 seleccionado:CUADRADA")
    if Canal == 2:      #Canal = 2, entonces BA=10
        GPIO.output(S1, True)#activa mux
        GPIO.output(S0, False)#activa mux
        print("Canal 2 seleccionado: TRIANGULAR")
    if Canal == 3:      #Canal = 3, entonces BA=11
        GPIO.output(S1, True)#activa mux
        GPIO.output(S0, True)#activa mux
        print("Canal 3 seleccionado: GND")
C = 0
while C < 5:
    C = int(input("Ingresa canal: "))
    CanalABin(C)
GPIO.cleanup()
print('Prueba terminada')