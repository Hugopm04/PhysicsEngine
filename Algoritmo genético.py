import os
import time
import random
import numpy as np
import psutil
import Fisica_IA
import concurrent.futures
from multiprocessing import Pool
from shutil import rmtree
from shutil import copytree

ASK_COMPUTATION_RATE = True

SIMULACION_A_OPTIMIZAR = "Simulaciones/movimiento parabolico"
DIRECTORIO_PARAMETROS = "Parametros"
DIRECTORIO_PADRES = "IA/Simulaciones"
DIRECTORIO_HIJOS = "IA/temp"
DIRECTORIO_MEJORES = "IA/Mejores"

ERROR_MAX = 10**(-4)
PUNTUACION_MIN = 1 / ERROR_MAX

def Seleccion(puntuaciones, individuos_por_generacion):
    #Normalizamos las puntuaciones.
    if puntuaciones.max() > 0:
        puntuaciones_normalizadas = puntuaciones / puntuaciones.max()
        puntuaciones_normalizadas *= 100
    else:
        #Todas las puntuaciones son nulas:
        puntuaciones_normalizadas = puntuaciones + 1
        puntuaciones_normalizadas *= 100

    supervivientes = []
    while len(supervivientes) < individuos_por_generacion:
        for i, puntuacion in enumerate(puntuaciones_normalizadas):
            dado = random.randint(1, 100)
            if puntuacion >= dado:
                supervivientes.append(i)
            
            if len(supervivientes) == individuos_por_generacion:
                break
    
    return(supervivientes)

def CrearHijo(id_padre, id_hijo):
    parametros = Fisica_IA.CargarDiccionario("Parametros.json")
    
    hijo = Fisica_IA.Entorno()
    hijo.Cargar(DIRECTORIO_PADRES + "/" + str(id_padre), reiniciada=True, ia=True)
    
    cuerpos = parametros["Cuerpos"]
    for nombre in cuerpos:
        cuerpo = hijo.cuerpos[nombre]
        for parametro in cuerpos[nombre]:
            if parametro == "Velocidad":
                for i, componente in enumerate(cuerpo.velocidad):
                    mutacion = TipoMutacion()
                    if mutacion == "Cambiazo":
                        nuevo_valor = np.random.random() * 0.02 - 0.01
                        if nuevo_valor != 0:
                            nuevo_valor = 1 / nuevo_valor #Para permitir a lo largo de todos los reales.

                    elif mutacion == "Escalar":
                        escala = np.random.random() + 0.5
                        nuevo_valor = componente * escala
                    
                    elif mutacion == "Variacion":
                        variacion = np.random.random() * 2 - 1
                        nuevo_valor = componente + variacion
                    
                    elif mutacion == "Cambio de signor":
                        nuevo_valor = - componente
                    
                    else:
                        nuevo_valor = componente
                    
                    cuerpo.velocidad[i] = nuevo_valor
    
    hijo.ID = id_hijo
    hijo.Guardar(DIRECTORIO_HIJOS + "/" + str(id_hijo))
    hijo.puntuacion = PuntuarSimulacion(hijo)
    return(hijo)

def TipoMutacion(): #https://stackoverflow.com/questions/31708478/how-to-evolve-weights-of-a-neural-network-in-neuroevolution
    PROBABILIDADES = { #En tanto por mil.
        "Cambiazo":10,
        "Escalar":50,
        "Variacion":300,
        "Cambio de signo":10,
    }
    
    for mutacion in PROBABILIDADES:
        dado = random.randint(1, 1000)
        probabilidad = PROBABILIDADES[mutacion]
        if probabilidad >= dado:
            return(mutacion)
    
    return(None)

def get_computer_data():
    if ASK_COMPUTATION_RATE:
        computation_rate = input("¿Cuánto potencial de tu ordenador pones a calcular? (Escribe un número del uno al cien): ")
        try:
            computation_rate = float(computation_rate)
        except:
            print("Eso no es una respuesta válida, asegúrate de haber escrito los decimales con punto y sin espacios.")
            exit()
        
        if computation_rate < 0:
            print("Con que un graciosillo poniendo valores negativos a ver que pasa ¿eh? Ya te lo digo yo:")
            time.sleep(1)
            print("Comenzando autodestrucción, 3 segundos restantes...")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1")
            time.sleep(1)
            print("KAPUM!")
            exit()
        
        computation_rate /= 100
        
    else:
        computation_rate = 1
    
    max_frecuency = psutil.cpu_freq().max
    frecuency_difference = max_frecuency / 2900
    generation_difference = (frecuency_difference * 1.3333333) / 1.26953618552599
    generation_size = generation_difference * 5
    generation_size = round(generation_size * computation_rate)
    if generation_size < 1:
        generation_size = 1
    
    return(generation_size)

def PuntuarSimulacion(entorno):

    objetivos = Fisica_IA.CargarDiccionario("Objetivos.json")
    
    tiempo_transcurrido = 0
    deltatime = 1 / entorno.configuracion["Cantidad de calculos"]
    tiempo_total = entorno.configuracion["Tiempo total"]
    range_kutta = entorno.configuracion["Orden Range-Kutta"]
    
    while tiempo_transcurrido < tiempo_total:
        entorno.Simular(deltatime, range_kutta)
        tiempo_transcurrido += deltatime
    
    error_total = 0
    for nombre in objetivos:
        cuerpo = entorno.cuerpos[nombre]
        
        for caracteristica in objetivos[nombre]:
            objetivo = objetivos[nombre][caracteristica]
            if caracteristica == "posicion":
                objetivo = np.array(objetivo).reshape(3)
                diferencia = abs(objetivo - cuerpo.posicion)
                error = np.sum(diferencia)
            error_total += error
    
    if error != 0:
        puntuacion = 1 / error
    
    entorno.puntuacion = puntuacion
    return(puntuacion)
    
if __name__ == '__main__':

    rmtree(DIRECTORIO_MEJORES)
    os.mkdir(DIRECTORIO_MEJORES)
    
    individuos_por_generacion = get_computer_data()

    parametros = Fisica_IA.CargarDiccionario("Parametros.json")
    objetivos = Fisica_IA.CargarDiccionario("Objetivos.json")
        
    maxima_puntuacion = 0
    id_maxima_puntuacion = 0
    puntuaciones = np.array([])
    procesos = []
    entornos_iniciales = []
    for ID in range(individuos_por_generacion):
        simulacion = Fisica_IA.Entorno(ID)
        simulacion.Cargar(SIMULACION_A_OPTIMIZAR, reiniciada=True, ia=True)
        simulacion.Generar(parametros)
        simulacion.objetivos = objetivos
        simulacion.Guardar(DIRECTORIO_PADRES + "/" + str(ID))

        entornos_iniciales.append(simulacion)
    
    with Pool(individuos_por_generacion) as p:
        puntuaciones = p.map(PuntuarSimulacion, entornos_iniciales)
    
    np_puntuaciones = np.array([])
    for puntuacion in puntuaciones:
        np_puntuaciones = np.append(np_puntuaciones, puntuacion)
    
    puntuaciones = np_puntuaciones
    
    del(np_puntuaciones)
    del(entornos_iniciales)
    
    generacion_actual = 0
    contador_prints = 0
    with concurrent.futures.ProcessPoolExecutor() as executor:
        while True:
            if contador_prints % 10 == 0:
                print("Comenzando generación Nº:", generacion_actual)
            
            supervivientes = Seleccion(puntuaciones, individuos_por_generacion)
            puntuaciones = np.array([])

            #Creamos a las simulaciones hijo utilizando multiprocesamiento:
            hijos = executor.map(CrearHijo, supervivientes, [i for i in range(individuos_por_generacion)])
            
            for hijo in hijos:
                puntuaciones = np.append(puntuaciones, hijo.puntuacion)
                if hijo.puntuacion > maxima_puntuacion:
                    maxima_puntuacion = hijo.puntuacion
                    id_maxima_puntuacion = len(os.listdir(DIRECTORIO_MEJORES))
                    
                    print("Nueva máxima puntuación! ({}), por:{} ({})".format(maxima_puntuacion, id_maxima_puntuacion, hijo.ID))
                    
                    hijo.Cargar(DIRECTORIO_HIJOS + "/" + str(hijo.ID), reiniciada=True, ia=True)
                    hijo.Guardar(DIRECTORIO_MEJORES + "/" + str(id_maxima_puntuacion))
                    
                    if maxima_puntuacion > PUNTUACION_MIN:
                        print("FIN!")
                        exit()
            
            rmtree(DIRECTORIO_PADRES)
            copytree(DIRECTORIO_HIJOS, DIRECTORIO_PADRES)

            generacion_actual += 1
            contador_prints += 1