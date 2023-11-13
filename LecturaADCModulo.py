import RPi.GPIO as GPIO             #libreria control GPIO
import time
from time import sleep
import Adafruit_ADS1x15
import time                         #libreria tiempo
from time import sleep              #libreria retardos
import datetime                     #formato de fecha
import matplotlib.pyplot as plt            #libreria para generar graficos
import numpy as np                  #libreria de funciones con arrays
import csv                          #libreria para extenciones .CSV
#configura puerto GPIO
GPIO.setwarnings(False) # Evita errores
GPIO.setmode(GPIO.BCM)# Numeracion de los puertos en formato BCM (por numero GPIO)
GPIO.cleanup() #limpia el puerto
# Crea una instancia para el ADS1115 ADC (16-bit)
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
Const = 4.096/32768
def TomaLecturaVoltajeCorriente():
    NL = 1
    # Read the specified ADC channel using the previously set gain value.
    LecturasVRDiv = [0]*NL#CREA Vector de 5 lecturas para voltaje
    LecturasCRM = [0]*NL#CREA Vector de 5 lecturas para corriente
    for i in range(NL):
        sleep(0.001)
        LecturasVRDiv[i] = adc.read_adc(0, gain=GAIN) # Lectura del adc en R10K
        sleep(0.001)
        LecturasCRM[i] = adc.read_adc(1, gain=GAIN)# lectura del adc de corriente en RM
    #Promedia las lecturas obtenidas de voltaje y corriente
    LecturaEnRDiv = int(sum(LecturasVRDiv)/len(LecturasVRDiv))
    LecturaEnRM = int(sum(LecturasCRM)/len(LecturasCRM))
    #conversiones
    VoltajeEnRDiv = round(LecturaEnRDiv*(4.096/32767),5) #Conversion de lectura a voltaje
    VoltajeEnRM = round(LecturaEnRM*(4.096/32767),5) #Conversion de lectura a voltaje
    #imprime los valores de voltaje y corriente
    print("Valor leido: ",LecturaEnRDiv, "   Voltaje en RDiv:", VoltajeEnRDiv)
    #print("Valor leido: ",LecturaEnRM, "   Corriente en RM:", VoltajeEnRM)
    adc.stop_adc()
    #conversiones
    Vr = round((VoltajeEnRDiv*6),2)    #Calcula voltaje total
    VoltajeEnRM = VoltajeEnRM * 1000      #De decimal a mA
    Ir = round((VoltajeEnRM/10.91),5)              #calcula voltaje en rm
    print("Valor leido: ",LecturaEnRDiv, "   Voltaje en RDiv:", Vr,"v")
    print("Valor leido: ",LecturaEnRM, "   Corriente en RM:", Ir,"mA")
    return Vr, Ir
########################################Main##############################################################
inicio = time.time()
t = [round(time.time() - inicio,3)]#inicia tiempo
V, C = TomaLecturaVoltajeCorriente()
Voltajes = [V]
Corrientes = [C]
Profundidad = [0]
tb = time.time() - inicio#tiempo base
while (time.time() - inicio) <= 60.0:   
    print("---------------",round((time.time() - inicio),0),"---------------")
    Va, Ca = TomaLecturaVoltajeCorriente()
    ta = time.time() - inicio #tiempo actuual
   
    t.append(round(ta,3))
    Voltajes.append(Va)
    Corrientes.append(Ca)
    
    time.sleep(0.125)

print(Corrientes)
print(t)
##########################################################
#inicia modulo de guardadr datos---------------------------------------------------
Hora = str(time.strftime("%X"))
Dt = datetime.datetime.now()

NombreF = "Lecturas"+str(Dt.day)+str(Dt.month)+" "+Hora
with open(NombreF+".csv", 'w', newline='') as MaquinadoFile:
    csvwriter = csv.writer(MaquinadoFile)
    csvwriter.writerow(t)
    csvwriter.writerow(Voltajes)
    csvwriter.writerow(Corrientes)
##########################################################
#grafica los datos
plt.errorbar(t, Corrientes, label='Corriente')
plt.legend(loc='upper right')
plt.ylabel('Corriente mA')
plt.xlabel('Tiempo (s)')
nC = NombreF+'C.png'
plt.savefig(nC,format='png',dpi=1200)
plt.show()