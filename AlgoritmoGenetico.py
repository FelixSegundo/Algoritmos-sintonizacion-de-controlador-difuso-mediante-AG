#!/usr/bin/env python
# coding: utf-8

# In[89]:


import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import time 
import random
import os
import csv
import statistics

from matplotlib import pyplot as plt

def PoblacionInicial():
    print("Cargando poblacion inical")
    poblacion=[]
    os.chdir("C:/RutaDondeSeEncuentraElArchivo.csv")
    os.getcwd()
    f= open("DatosGen.csv")
    reader = csv.reader(f)
    i = 0
    for row in reader:
        if i == 0:
            i = i+1
            continue
        poblacion.append([])                                          #agrega una fila vacia al array
        Valor = 0
        for j in range(len(row)):
            Valor = float(row[j])                                    #Convierte valor de string a float
            poblacion[i-1].append(Valor)
        i = i+1
        
    #print("Poblacion inicial de:",len(poblacion),"individuos y ",len(row),"genes")
    return poblacion

def CalculaMAPE(P):
    #print("Calculado MAPE de la poblacion",len(P),len(P[0]))
    MAPE = 0
    E = 0
    for i in range(len(P)):
        E = E + P[i][24]
    #print("Error acomulado",E)
    MAPE = E / (len(P))
    return round(MAPE,4), E

def SeleccionRuleta(P):
    #print("SELECCION POR RULETA")
    ##Calcular Desempeño 1/MAPE Y Desempeño ACOMULADO
    Desempeño = []
    DesempeñoTotal = 0
    T = len(P)
    for i in range(T):
        Desempeño.append(1/P[i][24])
        DesempeñoTotal = DesempeñoTotal + Desempeño[-1]
        
    p = []
    q = []
    a = []
    
    #calcula probabilidad de cada individuo y probabilidad acomulada
    for i in range(T):
        auxD = Desempeño[i]/DesempeñoTotal
        p.append(auxD)
        q.append(sum(p))
        #a.append(0.8)
        a.append(random.uniform(0, 1))
        
    ##elige los individuos a partir de su probabilidad con respecto a alfa
    pS = []
    for i in range(T):
        aux = False
        for j in range(T):
            if q[j]>a[i] and aux == False:
                I = P[j]
                pS.append(I)
                aux = True
    
    #print("Individuos seleccionados",len(pS), "con ",len(pS[0]),"genes")
    return pS

def Cruza(P):
    #print("Combina padres")
    t = len(P)
    tc = len(P[0])
    #print("numero de individuos",t,tc)
    NP = []                                        #contenedor de nueva poblacion
    a = random.uniform(0, 1.0)
    for i in range(0,t,2):                         #avanza por parejas
        H1 = P[i]                    #hijo 1, 
        H2 = P[i+1]                  #hijo 2,
        P1 = P[i]                    #padre 1,
        P2 = P[i+1]                  #padre 2,
        for j in range(tc):
            if(j==0 or j==5 or j==9 or j==12 or j==17 or j==18 or j==23):
                C1 = round(((P1[j]*a) + (P2[j]*(1-a))),3)
                C2 = round(((P2[j]*a) + (P1[j]*(1-a))),3)
                H1[j]=C1 
                H2[j]=C2
            if j==24:
                ######################sp2
                #E1 = 0
                #E2 = 0
                #if P1[24]>P2[24]: # si el padre uno es mayor al padre dos
                #    E1 = P1[24]-((P1[24]-P2[24])*a)
                #    E2 = P2[24]
                #if P2[24]>P1[24]: # si el padre dos es mayor al padre uno
                #    E2 = P2[24]-((P2[24]-P1[24])*a)
                #    E1 = P1[24]
                #if P1[24]==P2[24]:
                #    E2 = P2[24]
                #    E1 = P1[24]
                ###############################SP1    
                #PV = round(((P1[24]+P2[24])/2),2) #calcula el promedio de ambos padres
                #E1 = 0
                #E2 = 0
                #if P1[24]>P2[24]: # si el padre uno es mayor al padre dos
                #    E1 = PV
                #    E2 = P2[24]
                #if P2[24]>P1[24]: # si el padre dos es mayor al padre uno
                #    E2 = PV
                #    E1 = P1[24]
                #if P1[24]==P2[24]:
                #    E2 = P2[24]
                #    E1 = P1[24]
                H1[j] = BusquedaDeParientes(P,H1)
                H2[j] = BusquedaDeParientes(P,H2)  
            
        NP.append(H1)
        NP.append(H2)
      
    return(NP)
def BusquedaDeParientes2(P,H): #recibe como parametro la poblacion y el hijo
    
    ListaSimilitudes = []  #almacena la coantidad de genes similares del individuo y toda la población
    for i in range(len(P)):
        ValorSimilitud = []    #almacena el valor de la similitud de cada gen entre el hijo y un individuo
        Ind = P[i] #asigna individuo i  
        for j in range(len(P[0])-1): #busca similitud en cada gen, excepto en el gen de error
            if(j==0 or j==5 or j==9 or j==12 or j==17 or j==18 or j==23):
                vs = abs(Ind[j]-H[j]) #calcula la similitud como valor absoluto       
                ValorSimilitud.append(vs)# agrega el valor de similitud al vector
        vsmax = max(ValorSimilitud)#calcula el valor maximo de similitud
        ngs = 0 #contador de genes similares
        for k in range(len(ValorSimilitud)):
            if ValorSimilitud[k] < vsmax: # si el valor de similitud es menor al valor maximo
                ngs = ngs + 1
        ListaSimilitudes.append(ngs) #agrga el numero de genes similares a la lista
    ##ahora 
    elementos = [a[0]]
    for i in range(len(a)):
        band = 0
        for j in range(len(elementos)):
            if a[i]==elementos[j]:
                band = 1
        if band == 0:
            elementos.append(a[i])
    #moda = statistics.mode(ListaSimilitudes)
    mediana = statistics.median_low(ListaSimilitudes)#calcula la media baja
    sumaE = 0 #suma el error de cada pariente
    nC = 0 # hace el conteo de parientes
    print(mediana)
    print(ListaSimilitudes)
    for i in range(len(ListaSimilitudes)):
        if(ListaSimilitudes[i] == mediana):
            sumaE = sumaE+P[i][24]
            nC = nC+1
    EpP = round((sumaE/nC),2)#error en la profundidad proedio de los parientes
    return EpP

def BusquedaDeParientes(P,H):
    ValorSimilitud = []    #almacena el valor total de la similitud entre el hijo y cada individuo
    SimiOrd = []           #almacena el valor de similitud pero de manera ordenada
    indice = []
    for i in range(len(P)-1):
        I = P[i]
        #score = (P[i][0]-H[0])+(P[i][5]-H[5])+(P[i][9]-H[9])+(P[i][12]-H[12])+(P[i][7]-H[17])+(P[i][18]-H[18])+(P[i][23]-H[23])
        score = abs(I[0]-H[0])+abs(I[5]-H[5])+abs(I[9]-H[9])+abs(I[12]-H[12])+abs(I[7]-H[17])+abs(I[18]-H[18])+abs(I[23]-H[23])
        ValorSimilitud.append(round(score,4))
    AuxSim = ValorSimilitud.copy()   #copia la lista de valores de similitud
    ValorSimilitud.sort()            #ordena la lista de valores de similitud
    
    for i in range(len(ValorSimilitud)):
        if ValorSimilitud[0] == AuxSim[i]:
            vp1 = P[i][24]
        if ValorSimilitud[1] == AuxSim[i]:
            vp2 = P[i][24]
    peP = (vp1 + vp2)/2    

    return peP

def OrdenaPoblacion(P):
    AuxE = []              #vector de eror cada individuo
    AuxI = []              #vector para evitar sobreescribir
    PO = []                #poblacion ordenada
    T = len(P)
    for i in range(T):
        AuxE.append(P[i][24])       #extrae el error del individuo y lo almacena
        AuxI.append(0)              #se llena el array con 0
    #AuxE.sort(reverse=True)         #ordena el vector de error de manera descendente
    AuxE.sort()                     #ordena el vector de error de manera ascendente
    for i in range(T):
        for j in range(T):
            if AuxE[i] == P[j][24] and AuxI[j]==0:  #busca el elemnto del vector ordenado en la poblacion
                PO.append(P[j])
                AuxI[j] = 1
    return PO

def Reemplazo(P,H,r):
    T = len(P)
    ph= int(round(T*r,0))
    pp= int(T-ph)
    
    Np = []
    for i in range(pp):         
        Np.append(P[i])          #llena nueva poblacion con los mejores padres
    for i in range(ph):
        Np.append(H[i])          #llena nueva poblacion con los mejores hijos
        
    return Np

def MuestraError(P):
    T = len(P)
    E = []
    for i in range(T):
        v = P[i][24]
        E.append(v)
    return E

def CompilaAG(nG):
    print("Iniciando Algoritmo genético")
    P = PoblacionInicial()  
    IIp = P[0]                                  #Primer individuo de la poblacion original
    MAPE,E = CalculaMAPE(P)
    print("MAPE: ",MAPE)
    Desempeño = [MAPE]
    G = [1]
    while G[-1] < nG:
        print("_______________Generacion",G[-1],"___________")
        #print("cantidad de padres",len(P))
        PS = SeleccionRuleta(P)            #Selecciona individuos de la poblacion inicial
    
        H = Cruza(PS)                      #cruza a los padres y obtiene a los hijos
        P = OrdenaPoblacion(PS)            ###Ordena la poblacion para seleccionar a los mejores
        H = OrdenaPoblacion(H)             ###Ordena la poblacion para seleccionar a los mejores
        nP = Reemplazo(P,H,0.80)           #reemplaza un porcentaje de los padres con los hijos 
    
        MAPE,E = CalculaMAPE(nP)           #Calcula el error MAPE de la nueva poblacion
        random.shuffle(nP)                 ###DESORDENA LA POBLACION 
        P = nP
    
        print("MAPE",MAPE)
        Desempeño.append(MAPE)
        G.append(int(G[-1]+1))
    print(P[0])
    print(P[0][0:6])
    print(P[0][6:12])
    print(P[0][12:18])
    print(P[0][18:24])
    return Desempeño
##############################################################################################
print("Ejecucion de Funciones sin errores")
############################################################################################


# In[90]:


#/////////////////////////////////////////////////////////////////////////////////////////////
Repetibilidad20 = []
nR = 40
nG = 20
for r in range(nR):
    Desempeño20 = CompilaAG(nG)
    Repetibilidad20.append(Desempeño20)

Val20 = []
for i in range(len(Repetibilidad20)):
    Val20.append(Repetibilidad20[i][-1])

plt.boxplot(Val20)
plt.ylabel('MAPE')



# In[53]:


Repetibilidad40 = []
nR = 40
nG = 40
for r in range(nR):
    Desempeño40 = CompilaAG(nG)
    Repetibilidad40.append(Desempeño40)

Val40 = []
for i in range(len(Repetibilidad40)):
    Val40.append(Repetibilidad40[i][-1])
    
plt.boxplot(Val40)
plt.ylabel('MAPE')    


# In[49]:


Repetibilidad60 = []
nR = 40
nG = 60
for r in range(nR):
    Desempeño60 = CompilaAG(nG)
    Repetibilidad60.append(Desempeño60)
    
Val60 = []
for i in range(len(Repetibilidad60)):
    Val60.append(Repetibilidad60[i][-1])    

plt.boxplot(Val60)
plt.ylabel('MAPE')  


# In[54]:


Repetibilidad80 = []
nR = 40
nG = 80
for r in range(nR):
    Desempeño80 = CompilaAG(nG)
    Repetibilidad80.append(Desempeño80)
    
Val80 = []
for i in range(len(Repetibilidad80)):
    Val80.append(Repetibilidad80[i][-1])    

plt.boxplot(Val80)
plt.ylabel('MAPE')  


# In[85]:


#G = np.arange(1,nG+1,1)     
#print("Individuo Progenitor")
#print(IIp)
#print(len(P[0]))  

############################################################################################
GG = np.arange(1,len(Repetibilidad20[0])+1,1)
for r in range(len(Repetibilidad20)):
    plt.plot(GG, Repetibilidad20[r])#, label='MAPE')
plt.legend(loc='lower right')
plt.ylabel('MAPE')
plt.xlabel('Generación')
plt.xticks(GG)
plt.grid(True)
plt.figure(figsize=(12,6))
plt.show()
#############################################################################
plt.plot(GG, Repetibilidad20[0])#, label='MAPE')
plt.legend(loc='lower right')
plt.ylabel('MAPE')
plt.xlabel('Generación')
plt.xticks(GG)
plt.grid(True)
plt.figure(figsize=(12,6))
plt.show()


# In[77]:


print("Promedio G20", statistics.mean(Val20))
print("Mediana G20", statistics.median(Val20))
print("Moda G20", statistics.mode(Val20))
print("")
print("Promedio G40", statistics.mean(Val40))
print("Mediana G40", statistics.median(Val40))
print("Moda G40", statistics.mode(Val40))
print("")
print("Promedio G60", statistics.mean(Val60))
print("Mediana G60", statistics.median(Val60))
print("Moda G60", statistics.mode(Val60))
print("")
print("Promedio G80", statistics.mean(Val80))
print("Mediana G80", statistics.median(Val80))
print("Moda G80", statistics.mode(Val80))
cajas = [Val20,Val40,Val60,Val80]

plt.boxplot(cajas,labels=[20,40,60,80])
plt.ylabel('MAPE')
plt.xlabel('Generaciones')
plt.show()


# In[ ]:





# In[ ]:




