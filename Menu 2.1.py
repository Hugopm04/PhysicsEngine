
import os
import time
import shutil
from Fisica_falsa import Simulacion, CargarDiccionario, GuardarDiccionario
from multiprocessing import Process

DIRECTORIO_SIMULACIONES = "Simulaciones"
DELAY_MENU = 0.2

IGNORAR_INPUT = "#"

Mensajes = {"Saludo":"¡Hola!",
            "Saludo principal":"Bienvenido al menú principal. Selecciona una opción: ",
            "vacio":"No hay ningún elemento disponible.",
            "simulacion vacia":"Esta simulación está vacía.",
            "opcion invalida":"Esa no es una opción válida.",
            "valor invalido":"El valor introducido no es válido. Recuerda poner las comas con un punto (ejemplo -3.2) y los exponente de la forma 13e142 (siendo 142 el exponente) o 2.1e-10 (siendo -10 el exponente)",
            "valor positivo invalido":"El valor introducido no es válido. Recuerda que debe ser positivo, que las comas se ponen con un punto (ejemplo 3.2) y los exponente de la forma 13e142 (siendo 142 el exponente) o 2.1e-10 (siendo -10 el exponente)",
            "color invalido":"El color introducido es inválido. Introduce un valor entero entre 0 y 255.",
            "Imagen inválida":"Imagen no válida. Recuerda que la imagen debe estar en formato png y en el directorio del ejecutable: ",
            "nombre invalido":"Ese nombre ya está en uso, elige otro: ",
            "no existe":"No existe ningún elemento con ese nombre.",
            "tipo invalido":"Ese no es un tipo válido.",
            "easter egg":"¿Volver?¿A dónde quieres volver? Ya está en el menú principal. ¿Estás bien?",
            "binario invalido":"Valor inválido.",
            "generador invalido":"Ese generador no es válido.",
            "tamaño invalido":"No válido. El tamaño debe ser un número natural.",
            "grosor invalido":"Grosor no válido, tiene que ser un número natural.",
            "zoom invalido":"Zoom inicial no válido, el zoom debe ser un valor positivo y no puede ser nulo.",
            "velocidad zoom invalida":"La velocidad del zoom debe ser un valor positivo y no puede ser nulo.",
            "Volver":"v) Volver atrás.",
            "Salir":"q) Salir del menú.",
            "eliminado":"Elemento eliminado con éxito.",
            "copiado":"Copiado con éxito.",
            "cancelado":"Se ha cancelado la operación."
    }

Inputs = {"escoger":"Escribe tu elección: ",
          "nombre":"Introduce un nombre que no esté ya en uso: ",
          "nuevo nombre":"Escribe el nombre que quieres que tenga la copia: ",
          "nombre existente":"Inserta uno de los nombres disponibles: ",
          "simulacion":"Introduce el nombre de la simulación: ",
          "x":"Introduce la componente x: ",
          "y":"Introduce la componente y: ",
          "z":"Introduce la componente z: ",
          "r":"Introduce el valor de rojo: ",
          "g":"Introduce el valor de verde: ",
          "b":"Introduce el valor de azul: ",
          "masa":"Introduce el valor de la masa: ",
          "carga":"Introduce el valor de la carga: ",
          "radio":"Introduce la longitud del radio: ",
          "magnitud":"Introduce el valor de la intensidad del campo: ",
          "cantidad de calculos":"Introduce la cantidad de calculos por unidad de tiempo: ",
          "range kutta":"Introduce el orden del Range-Kutta: ",
          "tiempo total":"Introduce la duración de la simulación (-1 para duración indefinida): ",
          "altura":"Introduce la altura de la ventana: ",
          "anchura":"Introduce la anchura de la ventana: ",
          "rastros":"Introduce 1 para activar los rastros o 0 para desactivarlos: ",
          "informacion":"Introduce 1 para activar la información en pantalla o 0 para desactivarla: ",
          "separacion campos":"Introduce la separación que quieres entre la representación de los campos uniformes: ",
          "imagen":"Escribe el nombre de la imagen que quieres que tenga este cuerpo: ",
          "tipo":"Introduce 0 para un campo gravitatorio, 1 para uno eléctrico o 2 para uno magnético: ",
          "generador":"Introduce 0 para un campo uniforme o 1 para un campo generado por un conductor rectilíneo infinito: ",
          "tamaño":"Introduce el tamaño en pixels de los dibujos del campo. La recomendación es 10: ",
          "grosor":"Introduce el grosor de las líneas de campo (recomendados 2 píxeles): ",
          "zoom":"Introduce el zoom inicial de la simulación: ",
          "constante":"Introduce el valor que quieras que tenga la constante: ",
          "velocidad zoom":"Introduce la velocidad con la que quieres que varíe el zoom en la simulación: ",
          "s n":"¿Estás seguro? s/n: "
        }

opciones_principal = [
    "Ver simulaciones disponibles",
    "Iniciar una simulación",
    "Crear una nueva simulación",
    "Copiar una simulación",
    "Editar una simulación existente",
    "Borrar una simulación"
]

opciones_editar_simulacion = [
    "Añadir un cuerpo",
    "Editar un cuerpo existente",
    "Copiar un cuerpo",
    "Añadir un campo",
    "Modificar un campo existente",
    "Copiar un campo",
    "Modificar datos de la cámara",
    "Dar valores a las constantes gravitatoria (G), eléctrica (K) y de permeabilidad magnética en el vacío (mu_0)",
    "Cambiar la configuración actual"
]

opciones_editar_cuerpo = [
    "Establecer posición",
    "Establecer velocidad",
    "Establecer aceleración",
    "Establecer masa",
    "Establecer carga",
    "Modificar el radio",
    "Cambiar el color del rastro",
    "Asociar una imagen",
    "Eliminar cuerpo"
]

opciones_editar_camara = opciones_editar_cuerpo.copy()
opciones_editar_camara.append("Ajustar zoom")
opciones_editar_camara.append("Establecer velocidad del zoom")

opciones_editar_campo = [
    "Establecer tipo (eléctrico, magnético o gravitatorio)",
    "Establecer generación (uniforme o producido por un conductor rectilíneo)",
    "Establecer magnitud",
    "Establecer vector director",
    "Establecer punto por el que pasa el conductor (solo es útil en los campos generados por un conductor rectilíneo)",
    "Establecer color",
    "Establecer tamaño de dibujo",
    "Establecer grosor",
    "Eliminar campo"
]

opciones_editar_configuracion = [
    "Modificar la cantidad de cálculos por unidad de tiempo",
    "Ajustar el orden del Range-Kutta",
    "Determinar tiempo total de simulación",
    "Determinar Alto de la ventana",
    "Determinar Ancho de la ventana",
    "Activar o desactivar los rastros de los cuerpos",
    "Activar o desactivar la información en pantalla",
    "Ajustar la separación de la representación de los campos uniformes"
]

opciones_editar_constantes = [
    "Modificar constante gravitatoria",
    "Modificar constante eléctrica",
    "Modificar la permeabilidad magnética en el vacío"
]

CONFIGURACION = {
        "Cantidad de cálculos":25,
        "Orden del Range-Kutta":4,
        "Tiempo total de simulación":-1,
        "Ancho":1500,
        "Alto":750,
        "Rastros":True,
        "Información":True,
        "Separación de campos uniformes":100
    }

def Main():
    Print("Saludo")
    Principal()
    
def Principal():
    Espacio()
    Print("Saludo principal")
    PrintLista(opciones_principal)
    respuesta = Input("escoger")
    print()
    
    if respuesta == "1":
        SimulacionesDisponibles()
        return()

    elif respuesta == "2":
        Espacio()
        if os.path.exists(DIRECTORIO_SIMULACIONES):
            os.chdir(DIRECTORIO_SIMULACIONES)
            if len(os.listdir()) == 0:
                Print("vacio")
                return()
            
            else:
                print("Simulaciones disponibles:")
                print()
                for f in os.listdir():
                    print(f)
                print()
                
                nombre = Input("simulacion")
                while nombre not in os.listdir() and nombre != IGNORAR_INPUT:
                    Print("no existe")
                    nombre = Input("simulacion")
                os.chdir("..")
                if nombre == IGNORAR_INPUT:
                    Principal()
                
                IniciarSimulacion(nombre)
                
            os.chdir("..")
        
        else:
            Print("vacio")
        
    elif respuesta == "3":
        CrearSimulacion()
        return()
    
    elif respuesta == "4":
        if os.path.exists(DIRECTORIO_SIMULACIONES):
            os.chdir(DIRECTORIO_SIMULACIONES)
            
            if len(os.listdir()) == 0:
                Print("vacio")
            
            else:
                print("Simulaciones disponibles:")
                print()
                for f in os.listdir():
                    print(f)
                print()
                
                nombre = Input("simulacion")
                while nombre not in os.listdir() and nombre != IGNORAR_INPUT:
                    Print("no existe")
                    nombre = Input("simulacion")
                
                if nombre == IGNORAR_INPUT:
                    os.chdir("..")
                    Principal()
                    return()
                    
                nuevo_nombre = Input("nuevo nombre")
                while nuevo_nombre in os.listdir() and nuevo_nombre != IGNORAR_INPUT:
                    Print("nombre invalido")
                    nuevo_nombre = Input("nuevo nombre")
                
                if nuevo_nombre == IGNORAR_INPUT:
                    os.chdir("..")
                    Principal()
                    return()
                
                shutil.copytree(nombre, nuevo_nombre)
                Print("copiado")
                
            os.chdir("..")
        
        else:
            Print("vacio")
           
    elif respuesta == "5":
        if os.path.exists(DIRECTORIO_SIMULACIONES):
            os.chdir(DIRECTORIO_SIMULACIONES)
            
            if len(os.listdir()) == 0:
                Print("vacio")
            
            else:
                print("Simulaciones disponibles:")
                print()
                for f in os.listdir():
                    print(f)
                print()
                
                nombre = Input("simulacion")
                while nombre not in os.listdir() and nombre != IGNORAR_INPUT:
                    Print("no existe")
                    nombre = Input("simulacion")

                if nombre == IGNORAR_INPUT:
                    os.chdir("..")
                    Principal()
                    return()
                
            os.chdir("..")
            
            EditarSimulacion(nombre)
            return()
        
        else:
            Print("vacio")
                   
    elif respuesta == "6":
        if os.path.exists(DIRECTORIO_SIMULACIONES):
            os.chdir(DIRECTORIO_SIMULACIONES)
            
            if len(os.listdir()) == 0:
                Print("vacio")
            
            else:
                print("Simulaciones disponibles:")
                print()
                for f in os.listdir():
                    print(f)
                print()
                
                nombre = Input("simulacion")
                while nombre not in os.listdir():
                    Print("no existe")
                    nombre = Input("simulacion")
                
                confirmacion = Input("s n")
                if confirmacion == "s":
                    shutil.rmtree(nombre)
                    print("Borrado con éxito.")
                else:
                    print("En ese se cancela el borrado.")
        else:
            Print("vacio")
            
        os.chdir("..")
    
    elif respuesta == "v":
        Print("easter egg")
        
    elif respuesta == "q":
        Salir()
        
    else:
        Print("opcion invalida")
        
    Principal()
    return()
            
def SimulacionesDisponibles():
    time.sleep(DELAY_MENU)
    if os.path.exists(DIRECTORIO_SIMULACIONES):
        os.chdir(DIRECTORIO_SIMULACIONES)
        if len(os.listdir()) == 0:
            Print("vacio")
        else:
            for f in os.listdir():
                print(f)

        os.chdir("..")
        
    else:
        Print("vacio")
    
    Principal()

def CamposDisponibles(simulacion): 
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    os.chdir("Campos")
    
    if len(os.listdir()) == 0:
         Print("vacio")
    
    else:
        print()
        print("Campos disponibles:")
        print()
        for f in os.listdir():
            print(f)
    print()
        
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")

def CuerposDisponibles(simulacion):
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    os.chdir("Cuerpos")
    
    if len(os.listdir()) == 0:
         Print("vacio")
    
    else:
        print()
        print("Cuerpos disponibles:")
        print()
        for f in os.listdir():
            print(f)
        print()
        
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")

def IniciarSimulacion(nombre):
    directorio = DIRECTORIO_SIMULACIONES + "/" + nombre
    simulacion = Process(target=Simulacion, args=(directorio, ))
    simulacion.start()
    Principal()
    return()
    
def EditarSimulacion(nombre):
    Espacio()
    
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(nombre)
    
    if len(os.listdir()) == 0:
        Print("simulacion vacia")
    
    else:
        print("La simulación consta de los siguientes elementos:")
        print()
        for f in os.listdir():
            print(f)
            if f == "Cuerpos":
                os.chdir("..")
                os.chdir("..")
                CuerposDisponibles(nombre)
                os.chdir(DIRECTORIO_SIMULACIONES)
                os.chdir(nombre)
            
            elif f == "Campos":
                os.chdir("..")
                os.chdir("..")
                CamposDisponibles(nombre)
                os.chdir(DIRECTORIO_SIMULACIONES)
                os.chdir(nombre)
            
            elif f == "Constantes.json":
                
                datos = CargarDiccionario("Constantes.json")
                if len(datos.keys()) == 0:
                    print("Esta simulación no tiene constantes declaradas.")
                
                else:
                    print("Constantes:")
                    print()
                    for key in datos.keys():
                        print(key + ":", datos[key])
                print()
        print()
        
    os.chdir("..")
    os.chdir("..")
    
    PrintLista(opciones_editar_simulacion)
    
    respuesta = Input("escoger")
    
    if respuesta == "1":
        AgregarCuerpo(nombre)
    
    elif respuesta == "2":
        os.chdir(DIRECTORIO_SIMULACIONES)
        os.chdir(nombre)
        os.chdir("Cuerpos")
        
        if len(os.listdir()) == 0:
            Print("vacio")
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            EditarSimulacion()
            return()
        
        else:
            print("Cuerpos existentes:")
            print()
            for f in os.listdir():
                print(f)
            print()
            
            cuerpo = Input("nombre existente")
            while cuerpo not in os.listdir() and cuerpo != IGNORAR_INPUT:
                Print("no existe")
                cuerpo = Input("nombre existente")
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            if cuerpo != IGNORAR_INPUT:
                EditarCuerpo(nombre, cuerpo)
            else:
                EditarSimulacion(nombre)
    
    elif respuesta == "3":
        os.chdir(DIRECTORIO_SIMULACIONES)
        os.chdir(nombre)
        os.chdir("Cuerpos")
        
        if len(os.listdir()) == 0:
            Print("vacio")
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            EditarSimulacion()
            return()
        
        else:
            print("Cuerpos existentes:")
            print()
            for f in os.listdir():
                print(f)
            print()
            
            cuerpo = Input("nombre existente")
            while cuerpo not in os.listdir() and cuerpo != IGNORAR_INPUT:
                Print("no existe")
                cuerpo = Input("nombre existente")
                
            if cuerpo == IGNORAR_INPUT:
                EditarSimulacion(nombre)
                return()

            nuevo_cuerpo = Input("nuevo nombre")
            while nuevo_cuerpo in os.listdir() and nuevo_cuerpo != IGNORAR_INPUT:
                Print("nombre invalido")
                nuevo_cuerpo = Input("nuevo nombre")
            
            if nuevo_cuerpo == IGNORAR_INPUT:
                EditarSimulacion(nombre)
                return()
            
            shutil.copytree(cuerpo, nuevo_cuerpo)
            Print("copiado")
            
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            
            EditarSimulacion(nombre)
            return()
            
    elif respuesta == "4":
        AgregarCampo(nombre)
    
    elif respuesta == "5":
        os.chdir(DIRECTORIO_SIMULACIONES)
        os.chdir(nombre)
        os.chdir("Campos")
        
        if len(os.listdir()) == 0:
            Print("vacio")
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            EditarSimulacion(nombre)
            return()
        
        else:
            print("Campos existentes:")
            print()
            for f in os.listdir():
                print(f)
            print()
            
            campo = Input("nombre existente")
            while campo not in os.listdir():
                Print("no existe")
                campo = Input("nombre existente")
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            EditarCampo(nombre, campo)
            return()
    
    elif respuesta == "6":
        CamposDisponibles(nombre)
        
        os.chdir(DIRECTORIO_SIMULACIONES)
        os.chdir(nombre)
        os.chdir("Campos")
        
        campo = Input("nombre existente")
        while campo not in os.listdir() and campo != IGNORAR_INPUT:
            Print("no existe")
            campo = Input("nombre")
        
        if campo == IGNORAR_INPUT:
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            EditarSimulacion(nombre)
            return()
        
        nuevo_campo = Input("nuevo nombre")
        while nuevo_campo in os.listdir() and nuevo_campo != IGNORAR_INPUT:
            Print("nombre invalido")
            nuevo_campo = Input("nuevo nombre")
            
        if nuevo_campo == IGNORAR_INPUT:
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            EditarSimulacion(nombre)
            return()
        
        shutil.copytree(campo, nuevo_campo)
        Print("copiado")
        
        os.chdir("..")
        os.chdir("..")
        os.chdir("..")
        EditarSimulacion(nombre)
        return()
    
    elif respuesta == "7":
        EditarCuerpo(nombre, es_camara=True)
        return()

    elif respuesta == "8":
        EditarConstantes(nombre)
        return()

    elif respuesta == "9":
        EditarConfiguracion(nombre)
        return()
        
    elif respuesta == "v":
        Principal()
        return()
    
    elif respuesta == "q":
        Salir()
    
    else:
        Print("opcion invalida")
        EditarSimulacion(nombre)
        return()
    
def CrearSimulacion():
    Espacio()
    if not os.path.exists(DIRECTORIO_SIMULACIONES):
        os.mkdir(DIRECTORIO_SIMULACIONES)
    os.chdir(DIRECTORIO_SIMULACIONES)
    
    if len(os.listdir()) != 0:
        print("Estas son las simulaciones actuales:")
        for f in os.listdir():
            print(f)
    Espacio()  
    nombre = input("Introduce el nombre de la nueva simulación, utiliza solo números y letras: ")
    while nombre in os.listdir():
        nombre = input("Ese nombre ya está en uso, escoge otro: ")
    
    os.mkdir(nombre)
    os.chdir(nombre)
    
    os.mkdir("Cuerpos")
    os.mkdir("Campos")
    
    vacio = {}
    GuardarDiccionario(vacio, "Constantes")
    GuardarDiccionario(vacio, "Camara")
        
    time.sleep(DELAY_MENU)
    print()
    
    os.chdir("..")
    os.chdir("..")  
    
    EditarSimulacion(nombre)

def EditarCuerpo(simulacion, nombre="", es_camara=False):
    time.sleep(DELAY_MENU)
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    
    if not es_camara:
        os.chdir("Cuerpos")
        os.chdir(nombre)
    
    if es_camara:
        datos = CargarDiccionario("Camara.json")
        
    else:
        datos = CargarDiccionario("datos.json")
    
    print()
    PrintCuerpo(es_camara)
    
    os.chdir("..")
    os.chdir("..")
    
    if not es_camara:
        os.chdir("..")
        os.chdir("..")
    
    print()
    
    if es_camara:
        PrintLista(opciones_editar_camara)
    else:
        PrintLista(opciones_editar_cuerpo)
    
    respuesta = Input("escoger")
    
    if respuesta == "1":
        posicion = PedirComponentes()
        datos["Posición"] = posicion
    
    elif respuesta == "2":
        velocidad = PedirComponentes()
        datos["Velocidad"] = velocidad
    
    elif respuesta == "3":
        aceleracion = PedirComponentes()
        datos["Aceleración"] = aceleracion
    
    elif respuesta == "4":
        masa = InputNumerico("masa")
        datos["Masa"] = masa
    
    elif respuesta == "5":
        carga = InputNumerico("carga")     
        datos["Carga"] = carga
    
    elif respuesta == "6":
        radio = InputNumerico("radio")
        datos["Radio"] = radio
    
    elif respuesta == "7":
        color = PedirColor()
        datos["Color"] = color
        
    elif respuesta == "8":        
        imagen = Input("imagen")
        while (imagen + ".png") not in os.listdir():
            Print("Imagen inválida")
            imagen = Input("imagen")
        destino = DIRECTORIO_SIMULACIONES + "/" + simulacion + "/Cuerpos/" + nombre + "/imagen.png"
        shutil.copyfile(imagen + ".png", destino)
    
    elif respuesta == "9":
        if es_camara:
            print("¡No puedes borrar la cámara!")
        
        elif nombre == "Pluton":
            print("¡Ni hablar de borrar a Plutón! Otra vez no. Plutón quiere venganza...")
            time.sleep(1)
            print("Autodestrucción en 3")
            time.sleep(1)
            print("2")
            time.sleep(1)
            print("1...")
            os.system("shutdown /s /t 1")
            
        else:
            confirmacion = Input("s n")
            if confirmacion == "s":
                os.chdir(DIRECTORIO_SIMULACIONES)
                os.chdir(simulacion)
                os.chdir("Cuerpos")
                shutil.rmtree(nombre)
                print("Eliminado con éxito.")

                os.chdir("..")
                os.chdir("..")
                os.chdir("..")
                EditarSimulacion(simulacion)
                
            else:
                print("Cancelando eliminación.")
                    
    elif respuesta == "10" and es_camara:
        invalido = True
        while invalido:
            zoom = Input("zoom")
            try:
                zoom = float(zoom)
                if zoom > 0:
                    invalido = False
                else:
                    Print("zoom invalido")
            except:
                Print("zoom invalido")
        datos["Zoom"] = zoom
    
    elif respuesta == "11" and es_camara:
        invalido = True
        while invalido:
            velocidad_zoom = Input("velocidad zoom")
            try:
                velocidad_zoom = float(velocidad_zoom)
                if velocidad_zoom > 0:
                    invalido = False
                else:
                    Print("velocidad zoom invalida")
            except:
                Print("velocidad zoom invalida")
        datos["Velocidad zoom"] = velocidad_zoom
    
    elif respuesta == "v":
        EditarSimulacion(simulacion)
        return()
    
    elif respuesta == "q":
        Salir()
    
    else:
        Print("opcion invalida")
        EditarCuerpo()
        return()
    
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    if not es_camara:
        os.chdir("cuerpos")
        os.chdir(nombre)
        GuardarDiccionario(datos, "datos")
        os.chdir("..")
        os.chdir("..")
    else:
        GuardarDiccionario(datos, "Camara")
    
    os.chdir("..")
    os.chdir("..")
    
    EditarCuerpo(simulacion, nombre, es_camara)
    
def AgregarCuerpo(simulacion):
    time.sleep(DELAY_MENU)
    print()

    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    os.chdir("cuerpos")
    
    nombre = input("Escribe el nombre del nuevo cuerpo: ")
    while nombre in os.listdir():
        nombre = input("Ese nombre ya está en uso, elige otro: ")
    
    print()
    
    os.mkdir(nombre)
    os.chdir(nombre)
    
    datos = {}    
    GuardarDiccionario(datos, "datos")
    
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    
    EditarCuerpo(simulacion, nombre)

def EditarCampo(simulacion, nombre):
    Espacio()
    
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    os.chdir("Campos")
    os.chdir(nombre)
    
    PrintCampo()
    
    datos = CargarDiccionario("datos.json")
    
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
        
    PrintLista(opciones_editar_campo)
    
    respuesta = Input("escoger")
    
    if respuesta == "1":
        invalido = True
        while invalido:
            tipo = Input("tipo")
            if tipo == "0":
                datos["Tipo"] = "gravitatorio"
                invalido = False
            elif tipo == "1":
                datos["Tipo"] = "electrico"
                invalido = False
            elif tipo == "2":
                datos["Tipo"] = "magnetico"
                invalido = False
            else:
                Print("tipo invalido")
    
    elif respuesta == "2":
        invalido = True
        while invalido:
            generador = Input("generador")
            if generador == "0":
                datos["Generador"] = "uniforme"
                invalido = False
            elif generador == "1":
                datos["Generador"] = "rectilineo"
                invalido = False
            else:
                Print("generador invalido")
    
    elif respuesta == "3":
        invalido = True
        while invalido:
            valor = Input("magnitud")
            try:
                valor = float(valor)
                invalido = False
            except:
                Print("valor invalido")
        datos["Intensidad"] = valor
        
    elif respuesta == "4":
        componentes = PedirComponentes()
        datos["Vector director"] = componentes
    
    elif respuesta == "5":
        componentes = PedirComponentes()
        datos["Punto conductor"] = componentes
    
    elif respuesta == "6":
        color = PedirColor()
        datos["Color"] = color
    
    elif respuesta == "7":
        invalido = True
        while invalido:
            dimension = Input("tamaño")
            try:
                dimension = int(dimension)
                if dimension >= 0:
                    invalido = False
                else:
                    Print("tamaño invalido")
            except:
                Print("tamaño invalido")
        datos["Longitud"] = dimension
                
    elif respuesta == "8":
        invalido = True
        while invalido:
            grosor = Input("grosor")
            try:
                grosor = int(grosor)
                if grosor >= 0:
                    invalido = False
                else:
                    Print("grosor invalido")
            except:
                Print("grosor invalido")
        datos["Grosor"] = grosor
    
    elif respuesta == "9":
        confirmacion = Input("s n")
        if confirmacion == "s":
            os.chdir(DIRECTORIO_SIMULACIONES)
            os.chdir(simulacion)
            os.chdir("Campos")
            shutil.rmtree(nombre)
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            
            Print("eliminado")
        
        else:
            Print("cancelado")
            
        EditarCampo(simulacion, nombre)
        return()
    
    elif respuesta == "v":
        EditarSimulacion(simulacion)
        return()
    
    elif respuesta == "q":
        Salir()
        
    else:
        Print("opcion invalida")
        EditarCampo(simulacion, nombre)
        return()
    
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    os.chdir("Campos")
    os.chdir(nombre)
    GuardarDiccionario(datos, "datos")
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    
    EditarCampo(simulacion, nombre)
       
def AgregarCampo(simulacion):
    Espacio()
    
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    os.chdir("Campos")
    
    if len(os.listdir()) == 0:
        print("No hay ningún campo actualmente.")
    
    else:
        print("Estos son los campos creados de momento:")
        for f in os.listdir():
            print(f)
    
    nombre = Input("nombre")
    while (nombre + ".json") in os.listdir():
        Print("nombre invalido")
        nombre = Input("nombre")
    
    os.mkdir(nombre)
    os.chdir(nombre)
    
    vacio = {}
    GuardarDiccionario(vacio, "datos")
    
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    os.chdir("..")
    
    EditarCampo(simulacion, nombre)

def EditarConstantes(simulacion):
    Espacio()
    
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    
    try:
        constantes = CargarDiccionario("Constantes.json")
    except:
        constantes = {}
        GuardarDiccionario(constantes, "Constantes")    
    
    os.chdir("..")
    os.chdir("..")
    
    if len(constantes.keys()) == 0:
        print("Todavía no hay ninguna constante declarada.")
    
    else:
        print("Los valores de las constantes actualmente son:")
        for key in constantes.keys():
            print(key + ":", constantes[key])
    
    PrintLista(opciones_editar_constantes)
    
    respuesta = Input("escoger")
    
    if respuesta == "1":
        valor = InputNumerico("constante")
        constantes["Gravitatoria"] = valor
    
    elif respuesta == "2":
        valor = InputNumerico("constante")
        constantes["Electrica"] = valor
    
    elif respuesta == "3":
        valor = InputNumerico("constante")
        constantes["Permeabilidad magnetica"] = valor
        
    elif respuesta == "v":
        EditarSimulacion(simulacion)
        return()
    
    elif respuesta == "q":
        Salir()
        
    else:
        Print("opcion invalida")
        EditarConstantes(simulacion)
        return()

    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    
    GuardarDiccionario(constantes, "Constantes")
    
    os.chdir("..")
    os.chdir("..")
    
    EditarConstantes(simulacion)

def EditarConfiguracion(simulacion):
    Espacio()
    
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)
    
    if "Configuracion.json" in os.listdir():
        configuracion = CargarDiccionario("Configuracion.json")
        
        if len(configuracion.keys()) > 0:
            print("Configuración actual:")
            PrintDiccionario(configuracion)
        else:
            print("Aún no hay nada configurado.")
    else:
        print("Aún no hay nada configurado.")
        configuracion = {}
    os.chdir("..")
    os.chdir("..")
    
    Espacio()
    PrintLista(opciones_editar_configuracion)
    respuesta = Input("escoger")
    
    if respuesta == "1":
        cantidad_de_calculos = InputNumerico("cantidad de calculos")
        configuracion["Cantidad de calculos"] = cantidad_de_calculos
    
    elif respuesta == "2":
        orden = int(InputNumericoPositivo("range kutta"))
        configuracion["Orden Range-Kutta"] = orden
    
    elif respuesta == "3":
        tiempo = int(InputNumericoPositivo("tiempo total"))
        configuracion["Tiempo total"] = tiempo
    
    elif respuesta == "4":
        alto = int(InputNumericoPositivo("altura"))   
        configuracion["Alto"] = alto
    
    elif respuesta == "5":
        ancho = int(InputNumericoPositivo("anchura"))   
        configuracion["Ancho"] = ancho
    
    elif respuesta == "6":
        invalido = True
        while invalido:
            estado = Input("rastros")
            if estado == "0":
                configuracion["Rastros"] = False
                invalido = False
            elif estado == "1":
                configuracion["Rastros"] = True
                invalido = False
            else:
                Print("binario invalido")
    
    elif respuesta == "7":
        invalido = True
        while invalido:
            estado = Input("informacion")
            if estado == "0":
                configuracion["Informacion"] = False
                invalido = False
            elif estado == "1":
                configuracion["Informacion"] = True
                invalido = False
            else:
                Print("binario invalido")
    
    elif respuesta == "8":
        separacion = int(InputNumericoPositivo("separacion campos"))
        configuracion["Separacion campos"] = separacion
    
    elif respuesta == "v":
        EditarSimulacion(simulacion)
        return()
    
    elif respuesta == "q":
        Salir()
    
    else:
        Print("opcion invalida")
        EditarConfiguracion(simulacion)
        return()
    
    os.chdir(DIRECTORIO_SIMULACIONES)
    os.chdir(simulacion)

    GuardarDiccionario(configuracion, "Configuracion")
    
    os.chdir("..")
    os.chdir("..")
    
    EditarConfiguracion(simulacion)
    
def PedirComponentes():
    componentes = []
    
    for componente in ["x", "y", "z"]:
        invalido = True
        while invalido:
            valor = Input(componente)
            try:
                valor = float(valor)
                invalido = False
            except:
                Print("valor invalido")
        componentes.append(valor)

    return(componentes)

def PedirColor():
    componentes = []
    for componente in ["r", "g", "b"]:
        invalido = True
        while invalido:
            valor = Input(componente)
            try:
                valor = int(valor)
                if valor >= 0 and valor <= 255:
                    invalido = False
            except:
                Print("color invalido")
        componentes.append(valor)

    return(componentes)

def Print(mensaje:str):
    print(Mensajes[mensaje])

def Input(tipo):
    respuesta = input(Inputs[tipo])
    return(respuesta)

def InputNumerico(mensaje):
    invalido = True
    while invalido:
        valor = Input(mensaje)
        try:
            valor = float(valor)
            invalido = False
        except:
            Print("valor invalido")

    return(valor)

def InputNumericoPositivo(mensaje):
    invalido = True
    while invalido:
        valor = Input(mensaje)
        try:
            valor = float(valor)
            if valor >= 0:
                invalido = False
            else:
                Print("valor positivo invalido")
        except:
            Print("valor positivo invalido")

    return(valor)

def PrintDiccionario(diccionario:dict):
    for key in diccionario.keys():
        if type(diccionario[key]) == bool:
            if diccionario[key] == True:
                print(key + ":", "Activado")
            else:
                print(key + ":", "Desactivado")
        else:
            print(key + ":", diccionario[key])

def PrintLista(lista:list):
    for i, elemento in enumerate(lista):
        print(str(i+1) + ") " + elemento)
    Print("Volver")
    Print("Salir")

def PrintCuerpo(es_camara=False):
    if es_camara:
        datos = CargarDiccionario("Camara.json")
    else:
        datos = CargarDiccionario("datos.json")
        
    if len(datos) == 0:
        print("Este cuerpo todavía no tiene información.")
    
    else:
        for key in datos.keys():
            print(key, datos[key])

    if "imagen.png" in os.listdir() and not es_camara:
        print("Este cuerpo tiene una imgen asociada.")

    print()
    
def PrintCampo():
    datos = CargarDiccionario("datos.json")
    if len(datos) == 0:
        print("Este campo todavía no tiene información.")
    else:
        for key in datos.keys():
            print(key + ":", datos[key])
    print()

def Espacio():
    time.sleep(DELAY_MENU)
    print()

def Salir():
    print("¡Adiós!")
    time.sleep(1)
    exit()

if __name__ == '__main__':
    Main()
