#https://www.youtube.com/watch?v=T-pxFvh4hF0&ab_channel=GastonCarrera

import pygame
import numpy as np
import math
from pygame.locals import *
import os
import json
from shutil import rmtree

#Dimensiones de la ventana
ANCHO = 1500
ALTO = 750
PROFUNDO = 500

RASTROS = True

SEPARACION_CAMPOS_UNIFORMES = 100

CONFIGURACION = {"Cantidad de calculos":25,
                "Orden Range-Kutta":4,
                "Tiempo total":-1,
                "Ancho":1500,
                "Alto":750,
                "Rastros":True,
                "Informacion":True,
                "Separacion campos":100}

def Simulacion(nombre_simulacion, reiniciada=False):
    
    entorno = Entorno()
    entorno.Cargar(nombre_simulacion, reiniciada)
    
    cantidad_de_calculos = entorno.configuracion["Cantidad de calculos"]

    range_kutta = entorno.configuracion["Orden Range-Kutta"]

    tiempo_total = entorno.configuracion["Tiempo total"]

    ancho = entorno.configuracion["Ancho"]

    alto = entorno.configuracion["Alto"]

    rastros = entorno.configuracion["Rastros"]

    informacion = entorno.configuracion["Informacion"]

    separacion_campos_uniformes = entorno.configuracion["Separacion campos"]

    
    deltatime = 1 / cantidad_de_calculos
    
    #Set up de la ventana
    pygame.init()
    pygame.display.set_caption(nombre_simulacion)
    ventana = pygame.display.set_mode((ancho, alto))
    
    TIPOGRAFIA = pygame.font.SysFont("Calibri", 20) #Tipografía de la información en pantalla.
    NUMERACION = pygame.font.SysFont("Calibri", 15)
    
    label_tiempo_auxiliar = TIPOGRAFIA.render("Tiempo: ", False, (225, 225, 225))
    
    pausa = False #Variable de control, representa si se debe seguir con la simulación o si se debe detener.
    iteraciones_transcurridas = 0 #Variable que almacena las iteraciones realizadas.
    tiempo_transcurrido = 0
    
    if len(entorno.campos) == 0:
        print("Energía inicial: ", entorno.Energia())
    
    while tiempo_transcurrido < tiempo_total or tiempo_total == -1:
        #Toma de inputs:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #Si queremos cerrar la ventana.
                pygame.quit()
                exit()
            
            elif event.type == MOUSEWHEEL: #Control del zoom de la cámara.
                entorno.camara.zoom += event.y * entorno.camara.velocidad_zoom
                BorrarRastros(entorno.cuerpos)
                if entorno.camara.zoom < 0:
                    entorno.camara.zoom = 0
   
            elif event.type == pygame.KEYDOWN: #Para pulsaciones de teclas:
                if event.key == pygame.K_p: #Pausa (p)
                    if pausa:
                        pausa = False
                    else:
                        pausa = True
                
                elif event.key == pygame.K_q: #Salir (q)
                    pygame.quit()
                    return()
                    
                elif event.key == pygame.K_i: #Mostrar/Ocultar información:
                    informacion = not informacion
                
                elif event.key == pygame.K_r: #Reiniciar la simulación:
                    Simulacion(nombre_simulacion, reiniciada=True)
                    return()
                
                elif event.key == pygame.K_g: #Guardar la simulación:
                    entorno.Guardar(nombre_simulacion)
                            
        #Toma de inputs dinámicos: https://realpython.com/pygame-a-primer/
        teclas_pulsadas = pygame.key.get_pressed()
        #Movimiento de la cámara:
        if teclas_pulsadas[K_d]: #Derecha
            entorno.camara.aceleracion += np.array([100.0, 0.0, 0.0])
            
        if teclas_pulsadas[K_a]: #Izquierda
            entorno.camara.aceleracion -= np.array([100.0, 0.0, 0.0])
        
        if teclas_pulsadas[K_w]: #Arriba
            entorno.camara.aceleracion += np.array([0.0, 100.0, 0.0])
        
        if teclas_pulsadas[K_s]: #Abajo
            entorno.camara.aceleracion -= np.array([0.0, 100.0, 0.0])
        
        if teclas_pulsadas[K_z]: #Entrante
            entorno.camara.aceleracion += np.array([0.0, 0.0, 5.0])
            
        if teclas_pulsadas[K_x]: #Saliente
            entorno.camara.aceleracion -= np.array([0.0, 0.0, 5.0])
        
        if teclas_pulsadas[K_MINUS]: #Reducir la velocidad de simulación:
            deltatime -= 0.001
            if deltatime < 0: #¡Si el tiempo se vuelve negativo la simulación avanza hacia atrás!
                deltatime = 0
        
        if teclas_pulsadas[K_PLUS]: #Aumentar la velocidad de simulación:
            deltatime += 0.001
        
        if not pausa:
            #Actualizamos el tiempo transcurrido:
            iteraciones_transcurridas += 1
            tiempo_transcurrido += deltatime
            
        if len(entorno.campos) == 0:  
            if (iteraciones_transcurridas % 100 == 0):
                print("Energía tras", iteraciones_transcurridas, entorno.Energia())
        
        entorno.MovimientoCamara()
        
        if not pausa:
            entorno.Simular(deltatime, range_kutta)
        
        #Renderizado de la imagen:
        ventana.fill((0, 0, 0)) #Hacemos negra la pantalla.
        

        if entorno.camara != None:
            #Actualizamos la representación gráfica de los campo (si la hay):
            for i, campo in enumerate(entorno.campos):
                unitario = campo.vector_director.Unitario()
                if campo.generador == "rectilineo":
                    posicion_inicial = campo.punto_conductor[0:2]
                    posicion_final = (unitario * ancho).componentes[0:2]
                    posicion_final += posicion_inicial
                    
                    posicion_inicial = (posicion_inicial[0], posicion_inicial[1])
                    posicion_final = (posicion_final[0], posicion_final[1])
                    pygame.draw.line(ventana, campo.color, posicion_inicial, posicion_final, campo.grosor)
                    
                elif campo.generador == "uniforme":
                    if unitario.componentes[2] == 1: #Entrante:
                        for x in range(i*10 + 10, ancho, separacion_campos_uniformes):
                            for y in range(i*10 + 10, alto, separacion_campos_uniformes):
                                
                                posicion = DibujarEntrante(np.array([x, y]), campo.tamaño)
                                for linea in posicion:
                                    pygame.draw.line(ventana, campo.color, linea[0], linea[1], campo.grosor)
                
                    elif unitario.componentes[2] == -1: #Saliente.
                        for x in range(i*10 + 10, ancho, separacion_campos_uniformes):
                            for y in range(i*10 + 10, alto, separacion_campos_uniformes):
                                pygame.draw.circle(ventana, campo.color, (x, y), campo.tamaño, campo.grosor)
                                pygame.draw.circle(ventana, campo.color, (x, y), int(campo.tamaño / 5), campo.grosor)
                    
                    else:
                        for x in range(i * 10 + 10, ancho, separacion_campos_uniformes):
                            for y in range(i * 10 + 10, alto, separacion_campos_uniformes):
                                
                                posicion = np.array([x, y])
                                
                                a = campo.vector_director.componentes[0]
                                b = campo.vector_director.componentes[1]
                                
                                unitario = np.array([a, b]) / (math.sqrt(a**2 + b**2))
                                
                                desplazamiento = (unitario * campo.tamaño) / 2
                                    
                                inicial = posicion - desplazamiento
                                final = posicion + desplazamiento
                                
                                perpendicular = np.array([unitario[1], -unitario[0]])
                                vertice_a = final + perpendicular * campo.tamaño / 3
                                vertice_b = final - perpendicular * campo.tamaño / 3
                                punta = final + unitario * campo.tamaño / 3
                                
                                inicial = (inicial[0], alto - inicial[1])
                                final = (final[0], alto - final[1])
                                vertice_a = (vertice_a[0], alto - vertice_a[1])
                                vertice_b = (vertice_b[0], alto - vertice_b[1])
                                punta = (punta[0], alto - punta[1])
                                
                                pygame.draw.line(ventana, campo.color, inicial, final, campo.grosor)
                                pygame.draw.polygon(ventana, campo.color, (vertice_a, vertice_b, punta), width=campo.grosor)                                   
            
            
            #Actualización de las representaciones gráficas de los cuerpos:
            for i, nombre in enumerate(entorno.cuerpos):
                cuerpo = entorno.cuerpos[nombre]
                posicion = cuerpo.Posicion()
                
                distancia_z = posicion[2] - entorno.camara.posicion[2]

                if distancia_z > 0:
                    variacion = entorno.camara.zoom / distancia_z
                    proyeccion_x = posicion[0] * variacion - entorno.camara.posicion[0]
                    proyeccion_y = posicion[1] * variacion - entorno.camara.posicion[1]
                    imagen = cuerpo.AplicarPerspectiva(variacion)
                    imagen_rect = imagen.get_rect()
                    
                    #Redondeamos sus posiciones:
                    posicion = [round(proyeccion_x), alto/2 - round(proyeccion_y)]
                    
                    imagen_rect.left = posicion[0]
                    imagen_rect.top = posicion[1]
                    
                    if informacion:
                        #Numeración de cuerpos:
                        label = NUMERACION.render(nombre, False, (225, 225, 225))
                        ventana.blit(label, (posicion[0] + cuerpo.radio * variacion, posicion[1] - cuerpo.radio * variacion))
                        
                        #Masas:
                        label = TIPOGRAFIA.render(str("Masa (" + nombre + "): "), False, (225, 225, 225))
                        ventana.blit(label, (10, 30 + i * 20))
                        label = TIPOGRAFIA.render(str(cuerpo.masa), False, (225, 225, 225))
                        ventana.blit(label, (90+8*len(nombre), 30 + 20 * i))

                        #Coordenadas:
                        label = TIPOGRAFIA.render(str("Coordenadas (" + nombre + "): "), False, (225, 225, 225))
                        ventana.blit(label, (120, 10 + i * 20))
                        label = TIPOGRAFIA.render(str(cuerpo.posicion), False, (225, 225, 225))
                        ventana.blit(label, (260+8*len(nombre), 10 + 20 * i))
                        
                        #Velocidades:
                        label = TIPOGRAFIA.render(str("Velocidad (" + nombre + "): "), False, (225, 225, 225))
                        ventana.blit(label, (530+8*len(nombre), 10 + i * 20))
                        label = TIPOGRAFIA.render(str(Modulo(cuerpo.velocidad)), False, (225, 225, 225))
                        ventana.blit(label, (730+8*len(nombre), 10 + 20 * i))
                    
                    
                    if rastros:
                        #Dibujamos su rastro:
                        for punto in cuerpo.rastro.puntos:
                            pygame.draw.circle(ventana, cuerpo.rastro.color, punto, cuerpo.rastro.grosor)
                        
                        #Actualizamos su rastro:
                        cuerpo.rastro.AñadirPosicion((posicion[0] + cuerpo.radio * variacion, posicion[1] + cuerpo.radio * variacion))
                    
                    ventana.blit(imagen, imagen_rect) #Añadimos la imagen a la pantalla.
            
            #Información en pantalla:
            label_tiempo = TIPOGRAFIA.render(str(int(tiempo_transcurrido)), False, (225, 225, 225)) #Muestra el tiempo transcurrido en la simulación.

            ventana.blit(label_tiempo_auxiliar, (10, 10))
            ventana.blit(label_tiempo, (75, 10))
    
        pygame.display.flip()
        pygame.time.wait(16)

class Vector3():
    
    def __init__(self, componentes=np.array([0.0, 0.0, 0.0])):
        self.componentes = componentes
    
    def Unitario(self):
        '''Reduce el vector a un vector unitario. Comprobado y funciona.'''
        modulo = Modulo(self)
        self.componentes = self.componentes / modulo
        return(self)
      
    def __add__(self, a):
        '''Comprobado, funciona.'''
        if type(a) == np.ndarray:
            resultado = Vector3(self.componentes + a)

            return(resultado)
    
    def __mul__(self, a):
        '''Comprobado y funciona.'''
        
        if type(a) != Vector3:
            resultado = Vector3(a * self.componentes)
        else: #Producto vectorial:
            componente_x = self.componentes[1] * a.componentes[2] - self.componentes[2] * a.componentes[1] #Uy*Vz - Uz*Vy
            componente_y = self.componentes[2] * a.componentes[0] - self.componentes[0] * a.componentes[2] #Uz*Vx - Ux*Vz
            componente_z = self.componentes[0] * a.componentes[1] - self.componentes[1] * a.componentes[0] #Ux*Vy - Uy*Vx
            resultado = Vector3() + np.array([componente_x, componente_y, componente_z])
        
        return(resultado)    

    def __truediv__(self, a):
        if type(a) == int or type(a) == float:
            resultado = self * (1 / a)
        return(resultado)

class Campo():
    
    def __init__(self, tipo="electrico", generador="uniforme", intensidad=0.0, vector_director=Vector3(np.array([1.0, 0.0, 0.0])), color=(255, 255, 0),  tamaño=20, grosor=2):
        self.generador = generador
        self.tipo = tipo
        self.intensidad = intensidad
        self.vector_director = vector_director
        self.color = color
        self.tamaño = tamaño
        self.grosor = grosor
            
        if generador == "uniforme":
            self.punto_conductor = None
            
        elif generador == "rectilineo": #Conductores rectilíneos infinitos.
            self.punto_conductor = np.array([0.0, 0.0, 0.0])
    
    def Cargar(self, directorio, reiniciada=False):
        os.chdir(directorio)
        datos = CargarDiccionario("datos.json")
        os.chdir("..")
        
        mensaje_error = "¡Aviso! al campo " + directorio + " le falta"
        
        try:
            self.tipo = datos["Tipo"]
        except:
            if not reiniciada:
                print(mensaje_error, "el tipo.")
        
        try:
            self.generador = datos["Generador"]
        except:
            if not reiniciada:
                print(mensaje_error, "el generador")
        
        try:
            self.intensidad = datos["Intensidad"]
        except:
            if not reiniciada:
                print(mensaje_error, "la intensidad")
        
        try:
            self.vector_director = Vector3(np.array(datos["Vector director"]))
        except:
            if not reiniciada:
                print(mensaje_error, "el vector director.")
        
        if self.generador == "rectilineo":
            try:
                self.punto_conductor = np.array(datos["Punto conductor"])
            except:
                if not reiniciada:
                    print(mensaje_error, "el punto por el que pasa el conductor.")
        try:
            self.color = datos["Color"]
        except:
            if not reiniciada:
                print(mensaje_error, "el color.")
        
        try:
            self.tamaño = datos["Longitud"]
        except:
            if not reiniciada:
                print(mensaje_error, "el tamaño")
        
        try:
            self.grosor = datos["Grosor"]
        except:
            if not reiniciada:
                print(mensaje_error, "el grosor.")
        
    def Guardar(self, directorio):
        os.mkdir(directorio)
        os.chdir(directorio)
        
        vector_director = []
        
        if self.generador == "rectilineo":
            punto_conductor = []
        else:
            punto_conductor = None
            
        for i in range(3):
            vector_director.append(self.vector_director.componentes[i])
            
            if self.generador == "rectilineo":
                punto_conductor.append(self.punto_conductor[i])
        
        datos = {
            "Tipo":self.tipo,
            "Generador":self.generador,
            "Intensidad":self.intensidad,
            "Vector director":vector_director,
            "Punto conductor":punto_conductor,
            "Color":self.color,
            "Tamaño":self.tamaño,
            "Grosor":self.grosor
        }
        
        GuardarDiccionario(datos, "datos")
        os.chdir("..")
        
    def ProyeccionOrtogonal(self, punto):
        #https://www.youtube.com/watch?v=0BccMFU_yro&ab_channel=Mate316
        #Funcion comprobada con geogebra, funciona.
        vector_union = VectorPorPuntos(self.punto_conductor, punto)
        
        producto_escalar = ProductoEscalar(vector_union, self.vector_director)

        proyeccion = self.vector_director * (producto_escalar / Modulo(self.vector_director) ** 2) + self.punto_conductor
        
        return(proyeccion.componentes)
        
    def Magnitud(self, constantes, punto=0):
        
        CONSTANTE_MAGNETICA = constantes["Permitividad magnetica"]
        self.vector_director = self.vector_director.Unitario()
        if self.tipo == "magnetico":
            if self.generador == "uniforme":
                resultado = self.vector_director * self.intensidad
            
            elif self.generador == "rectilineo":
                proyeccion = self.ProyeccionOrtogonal(punto)
                vector_union = VectorPorPuntos(proyeccion, punto)
                
                direccion = self.vector_director * vector_union
                direccion.Unitario()
                distancia = Modulo(vector_union)
                modulo = CONSTANTE_MAGNETICA * (self.intensidad / distancia)

                resultado = direccion * modulo

        elif self.tipo == "electrico":
            resultado = self.vector_director * self.intensidad

        elif self.tipo == "gravitatorio":
            resultado = self.vector_director * self.intensidad
        
        return(resultado)
        
class Cuerpo():
    
    def __init__(self):
        self.nombre = None
        
        self.imagen = None
        self.imagen_rect = None
        
        self.posicion = np.array([0.0, 0.0, 0.0])
        
        self.velocidad = np.array([0.0, 0.0, 0.0])
        
        self.aceleracion = np.array([0.0, 0.0, 0.0])
        
        self.masa = 1
        
        self.carga = 1
        
        self.radio = 1
        
        self.rastro = Rastro()

        self.kutta_v = []
        
    def Guardar(self, directorio, camara=False):
        if not camara:
            if os.path.exists(directorio):
                rmtree(directorio)
            
            os.mkdir(directorio)
            os.chdir(directorio)
        
        posicion = []
        velocidad = []
        aceleracion = []
        for i in range(3):
            posicion.append(self.posicion[i])
            velocidad.append(self.velocidad[i])
            aceleracion.append(self.aceleracion[i])
        
        datos = {
            "Posición":posicion,
            "Velocidad":velocidad,
            "Aceleración":aceleracion,
            "Masa":self.masa,
            "Carga":self.carga
        }
        
        if camara:
            datos["Zoom"] = self.zoom
            datos["Velocidad zoom"] = self.velocidad_zoom
            
        if self.imagen != None:
            pygame.image.save(self.imagen, "imagen.png")
            
        if camara:
            GuardarDiccionario(datos, "Camara")
        else:
            GuardarDiccionario(datos, "datos")
            os.chdir("..")
        
    def Cargar(self, directorio, camara=False, reiniciada=False, ia=False):
        
        datos = {}
        
        if camara:
            mensaje_error = "¡Aviso! A la cámara le falta"
        else:
            mensaje_error = "¡Aviso! Al cuerpo " + directorio + " le falta"
        
        if camara:
            try:
                datos = CargarDiccionario("Camara.json")
            except:
                if not reiniciada:
                    print("¡Aviso!¡No hay ninguna cámara para visualizar la simulación!")
        else:
            os.chdir(directorio)
            
            dir = os.getcwd()

            buscado = "Cuerpos"
            palabra = ""
            for i, char in enumerate(dir):
                if char == buscado[len(palabra)]:
                    palabra += char
                
                if palabra == buscado:
                    break
    
            self.nombre = dir[i+2:-1] + dir[-1]
            
            try:
                datos = CargarDiccionario("datos.json")
            except:
                if not reiniciada:
                    print(mensaje_error, "el archivo datos.json.")
        try:
            self.posicion = np.array(datos["Posición"])
        except:
            if not reiniciada:
                print(mensaje_error, "la posición.")
            if camara:
                self.posicion = np.array([ANCHO / 2, ALTO / 2, -5])
        try:    
            self.velocidad = np.array(datos["Velocidad"])
        except:
            if not reiniciada:
                print(mensaje_error, "la velocidad.")
            
        try:  
            self.aceleracion = np.array(datos["Aceleración"])
        except:
            if not reiniciada:
                print(mensaje_error, "la aceleración.")
        
        try:
            self.masa = datos["Masa"]
        except:
            if not reiniciada:
                print(mensaje_error, "la masa")
        
        try:
            self.carga = datos["Carga"]
        except:
            if not reiniciada:
                print(mensaje_error, "la carga.")
        
        if camara:
            try:
                self.zoom = datos["Zoom"]
            except:
                if not reiniciada:
                    print(mensaje_error, "el zoom.")
                self.zoom = 1
            try:
                self.velocidad_zoom = datos["Velocidad zoom"]
            except:
                if not reiniciada:
                    print(mensaje_error, "la velocidad del zoom.")
                    self.velocidad_zoom = 0.05
        
        if "imagen.png" in os.listdir() and not ia:
            self.imagen = pygame.image.load("imagen.png")
            self.imagen_rect = self.imagen.get_rect()
            
        if not camara:
            os.chdir("..")
            if ia:
                self.radio = 10
            else:
                self.CalcularRadio()

    def Generar(self, parametros):
        for parametro in parametros:
            if parametro == "Velocidad":
                self.velocidad = np.random.random((3)) * 2 - 1
            
            elif parametro == "Posicion":
                self.posicion = np.random.random((3)) * 2 - 1
            
    def ImprimirCaracteristicas(self):
        print("Posición:", self.posicion)
        print("Velocidad:", self.velocidad)
        print("Aceleración:", self.aceleracion)
        print("Masa:", self.masa)
        print("Carga:", self.carga)
        print("Radio:", self.radio)
        
    def Redimensionar(self, size:float):
        ancho = self.imagen.get_width()
        alto = self.imagen.get_height()
        
        nuevo_ancho = int(ancho * size)
        nuevo_alto = int(alto * size)
        
        nueva_imagen = pygame.transform.scale(self.imagen, (nuevo_ancho, nuevo_alto))
        self.imagen = nueva_imagen
        self.imagen_rect = nueva_imagen.get_rect()
        self.CalcularRadio()
    
    def AplicarPerspectiva(self, size:float):
        ancho = self.imagen.get_width()
        alto = self.imagen.get_height()
        
        nuevo_ancho = int(ancho * size)
        nuevo_alto = int(alto * size)
        
        if nuevo_ancho < 10:
            nuevo_ancho = 10
        
        if nuevo_alto < 10:
            nuevo_alto = 10
        
        nueva_imagen = pygame.transform.scale(self.imagen, (nuevo_ancho, nuevo_alto))
        
        return(nueva_imagen)
    
    def Medidas(self):
        ancho = self.imagen.get_width()
        alto = self.imagen.get_height()    

        return ancho, alto
    
    def CalcularRadio(self):
        ancho = self.Medidas()[0]
        self.radio = ancho / 2
      
    def ComprobarColision(self, otro_cuerpo):
        #https://www.youtube.com/watch?v=SH0x5cBvx64&ab_channel=JoseAngel
        distancia = Distancia(self, otro_cuerpo)
        if distancia <= (self.radio + otro_cuerpo.radio): #Si hay colisión:
            vector_union = VectorPorPuntos(self.posicion, otro_cuerpo.posicion)
            vector_union.Unitario()
            
            denominador = self.masa + otro_cuerpo.masa
            
            #Primer cuerpo, cuerpo a (self):
            numerador = self.velocidad * (self.masa - otro_cuerpo.masa) + otro_cuerpo.velocidad * otro_cuerpo.masa * 2
            modulo_a = Modulo(numerador * (1 / denominador))
            
            #Segundo cuerpo:
            numerador = otro_cuerpo.velocidad * (otro_cuerpo.masa - self.masa) + self.velocidad * self.masa * 2
            modulo_b = Modulo(numerador * (1 / denominador))
            
            self.velocidad = (vector_union * (-1) * modulo_a).componentes
            self.velocidad_inicial = (vector_union * (-1) * modulo_a).componentes
            otro_cuerpo.velocidad = (vector_union * modulo_b).componentes
            otro_cuerpo.velocidad_inicial = (vector_union * modulo_b).componentes
            
            #Una vez calculadas las velocidades separamos ambos cuerpos:
            separacion = self.radio + otro_cuerpo.radio - distancia
            
            separacion_a = vector_union * (-1) * separacion / 2
            separacion_b = vector_union * separacion / 2
            
            self.posicion += separacion_a.componentes
            otro_cuerpo.posicion += separacion_b.componentes
                       
    def AplicarFuerza(self, fuerza:Vector3):
        if self.masa != 0:
            aceleracion = fuerza.componentes / self.masa
            self.aceleracion += aceleracion
            
    def CalcularEnergia(self, cuerpos, constantes):
        
        G = constantes["Gravitatoria"]
        K = constantes["Electrica"]
        
        velocidad = Vector3(self.velocidad)
        modulo = Modulo(velocidad)
        energia_cinetica = 0.5 * self.masa * (modulo ** 2)
        
        energia_potencial = 0
        for nombre in cuerpos:
            if nombre == self.nombre:
                pass
            
            else:
                cuerpo = cuerpos[nombre]
                distancia = Distancia(self, cuerpo)
                energia_potencial -= 0.5 * G * (self.masa * cuerpo.masa) / distancia
                energia_potencial += 0.5 * K * (self.carga * cuerpo.carga) / distancia
        
        return(energia_cinetica + energia_potencial)

    def Posicion(self):
        posicion = self.posicion - np.array([self.radio, self.radio, 0])
        return(posicion)
    
class Rastro():
    def __init__(self):
        self.puntos = []
        self.color = (255, 255, 255)
        self.longitud = 1000
        self.grosor = 1
        
    def AñadirPosicion(self, posicion):
        if len(self.puntos) > 0:
            if self.puntos[-1] == posicion:
                pass
            
            else:
                if len(self.puntos) == self.longitud:
                    self.puntos.pop(0)
                self.puntos.append(posicion)
        else:
            self.puntos.append(posicion)

class Entorno():
    def __init__(self, ID=0, cuerpos={}, campos=[], constantes={}, camara=None):
        self.ID = ID
        self.cuerpos = cuerpos
        self.campos = campos
        self.camara = camara
        self.paredes = False
        if constantes == {}:
            self.constantes = {
                "Gravitatoria":0,
                "Electrica":0,
                "Permitividad magnetica":0
            }
        else:
            self.constantes = constantes
    
    def Guardar(self, directorio):
        directorio_inicial = os.getcwd()
        if os.path.exists(directorio):
            rmtree(directorio)
        
        os.mkdir(directorio)
        
        os.chdir(directorio)
        
        GuardarDiccionario(self.constantes, "Constantes")
        GuardarDiccionario(self.configuracion, "Configuracion")
        self.camara.Guardar("camara", True)

        
        os.mkdir("Cuerpos")
        os.chdir("Cuerpos")
        
        for i, nombre in enumerate(self.cuerpos):
            cuerpo = self.cuerpos[nombre]
            cuerpo.Guardar(nombre)
        
        os.chdir("..")
        os.mkdir("Campos")
        os.chdir("Campos")
        
        for i, campo in enumerate(self.campos):
            campo.Guardar(str(i))
        
        os.chdir(directorio_inicial)     
    
    def Cargar(self, directorio, reiniciada=False, ia=False):
        directorio_inicial = os.getcwd()
        os.chdir(directorio)
        
        try:
            configuracion = CargarDiccionario("Configuracion.json")
        except:
            if not reiniciada:
                print("¡Aviso! No hay un archivo de configuración para esta simulación, se utilizará la configuración por defecto.")
            configuracion = CONFIGURACION
            
        self.configuracion = {}
        for key in CONFIGURACION.keys():
            try:
                self.configuracion[key] = configuracion[key]
            except:
                if not reiniciada:
                    print("¡Aviso! A la simulación le falta la/el", key)
                self.configuracion[key] = CONFIGURACION[key]
        
        try:
            constantes = CargarDiccionario("Constantes.json")
            self.constantes = {}
            self.constantes["Gravitatoria"] = constantes["Gravitatoria"]
            self.constantes["Electrica"] = constantes["Electrica"]
            self.constantes["Permitividad magnetica"] = constantes["Permitividad magnetica"]
            
        except:
            if not reiniciada:
                print("¡Aviso!¡Faltan constantes en esta simulación!")
            self.constantes = {"Gravitatoria": 6.67428e-11, "Electrica": 9000000000, "Permitividad magnetica": 1.2566368e-06}

        os.chdir("Cuerpos")
        self.cuerpos = {}
        for archivo in os.listdir():
            cuerpo = Cuerpo()
            cuerpo.Cargar(archivo, reiniciada=reiniciada, ia=ia)
            self.cuerpos[archivo] = cuerpo
        
        os.chdir("..")
        
        os.chdir("Campos")
        self.campos = []
        for archivo in os.listdir():
            campo = Campo()
            campo.Cargar(archivo, reiniciada)
            self.campos.append(campo)
        
        os.chdir("..")
        
        self.camara = Cuerpo()
        self.camara.Cargar("Camara.json", camara=True) 

        os.chdir(directorio_inicial)
        
    def Simular(self, deltatime, range_kutta=1):
        for nombre in self.cuerpos:
            cuerpo = self.cuerpos[nombre]
            
            cuerpo.velocidad_inicial = cuerpo.velocidad
            cuerpo.posicion_inicial_v = cuerpo.posicion
        
        for k in range(range_kutta - 1):
            #Calculamos la aceleración y guardamos la posición y velocidad iniciales:
            self.CalcularAceleracion()
            
            for nombre in self.cuerpos:
                cuerpo = self.cuerpos[nombre]
                cuerpo.velocidad = cuerpo.velocidad_inicial + cuerpo.aceleracion * deltatime #Euler
                cuerpo.kutta_v.append(cuerpo.velocidad)
                
                #Movemos los cuerpos a la mitad del desplazamiento producido por dicha aceleración: (mid point)
                cuerpo.posicion = cuerpo.posicion_inicial + 0.5 * cuerpo.velocidad_inicial * deltatime + 0.25 * cuerpo.aceleracion * (deltatime / 2)**2

        for nombre in self.cuerpos:
            cuerpo = self.cuerpos[nombre]
            cuerpo.velocidad = cuerpo.velocidad_inicial + cuerpo.aceleracion * deltatime
            cuerpo.kutta_v.append(cuerpo.velocidad)
            
            cuerpo.posicion = cuerpo.posicion_inicial_v
            coeficientes = []
            denominador = 0
            for k in range(range_kutta // 2):
                coeficientes.append(2**k)
                denominador += 2**k
            if (range_kutta % 2 == 1):
                coeficientes.append(2**(range_kutta // 2 + 1))
                denominador += 2**(range_kutta // 2 + 1)
            
            for k in range(range_kutta // 2):
                coeficientes.append(2**(range_kutta // 2 - k))
                denominador += 2**(range_kutta // 2 - k)
            
            for k in range(range_kutta):
                cuerpo.posicion += (coeficientes[k] * deltatime * cuerpo.kutta_v[k] / denominador)
            
            cuerpo.kutta_v = []
            self.Colisiones()
    
    def Generar(self, parametros):
        cuerpos = parametros["Cuerpos"]
        for nombre in cuerpos:
            cuerpo = self.cuerpos[nombre]
            cuerpo.Generar(parametros["Cuerpos"][nombre])

    def Colisiones(self):
        for i, nombre in enumerate(self.cuerpos):
            for j, otro_nombre in enumerate(self.cuerpos):
                if j <= i:
                    pass
                
                else:
                    cuerpo = self.cuerpos[nombre]
                    otro_cuerpo = self.cuerpos[otro_nombre]
                    
                    cuerpo.ComprobarColision(otro_cuerpo)
    
    def Energia(self):
        energia = 0
        for nombre in self.cuerpos:
            cuerpo = self.cuerpos[nombre]
            energia += cuerpo.CalcularEnergia(self.cuerpos, self.constantes)
        
        return(energia)
    
    def InteraccionGravitatoria(self):
        
        G = self.constantes["Gravitatoria"]
        
        for i, nombre in enumerate(self.cuerpos):
            cuerpo = self.cuerpos[nombre]
            for j, otro_nombre in enumerate(self.cuerpos):
                if j <= i:
                    pass
                
                else:
                    otro_cuerpo = self.cuerpos[otro_nombre]
                    
                    posicion_a = cuerpo.posicion
                    posicion_b = otro_cuerpo.posicion
                    
                    vector_union = VectorPorPuntos(posicion_a, posicion_b)
                    
                    distancia = Modulo(vector_union)
                    
                    vector_union.Unitario()
                    
                    modulo = G * (cuerpo.masa * otro_cuerpo.masa) / (distancia ** 2)

                    fuerza_gravitatoria = vector_union * modulo
                    
                    cuerpo.AplicarFuerza(fuerza_gravitatoria)
                    otro_cuerpo.AplicarFuerza(fuerza_gravitatoria * (-1)) #3ª Ley de Newton, acción reacción. Mismo módulo y dirección pero sentido opuesto.
    
    def InteraccionElectrica(self):
        
        K = self.constantes["Electrica"]
        
        for i, nombre in enumerate(self.cuerpos):
            cuerpo = self.cuerpos[nombre]
            for j, otro_nombre in enumerate(self.cuerpos):
                if j <= i:
                    pass
                    
                else:
                    otro_cuerpo = self.cuerpos[otro_nombre]
                    posicion_a = cuerpo.posicion
                    posicion_b = otro_cuerpo.posicion
                    
                    vector_union = VectorPorPuntos(posicion_b, posicion_a) #La fuerza eléctrica es repulsiva
                    
                    distancia = Modulo(vector_union)
                    
                    vector_union.Unitario()
                    
                    modulo = K * (cuerpo.carga * otro_cuerpo.carga) / (distancia ** 2)
                    
                    fuerza_electrica = vector_union * modulo
                    
                    cuerpo.AplicarFuerza(fuerza_electrica)
                    otro_cuerpo.AplicarFuerza(fuerza_electrica * (-1)) #3ª Ley de Newton, acción reacción. Mismo módulo y dirección pero sentido opuesto.
                    
    def CalcularAceleracion(self):
        for nombre in self.cuerpos:
                cuerpo = self.cuerpos[nombre]
                cuerpo.aceleracion = np.array([0.0, 0.0, 0.0]) #La aceleración se calcula junto a las fuerzas en cada iteración.
                cuerpo.posicion_inicial = cuerpo.posicion
        self.InteraccionGravitatoria()
        self.InteraccionCamposUniformes()
        self.InteraccionElectrica()
        self.Colisiones()
    
    def InteraccionCamposUniformes(self):
        for nombre in self.cuerpos:
            cuerpo = self.cuerpos[nombre]
            for campo in self.campos:
                if campo.generador == "uniforme":
                    velocidad = Vector3(cuerpo.velocidad)
                
                    valor_del_campo = campo.Magnitud(self.constantes)
                    
                    if campo.tipo == "magnetico":
                        fuerza = (velocidad * valor_del_campo) * cuerpo.carga
                        
                    elif campo.tipo == "electrico":
                        fuerza = valor_del_campo * cuerpo.carga
                    
                    elif campo.tipo == "gravitatorio":
                        fuerza = valor_del_campo * cuerpo.masa
                    
                    cuerpo.AplicarFuerza(fuerza)
                
                elif campo.generador == "rectilineo":
                    velocidad = Vector3(cuerpo.velocidad)
                    valor_del_campo = campo.Magnitud(self.constantes, cuerpo.posicion)
                    
                    fuerza_magnetica = (velocidad * valor_del_campo) * cuerpo.carga
                    
                    cuerpo.AplicarFuerza(fuerza_magnetica)
   
    def MovimientoCamara(self):
        ROZAMIENTO = 1
        DELTATIME = 1 / 25
        #Rozamiento:
        self.camara.velocidad -= ROZAMIENTO * self.camara.velocidad * DELTATIME
        
        self.camara.velocidad += self.camara.aceleracion * DELTATIME
        self.camara.aceleracion = np.array([0.0, 0.0, 0.0])
        self.camara.posicion += self.camara.velocidad * DELTATIME
        
        
        for componente in self.camara.velocidad:
            if componente > 0.99 * ROZAMIENTO or componente < - 0.99 * ROZAMIENTO:
                BorrarRastros(self.cuerpos)
        
def Distancia(A, B):
    if type(A) == np.ndarray and type(B) == np.ndarray:
        distancia = Modulo(B-A)

    elif type(A) == Cuerpo and type(B) == Cuerpo:
        distancia = Modulo(B.posicion - A.posicion)
    
    elif type(A) == Campo and type(B) == Cuerpo:
        if A.generador == "rectilineo":
            vector_union = VectorPorPuntos(A.punto_conductor, B.posicion)
            numerador = Modulo(A.vector_director * vector_union)
            denominador = Modulo(A.vector_director)
            distancia = numerador / denominador
    
    elif type(A) == Campo and type(B) == np.ndarray:
        if A.generador == "rectilineo":
            vector_union = VectorPorPuntos(A.punto_conductor, B)
            numerador = Modulo(A.vector_director * vector_union)
            denominador = Modulo(A.vector_director)
            distancia = numerador / denominador
    
    elif type(B) == Campo and type(A) == Cuerpo:
        if B.generador == "rectilineo":
            vector_union = VectorPorPuntos(B.punto_conductor, A.posicion)
            numerador = Modulo(B.vector_director * vector_union)
            denominador = Modulo(B.vector_director)
            distancia = numerador / denominador
    
    elif type(B) == Campo and type(A) == np.ndarray:
        if B.generador == "rectilineo":
            vector_union = VectorPorPuntos(B.punto_conductor, A)
            numerador = Modulo(B.vector_director * vector_union)
            denominador = Modulo(B.vector_director)
            distancia = numerador / denominador

    return(distancia)
    
def Modulo(A):
    if type(A) == Vector3:
        '''Devuelve el módulo del vector. Comprobado, funciona'''
        x = A.componentes[0]
        y = A.componentes[1]
        z = A.componentes[2]
    
    elif type(A) == np.ndarray:
        x = A[0]
        y = A[1]
        z = A[2]
    
    modulo = (x**2 + y**2 + z**2) ** (0.5)
        
    return(modulo)

def VectorPorPuntos(a:np.array, b:np.array):
    '''Crea un vector dados dos puntos (Desde A hasta B). Comprobado y funciona.'''
    componentes = np.copy(b - a)
    resultado = Vector3() + componentes
    
    return(resultado)

def ProductoEscalar(A, B):
        '''Comprobado y funciona.'''
        resultado = A.componentes[0] * B.componentes[0]
        resultado += A.componentes[1] * B.componentes[1]
        resultado += A.componentes[2] * B.componentes[2]
        
        return(resultado)

def ProductoVectorial(a:Vector3, b:Vector3):
    producto_vectorial = a * b
    return(producto_vectorial)

def Angulo(a:Vector3, b:Vector3):
    '''
        Comprobado. funciona.
        
        Usando la fórmula del producto escalar:
                        (  U  *  V  )
        alfa =  Arcocos (-----------)
                        ( |U| * |V| )
    '''
    alfa = (ProductoEscalar(a, b)) / (Modulo(a) * Modulo(b))
    alfa = math.acos(alfa)
    
    return(alfa)

def DibujarEntrante(posicion:np.ndarray, tamaño):
    
    puntos = np.array([
        [[0, 0], [1, 1]],
        [[1, 0], [0, 1]]
    ])
    
    puntos *= tamaño
    
    puntos += posicion
    
    return(puntos)

def DibujarOblicuo(posicion:np.ndarray, vector_director, tamaño):
    puntos = np.array([])
    
    x = vector_director.componentes[0]
    y = vector_director.componentes[1]
    
    unitario = np.array([x, y])
    unitario = unitario / (math.sqrt(x**2 + y**2))
    
    desplazamiento = (unitario * tamaño) / 2
        
    inicial = posicion - desplazamiento
    
    final = posicion + desplazamiento
    
    puntos = np.append(puntos, [inicial, final])
    
    if x != 0:
        alfa = math.atan(y/x)

        if alfa >= 0:
            if x < 0:
                alfa = alfa + math.pi
        
        else:
            if x <= 0:
                alfa = math.pi - alfa
        
        
    else:
        if y > 0:
            alfa = math.pi / 2

        elif y < 0:
            alfa = 3/2 * math.pi
        
        else:
            alfa = 0

    beta = -1/4 * math.pi - alfa
    
    unitario = np.array([math.cos(beta), math.sin(beta)])
    
    inicial = final + (unitario * tamaño / 3)
    
    puntos = np.append(puntos, [inicial, final])
    
    beta = math.pi - alfa
    
    unitario = np.array([math.cos(beta), math.sin(beta)])
    
    inicial = final + (unitario * tamaño / 3)
    
    puntos = np.append(puntos, [inicial, final])
    
    puntos = np.reshape(puntos, (3, 2, 2))

    return(puntos)

def BorrarRastros(cuerpos):
    for nombre in cuerpos:
        cuerpo = cuerpos[nombre]
        cuerpo.rastro.puntos = []

def GuardarDiccionario(diccionario, destino):
    with open(destino + ".json", "w") as f:
            json.dump(diccionario, f)
    f.close()

def CargarDiccionario(archivo):
    f = open(archivo)
    diccionario = json.load(f)
    f.close()
    
    return(diccionario)

if __name__ == '__main__':
    pass

