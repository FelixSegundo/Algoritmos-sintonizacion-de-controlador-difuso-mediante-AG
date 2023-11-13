import numpy as np
from matplotlib import pyplot as plt
from time import time
import math
import random
import matplotlib.animation as animation
# Lista para guardar datos Tiempo y Amplitud
timepoints = []
ydata = []
filtrado = []
pIEG = []
pI = []
vok = 0
vik = 0

vok3=0
vok2=0
vok1=0
vik3=0
vik2=0
vik1=0
def FiltroDigital(f,sensor,vok,vik,vok3, vok2, vok1, vik3, vik2, vik1):
    if f == 1:
        vo=0.98497383111445*vok+0.01502616888555*vik;
        #vo=0.98874278738451*vok+0.01125721261549*vik;
        
        vok=vo;
        vik=float(sensor);
    if f==2:
        vo=1.881483426*vok1-1.309460391*vok2+0.3173878886*vok3+0.01382363442*sensor+0.04147090325*vik1+0.04147090325*vik2+0.01382363442*vik3;
        vok3=vok2
        vok2=vok1
        vok1=vo

        vik3=vik2
        vik2=vik1
        vik1=sensor
    return vo, vok, vik, vok3, vok2, vok1, vik3, vik2, vik1
################################################################################################
def CalculaPendiente(y2,y1,x2,x1,Pi,tol):
    Ajuste = False
    TipoA = 0
    pendiente = (y2-y1)/(x2-x1)
    if(Pi[1]==1):                                    #si la pendiente inicial ya se calculo
        errorP = round((Pi[0]-pendiente),3)          #calcula el error enla pendiente
        lfErrorP = round((Pi[0] - (Pi[0]*(1+tol))),3)                   #calcula mas un 10%
        liErrorP = round((Pi[0] - (Pi[0]*(1-tol))),3)                   #calcual menos un 10%
        
        print("ERROR", liErrorP, errorP, lfErrorP)
        #if ( pendiente >= (Pi[0]*(1+tol)) and pendiente <= (Pi[0]*(1-tol)) ):#si la pendiente es similar +-10%
        if(errorP >= liErrorP and errorP <= lfErrorP):
            Ajuste = False
        else:
            Ajuste = True
            #if (pendiente <= (Pi[0]*(1+tol))):
            if(errorP < liErrorP):
                TipoA = -1
                
            #if (pendiente >= (Pi[0]*(1-tol))):
            if(errorP > lfErrorP):
                TipoA = 1
        print("PendienteI ",round(Pi[0],3),"     PendienteA",round(pendiente,3),"     Ajuste",Ajuste,"   Tipo de ajuste",TipoA)
    return pendiente, Ajuste, TipoA

def CalculaErrorEnLaPendiente(y2,y1,x2,x1,Pi,tol):
    Ajuste = False
    TipoA = 0
    pendiente = (y2-y1)/(x2-x1)
    errorP = 0
    if(Pi[1]==1):                                    #si la pendiente inicial ya se calculo
        errorP = round((Pi[0]-pendiente),3)          #calcula el error enla pendiente
        lfErrorP = round((Pi[0] - (Pi[0]*(1+tol))),3)                   #calcula mas un 10%
        liErrorP = round((Pi[0] - (Pi[0]*(1-tol))),3)                   #calcual menos un 10%
        
        print("ERROR", liErrorP, errorP, lfErrorP)
        if(errorP >= liErrorP and errorP <= lfErrorP): #si la pendiente es similar +-10%
            Ajuste = False
        else:
            Ajuste = True
            if(errorP < liErrorP):
                TipoA = -1
                
            if(errorP > lfErrorP):
                TipoA = 1
        print("PendienteI ",round(Pi[0],3),"     PendienteA",round(pendiente,3),"     Ajuste",Ajuste,"   Tipo de ajuste",TipoA)
    return pendiente, Ajuste, TipoA, errorP
###############################################################################################
import os
os.chdir("/home/pi/Desktop/Control Maquinado/21-08-23")
os.getcwd()
import csv
#f= open("LF2.csv")
f= open("218 132504 Cuadrada7V60.983s2.csv")
reader = csv.reader(f)
i = 0
vok = 33.18
vik = 33.18
#variables calcula pendiente
Px1 = 0
Py1 = 0
Px2 = 0
Py2 = 0
ti = 0
PendienteI = [0,0]
tol = 0.25
TMuestra = 5
Contador = 0
PX = []
PY = []
PE = [240]
TipoA = 0
listaError=[]
for row in reader:  
    if i<9:
        i = i+1
        continue
        
    tm = float(row[0])
    sensor = float(row[2])
    vo,vok, vik,vok3, vok2, vok1, vik3, vik2, vik1 = FiltroDigital(1,sensor,vok, vik,vok3, vok2, vok1, vik3, vik2, vik1)
    ydata.append(sensor)
    filtrado.append(vo)
    timepoints.append(tm)
    
    if Contador == 3:  ##espera a que se estabilice
        print("Estabilizando")
        Px1 = tm
        Py1 = vo
        ti = tm
        PX.append(Px1)
        PY.append(Py1)
    if (tm-ti) >= TMuestra:
        #print("")
        Px2 = tm
        Py2 = vo
        #print(Py2,Py1,Px2,Px1)
        Pendiente, Ajuste, TipoA, errorP= CalculaErrorEnLaPendiente(Py2,Py1,Px2,Px1,PendienteI,tol)
        listaError.append(errorP)
        if(PendienteI[1]==0):
            PendienteI[0]=Pendiente
            PendienteI[1]=1
            #print("pendiente inicial",round(Pendiente))
        
        #print("Pendiente ",Pendiente,"Ajuste",Ajuste)
        ti = tm
        Contador = 0
        PX.append(Px2)
        PY.append(Py2)
        if TipoA == 1:
            print("sube electrodo") 
        if TipoA == -1:
            print("Baja electrodo")
            
    Contador  = Contador + 1
    
plt.figure(figsize=(15,6))
#plt.plot(timepoints, ydata, label='Original')
plt.plot(timepoints, filtrado, label='Filtrado')
plt.legend(loc='upper right')
plt.ylabel('Corriente (mA)')
plt.xlabel('Tiempo (s)')
for i in range(0,(len(PY)-(len(PY)%2)),2):
    lx=[]
    ly=[]
    plt.plot(PX[i],PY[i], "o",color="b")
    plt.plot(PX[i+1],PY[i+1], "o",color="r")
    lx.append(PX[i])
    lx.append(PX[i+1])
    ly.append(PY[i])
    ly.append(PY[i+1])
    n = "pendiente"+str(i)
    plt.plot(lx,ly,color="k")
plt.grid(True)
plt.show()
###############################
a = np.arange(0,len(listaError),1)
print(listaError)
print(len(listaError))
plt.plot(a, listaError, label='Filtrado')
plt.legend(loc='upper right')
plt.ylabel('Error en la pendiente')
plt.xlabel('Tiempo (s)')
plt.grid(True)
plt.show()
print("Filtrado terminado")