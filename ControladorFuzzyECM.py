import RPi.GPIO as GPIO             #libreria control GPIO
import time                         #libreria tiempo
from time import sleep              #libreria retardos
import datetime                     #formato de fecha
import Adafruit_ADS1x15             #libreria para el control del ADC
import skfuzzy as fuzz              #libreria para logica difusa
from skfuzzy import control as ctrl #libreria de control de reglas difusas
import matplotlib.pyplot as plt            #libreria para generar graficos
import numpy as np                  #libreria de funciones con arrays
import csv                          #libreria para extenciones .CSV
import math                         #libreria funciones matematicas
import random

#configura puerto GPIO
GPIO.setwarnings(False) # Evita errores
GPIO.setmode(GPIO.BCM)# Numeracion de los puertos en formato BCM (por numero GPIO)
GPIO.cleanup() #limpia el puerto
#pausa = 0.0001
pausa = 0.009
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
####################(Potenciometro)####################
# define pines potenciometro
CS = 17           #Habilita el potenciometro en low
INC = 27          #EN FLACO DE BAJADA HACE CAMBIO clk
UD = 22           #1 INCREMENTA, 0 DECREMENTA
#configura pines del potenciometro como salida
GPIO.setup(CS, GPIO.OUT)
GPIO.setup(INC, GPIO.OUT)
GPIO.setup(UD, GPIO.OUT)
def potenciometro(resistencia):
    if resistencia == 0:
        Accion = 'SIN Ajuste en voltaje'
    if resistencia > 0:
        GPIO.output(UD, GPIO.HIGH)#INCREMENTA
        Accion = 'INCREMENTA Voltaje PP'
    if resistencia < 0:
        GPIO.output(UD, GPIO.LOW)#DECREMENTA
        resistencia=resistencia*-1
        Accion = 'DECREMENTA Voltaje PP'
    print(Accion)
    GPIO.output(CS, GPIO.LOW)#habilita el pontenciometro
    pulsos = resistencia #pulso de inc o dec
    print(Accion,": ",pulsos)
    #genera el tren de pulsos
    for i in range(pulsos):
        GPIO.output(INC, GPIO.HIGH)
        sleep(pausa)
        GPIO.output(INC, GPIO.LOW)
        sleep(pausa)
    GPIO.output(CS, GPIO.HIGH)#deshabilita el potenciometro
###################################################
# Crea una instancia para el ADS1115 ADC (16-bit)
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
Const = 4.096/32768
DT = 860 #8,16,32,64,128,250,475,860,
def TomaLecturaVoltajeCorriente(wf):
    sleep(0.004)     
    #Promedia las lecturas obtenidas de voltaje y corriente
    LecturaEnRDiv = adc.read_adc(0, gain=GAIN) # Lectura del adc en R10K
    sleep(0.004)   
    LecturaEnRM = adc.read_adc(1, gain=GAIN)# lectura del adc de corriente en RM
    #conversiones
    VoltajeEnRDiv = round(LecturaEnRDiv*(4.096/32767),4) #Conversion de lectura a voltaje
    VoltajeEnRM = round(LecturaEnRM*(4.096/32767),4) #Conversion de lectura a voltaje
    #adc.stop_adc()#PUEDE QUE ESTE GENERANDO ERROR AL TENR QUE DETENER E INICIR EL ADC MYU RAPIDO
    #conversiones
    Vr = round((VoltajeEnRDiv*6.066),2)    #Calcula voltaje total
    VoltajeEnRM = VoltajeEnRM * 1000      #De decimal a mA
    Ir = round((VoltajeEnRM/(1+(67.3/4.646))),1)              #calcula voltaje en rm
    print("Voltaje RMS en RDiv:", VoltajeEnRDiv,"V           Voltaje RMS en la Celda:", Vr)
    Cof = [2.003,1.42,2.5,1]
    print("Voltaje PP en RM:", round((Vr*Cof[wf]),2),"V            Corriente en RM:", Ir,"mA")
    return Vr, Ir
#####################################################################################
vok = 0
vik = 0

vok3=0
vok2=0
vok1=0
vik3=0
vik2=0
vik1=0
def FiltroDigital(f,Ca,vok,vik,vok3, vok2, vok1, vik3, vik2, vik1):
    if f == 1:
        #vo=0.56801*vok+0.43191*vik;
        vo=0.98*vok+0.02*vik;
        vok=vo;
        vik=float(Ca);
    if f==2:
        vo=1.881483426*vok1-1.309460391*vok2+0.3173878886*vok3+0.01382363442*Ca+0.04147090325*vik1+0.04147090325*vik2+0.01382363442*vik3;
        vok3=vok2
        vok2=vok1
        vok1=vo

        vik3=vik2
        vik2=vik1
        vik1=Ca
        
    return round(vo,2), vok, vik, vok3, vok2, vok1, vik3, vik2, vik1
#######################################################################################
source = 26                    #control del rele
GPIO.setup(source, GPIO.OUT)   #configura el pin del rele como salida
#Conecta a fuente 1 0 fuente 2
def ReleIEG(estado):
    if(estado == 1):         
        GPIO.output(source, GPIO.HIGH)#apaga 
        print("Conectado a amplificador aislado")
    if(estado == 2):
        GPIO.output(source, GPIO.LOW)#PRENDE
        print("Conectado a fuente 5v")
######################################### EJE Z ###############################################
EnaZ = 16         # pin HABILITA DRIVER EN
DirZ = 20         # PIN DE DIRECCION CW
PulZ = 21         # PIN DE PULSOS/PASOS CLK
#configura resolucion de pasos
#1    -> 40, #1/2  -> 20, #1/8  -> 5, #1/16 -> 2.5
Resolucion = 2.5;
#configura pines como salida
GPIO.setup(EnaZ, GPIO.OUT)
GPIO.setup(DirZ, GPIO.OUT)
GPIO.setup(PulZ, GPIO.OUT)
GPIO.output(EnaZ, GPIO.HIGH)#Deshabilita motorEjeZ

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
    #genera el tren de pulsos
    for i in range(pulsos):
        GPIO.output(PulZ, GPIO.HIGH)
        sleep(pausa)
        GPIO.output(PulZ, GPIO.LOW)
        sleep(pausa)
    GPIO.output(EnaZ, GPIO.HIGH)#Deshabilita motorEjeZ
############################################ FIN EJE Z ############################################
#define pines
EnaX = 23 # pin HABILITA DRIVER EN EJE X
DirX = 24 # PIN DE DIRECCION CW EJE X
PulX = 25 # PIN DE PULSOS/PASOS CLK EJE X
#configura resolucion de pasos
#1    -> 40, #1/2  -> 20, #1/8  -> 5, #1/16 -> 2.5
Resolucion = 2.5;
#configura pines como salida
GPIO.setup(EnaX, GPIO.OUT)
GPIO.setup(DirX, GPIO.OUT)
GPIO.setup(PulX, GPIO.OUT)
GPIO.output(EnaX, GPIO.HIGH)#Deshabilita motorEjeZ
pausa = 0.0009
#######################Fin configura pines del sistema mecanico########################      
        
def EjeX(distancia):
    GPIO.output(EnaX, GPIO.LOW)#habilita motorEjeZ
    if distancia > 0:
        GPIO.output(DirX, GPIO.LOW)#Establece direccion DRECHA
        print("Derecha")
    if distancia < 0:
        GPIO.output(DirX, GPIO.HIGH)#Establece direccion IZQUIERDA
        distancia=distancia*-1
        print("Izquierda")
    pulsos = int(distancia//Resolucion) ###CALCULA CANTIDAD DE PULSOS PARA MOVERSE A LA DISTANCIA DESEADA
    print(pulsos)
    
    for i in range(pulsos):
        GPIO.output(PulX, GPIO.HIGH)
        sleep(pausa)
        GPIO.output(PulX, GPIO.LOW)
        sleep(pausa)
    GPIO.output(EnaX, GPIO.HIGH)#Deshabilita motorEjeZ
############################################## FIN EJE X#####################################################
    
def EstableceIEG(Fo):
    d = 0
    Contacto = False
    
    while Contacto == False:
        V, C = TomaLecturaVoltajeCorriente(Fo)
        if(C < 2.3):
            d = d - 5
            EjeZ(-5)
            Contacto = False
        if(C >= 2.3):
            Contacto = True

    EjeZ(240)#separa 240 IEG
    return d 
##################################Ventana de corriente################
def CalculaVC(Fo):
    #Retrocede un paso y toma voltaje y corriente bajos 
    EjeZ(20)
    sleep(1)
    VL, CL = TomaLecturaVoltajeCorriente(Fo)
    HL = time.time() - inicio
    print("Voltaje Bajo: ",VL," Corriente Baja: ",CL)
 
    #Corriente inicial IEG = 240
    EjeZ(-20)
    sleep(1)
    VI, CI = TomaLecturaVoltajeCorriente(Fo)
    HI = time.time() - inicio
    print("Voltaje Inicial: ",VI," Corriente Inicial: ",CI)
     
    #voltaje alto y corriente alta IEG = 237.5
    EjeZ(-20)
    sleep(1)
    VH, CH = TomaLecturaVoltajeCorriente(Fo)
    HH = time.time() - inicio
    print("Voltaje Alto: ",VH," Corriente Alta: ",CH)
    EjeZ(20) #IEG 240 INICIAL
    
    mi = min(CI,CH,CL)
    MA = max(CI,CH,CL)
    v=MA-mi
    VC = round(v,5)
    if VC == 0:#si no existe ventana de corriente por defecto 1mA
        VC= VC+1
    return VC, CL, CI, CH
#################################Ajuste de corriente inicial###############
def AjusteDeCorrienteInicial(Ca,C,VC):
    NAjustes = 0
    print("Ventana de Corriente: ",VC)
    if (C - Ca) >= VC:
        EjeZ(-10)
        NAjustes=10
    return NAjustes
##############################Calcula Area de exposicion###################
def calculaAE(d):
    if d <= 0:
        p = d*-1
    else:
        p = 0
    
    p = p/1000
    A = [0,0,0]
    De = 0.600
    Di = 0.380
    Aa = (math.pi*((De/2)**2)) - (math.pi*((Di/2)**2)) #area del anillo de la base del catodo
    Ap = (math.pi*De)*p                                #area de las paredes laterales del catodo
    At = Aa + Ap
    A[0]=round(Aa,3)
    A[1]=round(Ap,3)
    A[2]=round(At,3)
    #print("Area total:", round(A[2],3), "mm^2        >> Aa:",round(A[0],3),"  Ap:",round(A[1],3))
    return A
#############################Calcula IEG ##################################
AIEG = [0,0]
def calculaIEG(Ca,Va,A,Fo):
	if AIEG =  
    Fo = int(Fo)
    kFo = [0.4992,0.7042,0.4]
    r = 46.51 #resistividad del electrolito Ohm.mm
    c = round((Ca/1000),6)
    #IEG = (Va*A) / ((c/kFo[Fo])*r)-0.180
    IEG = (((Va*kFo[Fo])*A) / (c*r))-0.100
    return round((IEG*1000),1)
#######################################################################################################
#############################Calcula IEG ##################################
def calculaCi(nl,Fo):
    Ci = 0
    Ec = []
    E = 0
    for i in range(nl):
        V,C = TomaLecturaVoltajeCorriente(Fo)
        Ec.append(C)
        E = E + C
    CM = max(Ec)
    Cm = min(Ec)
    Ci = round(((E/nl)+((CM-Cm)/2)),3)
    return V,Ci
#######################################################################################################
###############################################################################################
def CalculaPendiente(y2,y1,x2,x1,Pi,tol):
    Ajuste = False
    TipoA = 0
    pendiente = round(((y2-y1)/(x2-x1)),4)
    error=0
    if(Pi[1]==1):                                    #si la pendiente inicial ya se calculo
        if ( pendiente >= (Pi[0]*(1+tol)) and pendiente <= (Pi[0]*(1-tol)) ):
            Ajuste = False
        else:
            Ajuste = True
            if (pendiente < (Pi[0]*(1+tol))): # si la pendieente es mneor a la pendiente menos 10 %
                TipoA = 1
                
            if ((pendiente > (Pi[0]*(1-tol))) and pendiente < 0): # si la pendiente es mayor a la pendiente mas 10% y menor a 0
                TipoA = -1
            if (pendiente >= 0):#si la pendiente es mayor a 0->incremnto mucho
                TipoA = 2
        
        print("PendienteI ",round(Pi[0],5),"     PendienteA",round(pendiente,5),"     Ajuste",Ajuste,"   Tipo de ajuste",TipoA)
    return pendiente, Ajuste, TipoA, error

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
def universoAreaE(PD):
    De = 0.6         #Diametro externo en mm
    Di = 0.380       #Diametro Interno en mm
    PD = PD/1000     #Profundidad deseada en mm 
    Ab = round((math.pi * ((De/2)**2))-(math.pi * ((Di/2)**2)),3) #Area de la base
    Ap = (math.pi*De)*(PD)                                        #Area de la pared
    AT = Ab + Ap                                                  #Area total
    pAb = round(((Ab*100)/AT),3)        #porcentaje del area de la base con respecto al area total
    pAp = round(((Ap*100)/AT),3)        #porcentaje del area de la base con respecto al area total
    pG = round((pAb + (pAp*(1/6))),3)
    pS = round((pAb + (pAp*(5/6))),3)
        
    print("% area de la base",pAb,"% area de la pared",pAp)
    #normaliza datos
    Z1 = round(((pAb)-0)/(100-0),2)
    Z2 = round((((pG)-0)/(100-0)),2)
    G = round((((pG)-0)/(100-0)),2)
    S1 = round((((pG)-0)/(100-0)),2)
    S2 = round((((pS)-0)/(100-0)),2)

    #print(Z1,Z2,G,S1,S2)
    #     X  z1  z2  g    m   s1  s2  X     X 
    AE = [0, Z1, Z2, G, 0.05, S1, S2, 1.1, 0.01]#limites del conjunto Aarea de Exposicion
    print(AE)
    return AE

def NormalizaDatos(di,D,AE,AT):
    di = round((di/D),3)
    AE = round((AE/AT),3)
    return di, AE

def DesnormalizaDatos(Vol,IEG):
    Vol = round((5 + (Vol*(9-5))),3)
    IEG = round((IEG * 40),3)
    return Vol, IEG
##PIDE DATOS A USUARIO
PD = float(input("Ingresa la profundidad deseada:"))#profundidad deseada
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$DIFUSO$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#     i   s1i   s1f  gm   gt   s2i  s2f  f     P            f
lI = [-1, -0.8,  0,   0, 0.1,   0,  0.8, 1.1, 0.01]#limites del universo dcorriente
AE = AE = universoAreaE(50)                     #limites dinamicos del universo Aarea de Exposicion
Gp = [-1, -0.8,-0.2,   0, 0.2, 0.2, 0.8, 1.1, 0.01]#limites del conjunto IEG
gv = [ 0, 0.10, 0.5, 0.5, 0.1, 0.5, 0.9, 1.1, 0.01]#limites del conjunto voltaje

#define los arreglos con el universo de discurso de los antecedentes, rango global
Corriente = ctrl.Antecedent(np.arange(lI[0],lI[7],lI[8]), 'Corriente')
AreaE = ctrl.Antecedent(np.arange(AE[0],AE[7],AE[8]), 'AreaE')

#define los arreglo de los universos de discurso de los consecuentes, rango global
IEG = ctrl.Consequent(np.arange(Gp[0],Gp[7],Gp[8]),'IEG')
GV = ctrl.Consequent(np.arange(gv[0],gv[7],gv[8]), 'Voltaje')

#define las variables lingúisticas y los limites de corrente
Corriente['Negativa'] = fuzz.zmf(Corriente.universe,lI[1],lI[2])
Corriente['Cero'] = fuzz.gaussmf(Corriente.universe,lI[3],lI[4])
Corriente['Positiva'] = fuzz.smf(Corriente.universe,lI[5],lI[6])
#define las variables lingúisticas y los limites de Area de exposición
AreaE['Inicial'] = fuzz.zmf(AreaE.universe,AE[1],AE[2])
AreaE['Intermedia'] = fuzz.gaussmf(AreaE.universe,AE[3],AE[4])
AreaE['Final'] = fuzz.smf(AreaE.universe,AE[5],AE[6])

#define las variables lingúisticas y los limites de la IEG
IEG['Cerca'] = fuzz.zmf(IEG.universe,Gp[1],Gp[2])
IEG['Estandar'] = fuzz.gaussmf(IEG.universe,Gp[3],Gp[4])
IEG['Lejos'] = fuzz.smf(IEG.universe,Gp[5],Gp[6])
#define las variables lingúisticas y los limites de voltaje
GV['Bajo'] = fuzz.zmf(GV.universe,gv[1],gv[2])
GV['Normal'] = fuzz.gaussmf(GV.universe,gv[3],gv[4])
GV['Alto'] = fuzz.smf(GV.universe,gv[5],gv[6])

#visualiza los conjuntos de las variables
#Corriente.view()
#AreaE.view()
#IEG.view()
#GV.view()
#Regals difusas
R1 = ctrl.Rule(Corriente['Negativa'] & AreaE['Inicial'], GV['Normal'])
R2 = ctrl.Rule(Corriente['Negativa'] & AreaE['Intermedia'], GV['Alto'])
R3 = ctrl.Rule(Corriente['Negativa'] & AreaE['Final'], GV['Alto'])
R4 = ctrl.Rule(Corriente['Cero'] & AreaE['Inicial'], GV['Bajo'])
R5 = ctrl.Rule(Corriente['Cero'] & AreaE['Intermedia'], GV['Normal'])
R6 = ctrl.Rule(Corriente['Cero'] & AreaE['Final'], GV['Alto'])
R7 = ctrl.Rule(Corriente['Positiva'] & AreaE['Inicial'], GV['Bajo'])
R8 = ctrl.Rule(Corriente['Positiva'] & AreaE['Intermedia'], GV['Bajo'])
R9 = ctrl.Rule(Corriente['Positiva'] & AreaE['Final'], GV['Normal'])

R10 = ctrl.Rule(Corriente['Negativa'] & AreaE['Inicial'], IEG['Cerca'])
R11 = ctrl.Rule(Corriente['Negativa'] & AreaE['Intermedia'], IEG['Cerca'])
R12 = ctrl.Rule(Corriente['Negativa'] & AreaE['Final'], IEG['Cerca'])
R13 = ctrl.Rule(Corriente['Cero'] & AreaE['Inicial'], IEG['Estandar'])
R14 = ctrl.Rule(Corriente['Cero'] & AreaE['Intermedia'], IEG['Estandar'])
R15 = ctrl.Rule(Corriente['Cero'] & AreaE['Final'], IEG['Estandar'])
R16 = ctrl.Rule(Corriente['Positiva'] & AreaE['Inicial'], IEG['Lejos'])
R17 = ctrl.Rule(Corriente['Positiva'] & AreaE['Intermedia'], IEG['Lejos'])
R18 = ctrl.Rule(Corriente['Positiva'] & AreaE['Final'], IEG['Lejos'])

#evalua las reglas
Vol_ctrl = ctrl.ControlSystem([R1, R2, R3, R4, R5, R6, R7, R8, R9])
IEG_ctrl = ctrl.ControlSystem([R10, R11, R12, R13, R14, R15, R16, R17, R18])
VolC = ctrl.ControlSystemSimulation(Vol_ctrl)
IEGC = ctrl.ControlSystemSimulation(IEG_ctrl)
#####################################Inicia Controlador Difuso##########################
######################################Inicia proceso###################################################
Fo = int(input("Selecciona la forma de onda de maquinado: 0: Sinosoidal, 1: Cuadrada,  2: Triangular:"))
if Fo == 0:
    Forma = "Sinusoidal"
if Fo == 1:
    Forma = "Cuadrada"
if Fo == 2:
    Forma = "Triangular"
VoltajeP = int(input("Ingresa el valor de VPP: "))
FHz = int(input("Ingresa la frecuencia: "))
CanalABin(3)# selecciona canal 0, señal nula
potenciometro(0)# sin cambio de ganacia potdig
ReleIEG(2)#1: Aislado, 2: Fuente 5V, conectado a fuente de 5V
sleep(0.25)
md = EstableceIEG(3)    #Desciende hasta hacer contacto y se separa 240 um
ReleIEG(1)#1: Aislado, 2: Fuente 5V, conectado a amplificador aislado

sleep(0.25)
Ee = input("Prende bomba de aire y agua e Igresa un numero para continuar ")
CanalABin(0)# selecciona canal 1= Sinosuidal
potenciometro(0)# sin cambio de ganacia potdig
sleep(3)
####################################################
#------------------------------------IEG normales---------------------------------
#VC,CL,CI,CH = CalculaVC(Fo)#Calcula ventana de corriente
#V, C = TomaLecturaVoltajeCorriente(Fo)
V,C = calculaCi(20,Fo)
y = C
z = C
#VC,CL,CI,CH = CalculaVC(Fo)#Calcula ventana de corriente
VC,CL,CI,CH = 5, C-5, C, C+5                #CalculaVC(Fo)#Calcula ventana de corriente
inicio = time.time()                        #Inicia a contar el tiempo
t = [round(time.time() - inicio,3)]         #Lista1 para almacenar al tiempo
Voltajes = [V]                              #lista2 para almacenar voltaje medido
Corrientes = [C]                            #lista3 para almacenar corriente medida
CorrientesF = [C]                           #lista4 para almacenar corriente filtrada
KVr = 0.0367                                #coeficiente de velocidad de remosion
Descenso = [240]                              #lista5 para almacenar el descenso del cátodo
A = calculaAE(0)                            #Area de exposicion inicial, area del anillo
AExp = [A[0]]                               #lista6 para almacenar el area de exposicion
DensidadI = [round(((C/1000)/A[2]),3)]             #lista7 para alamacenar la densidad de corriente
VelocidadA = [round(((KVr*C)/A[2]),3)]     #lista8 para almacenar la Velocidad de avance del cátodo
IEG = calculaIEG(C,V,A[0],Fo)
IEGl = [IEG]
vok = C                  #Inicia los coeficientes del filtro
vik = C                  #Inicia los coeficientes del filtro
tb = time.time() - inicio#tiempo base
Contador = 0

Adj = False#bandera de ajuste
tAdj = 0  #tiempo en el que se realizoe l ajuste
timeT = 0 #tiempo transcurrido desde el ajuste

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
listaError=[]
#while (time.time() - inicio) <= 121.0:
while ((Descenso[-1]-240) >= (-PD)): #mientras el descenso sea mayor a la profundidad deseada
    print("------------------------------",round((time.time() - inicio),0),"------------------------------")
    ta = time.time() - inicio #tiempo actuual
    Va, Ca = TomaLecturaVoltajeCorriente(Fo) #Voltaje, Corriente actual
    Csf = Ca
    vo,vok, vik,vok3, vok2, vok1, vik3, vik2, vik1 = FiltroDigital(1,Ca,vok, vik,vok3, vok2, vok1, vik3, vik2, vik1)#Corriente filtrado
    print("Corriente inicial",C,"                   Corriente Actual",vo,"               Ventana de corriente",round(C-vo,2))
    Ca = vo                                              #usa la corriente filtrada
    A = calculaAE(Descenso[-1])                          #Calcula el Area de exposicion(cambia variable de negativa a positiva)
    VAa = round(((KVr*vo)/A[2]),3)                       #Calcula la velocidad de Avance actual 
    IEG = calculaIEG(vo,Va,A[2],Fo)                      #Calcula IEG actual
    d = 0
    if Contador == 10:  ##espera a que se estabilice
        print("Estabilizado")
        Px1 = ta
        Py1 = vo
        ti = ta
        PX.append(Px1)
        PY.append(Py1)
    if (ta-ti) >= TMuestra:#si el tiempo transcurrido es igual al tamaño de muestra
        #print("")
        Px2 = ta
        Py2 = vo
        #print(Py2,Py1,Px2,Px1)
        Pendiente, Ajuste, TipoA, errorP = CalculaErrorEnLaPendiente(Py2,Py1,Px2,Px1,PendienteI,tol)
        listaError.append(errorP)
        
        if(PendienteI[1]==0):              ##si no se  ha calculado la pendiente inicial
            PendienteI[0]=Pendiente         #asigna la pendiente inicial
            PendienteI[1]=1                 #
            if(PendienteI[1]==1):         #si ya se calculo la pendiente inicial
                if(PendienteI[0] > -0.1):   #si la pendiente inicial es muy pequeña o positiva
                    PendienteI[0] = -0.25    #asigna pendiente por default
        #print("Pendiente ",Pendiente,"Ajuste",Ajuste)
        ti = ta
        Contador = 0
        PX.append(Px2)
        PY.append(Py2)
        #####################################################difusi#################################
        AreaTotal = calculaAE(-PD)
        AreaActual = calculaAE(Descenso[-1])
        print("Area Actual: ",AreaActual,"       Area Total: ",AreaTotal[2])
        din, AEn = NormalizaDatos(errorP,5,AreaActual[2],AreaTotal[2])#normaliza datos
        print("ENTRADAS AL CONTROLADOR")
        print("Valor del Error",errorP, din)
        print("Valor deñ area de exposicion",AreaActual,AEn)
        VolC.input['Corriente'] = din
        VolC.input['AreaE'] = AEn
        IEGC.input['Corriente'] = din
        IEGC.input['AreaE'] = AEn
        #procesa el resultado
        VolC.compute()
        IEGC.compute()
        #Calcula el resultado
        nVol = round(VolC.output['Voltaje'],3)
        nIEG = round(IEGC.output['IEG'],3)

        #desnormaliza datos
        dV, dIEG = DesnormalizaDatos(nVol,nIEG)
        print("SALIDA DEL CONTROLADOR")
        print("Valor de Voltaje:",nVol, dV)
        print("Valor de IEG:",nIEG, dIEG)
        d = dIEG
        if ((d > -2.5) and (d < 0)):
            d = -2.5
        if ((d > 0) and (d < 2.5)):
            d = 2.5
        EjeZ(d)#realiza el ajuste de la IEG
        #####################################################difusi#################################
    Contador  = Contador + 1
    
    print("IEG actual",IEG,"                     Posicion del electrodo: ", Descenso[-1],"              AreaExp: ",A[2])
    
    t.append(round(ta,3))                                      #L1 ingresa nuevo tiempo de muestreo
    Voltajes.append(Va)                                        #L2 ingresa el voltaje actual
    Corrientes.append(Csf)                                      #L3 ingresa la corriente actual      
    CorrientesF.append(vo)                                     #L4 ingresa la corriente actual filtrada
    Descenso.append(Descenso[-1]+d)                            #L5 ingresa el descenso actual
    AExp.append(A[2])                                          #L6 Ingresa el area de exposicion
    DensidadI.append(round(((vo/1000)/A[2]),3))                #L7 Ingresa la densidad de corriente
    VelocidadA.append(VAa)                                     #L8 ingresa la velocidad de avance actual
    IEGl.append(IEG)

CanalABin(3)                          #selecciona canal 3= Señal nula
EjeZ(2000)                            #levanta el electrodo
print("Ventana de corriente: ",VC,"                       Profundidad aparente: ",(Descenso[-1]-240))
print("Pendiente Inicial", PendienteI[0])
EjeX(-2000)

#print("Profundidad aparente: ",mp, mp+240)
##########################################################
#inicia modulo de guardadr datos---------------------------------------------------
tm=t[-1]
Hora = time.strftime("%X")
Hora = str(Hora[0]+Hora[1]+Hora[3]+Hora[4]+Hora[6]+Hora[7])
Dt = datetime.datetime.now()

NombreF = str(Dt.day)+str(Dt.month)+" "+Hora+" "+Forma+str(VoltajeP)+"V"+str(tm)+"s2"
with open(NombreF+".csv", 'w', newline='') as MaquinadoFile:
    csvwriter = csv.writer(MaquinadoFile)
    csvwriter.writerow(['Forma', Forma])
    csvwriter.writerow(['Frecuencia', FHz])
    csvwriter.writerow(['Voltaje RMS',round((Voltajes[0]),2)])
    csvwriter.writerow(['Corriente inicial', C])
    csvwriter.writerow(['Pendiente inicial', PendienteI[0]])
    csvwriter.writerow(['C',C])
    csvwriter.writerow(['CI',CI])
    csvwriter.writerow(['CL',CL])
    csvwriter.writerow(['CH',CH])
    csvwriter.writerow(['t','V_RMS','iRMS','iFRMS','Descenso','AExp','DensidadI','VelocidadA','IEGc'])
    for i in range(len(t)):
        csvwriter.writerow([t[i],Voltajes[i],Corrientes[i],CorrientesF[i],Descenso[i],AExp[i],DensidadI[i], VelocidadA[i],IEGl[i]])
##########################################################
#grafica los datos
plt.errorbar(t, CorrientesF, label='Corriente')
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
    #n = "pendiente"+str(i)
    #plt.plot(lx,ly,label=n)
    plt.plot(lx,ly,color="k")
plt.grid(True)
nC = NombreF+'Cf.png'
plt.savefig(nC,format='png',dpi=1200)
#plt.show()
plt.clf()
print("Figura 0 guardada")
################3##############3guarda imagen
plt.errorbar(t, Corrientes, label='Corriente')
plt.errorbar(t, CorrientesF, label='Corriente Filtrada')
plt.legend(loc='upper right')
plt.ylabel('Corriente (mA)')
plt.xlabel('Tiempo (s)')
plt.grid(True)
nC = NombreF+'C.png'
plt.savefig(nC,format='png',dpi=1200)
plt.clf()
print("Figura 1 guardada")
############################################3
plt.errorbar(t, Descenso, label='Descenso')
#plt.errorbar(t, IEGl, label='IEG')
plt.legend(loc='upper right')
plt.ylabel('Descenso de la herramienta de trabbajo (µm)')
plt.xlabel('Tiempo (s)')
plt.grid(True)
nP = NombreF+'P.png'
plt.savefig(nP,format='png',dpi=1200)
plt.clf()
print("Figura 2 guardada")
##########################################################
#plt.errorbar(t, DensidadI, label='Densidad de corriente')
#plt.legend(loc='upper right')
#plt.ylabel('Densidad de corriente (mA/µm^2)')
#plt.xlabel('Tiempo (s)')
#plt.grid(True)
#nVA = NombreF+'DC.png'
#plt.savefig(nVA,format='png',dpi=1200)
#plt.show()
#plt.clf()
#print("Figura 3 guardada")
######################################################
#plt.errorbar(t, VelocidadA, label='Velocidad')
#plt.legend(loc='upper right')
#plt.ylabel('Velocidad de avance de la herramienta de trabajo (µm/s)')
#plt.xlabel('Tiempo (s)')
#plt.grid(True)
#nVA = NombreF+'VA.png'
#plt.savefig(nVA,format='png',dpi=1200)
#plt.show()
#plt.clf()
#print("Figura 4 guardada")
#############################################
a = np.arange(0,len(listaError),1)
plt.plot(a, listaError, label='Error')
plt.legend(loc='upper right')
plt.ylabel('Error en la pendiente')
plt.xlabel('Tiempo (s)')
plt.grid(True)
nEP = NombreF+'EP.png'
plt.savefig(nEP,format='png',dpi=1200)
plt.clf()
print("Figura 5 guardada")
#############################################
AreaE.view()
adc.stop_adc()
#GPIO.cleanup()
print('Prueba ECM MODULOS terminada')
