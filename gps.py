# Practica 3: GPS - librería gps.py - Matematica Discreta
# Autores: Lucía Prado Fernandez-Vega y Lara Ocón Madrid

# Importamos las librerias necesarias
import grafo as gf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import time, os, sys
import regex as re
import warnings

# Inicializamos los grafos que vamos a usar
G = nx.Graph()                              # Grafo de networkx
grafo1 = gf.Grafo(False)                    # Grafo del TAD grafo.py (pesos son distancias)
grafo2 = gf.Grafo(False)                    # Grafo del TAD grafo.py (pesos son tiempos)


# Definimos los colores que vamos a emplear al imprimir por pantalla
class bcolors:
    BOLDGREEN = '\033[1m\033[92m'
    BOLDRED = '\033[1m\033[91m'
    BOLDYELLOW = '\033[1m\033[93m'
    BOLDWHITE = '\033[1m\033[97m'
    BOLDBLUE = '\033[1m\033[94m'
    FONDOBLANCO = '\033[107m'
    CURSIVA = '\033[3m'
    CURSIVA_AZUL = '\033[3m\033[94m'
    CURSIVA_AMARILLO = '\033[3m\033[93m'
    ENDC = '\033[0m'


class Vertice:
    """
    Clase Vertice
    Atibutos:
        - calles: diccionario de calles que salen de este vertice: {calle: numero}
        - coords: coordenadas del vertice (x,y)
        - num: numero del vertice (lo usaremos como identificador del vertice en los grafos)
    """

    def __init__(self, coords, num):
        self.calles = {}                    # Diccionario de calles: {calle: numero}
        self.coords = coords
        self.num = num

    def __hash__(self):
        return hash(self.coords)

    def __eq__(self, other):
        # definimos la igualdad de vertices como la igualdad de sus coordenadas
        try:
            eq = (self.coords == other.coords)
        except:
            eq = False

        return eq

    def __repr__(self):
        return str(self.num)


"""
FASE 1: Funciones para generar los grafos
"""

def velocidad(tipo):
    """
    Funcion que nos devuelve la velocidad maxima permitida en una arista en funcion
    del tipo de vía.
    """
    VELOCIDADES = {
        'AUTOVIA': 100,'AVENIDA': 90,'CARRETERA': 70,'CALLEJON': 30,'CAMINO': 30,
        'ESTACION DE METRO': 20, 'PASADIZO': 20, 'PLAZUELA': 20, 'COLONIA': 20
        }
    if tipo in VELOCIDADES.keys():
        return VELOCIDADES[tipo]
    else:
        return 50


def unificar_rotondas(rotonda, df):
    """
    cogemos las coordenadas que componen la rotonda y las unimos en una unica
    coordenada que será la media de dichas coordenadas en el dataframe de cruces
    """
    coords = (df[df['Codigo de vía tratado'] == rotonda]['Coordenada X (Guia Urbana) cm (cruce)'].mean(), df[df['Codigo de vía tratado'] == rotonda]['Coordenada Y (Guia Urbana) cm (cruce)'].mean())
    df.loc[df['Codigo de vía tratado'] == rotonda, 'Coordenada X (Guia Urbana) cm (cruce)'] = coords[0]
    df.loc[df['Codigo de vía tratado'] == rotonda, 'Coordenada Y (Guia Urbana) cm (cruce)'] = coords[1]

    df.loc[df['Codigo de via que cruza o enlaza'] == rotonda, 'Coordenada X (Guia Urbana) cm (cruce)'] = coords[0]
    df.loc[df['Codigo de via que cruza o enlaza'] == rotonda, 'Coordenada Y (Guia Urbana) cm (cruce)'] = coords[1]

    return df, coords


def generar_grafos():  

    """
    ORDENAR CSV y GENERAR GRAFOS:
        - Leer cruces y direcciones y ordenar por numero de via (es decir numero de calle).
        - Procesamos cada fila de cruces considerandolo como informacion de un vértice.
        - Para cada fila de cruces, su numero de calle nos lo dará la fila con la coordenada mas cercana 
        en el df de direcciones que pertenezca a la misma calle.
    
    """
    cruces = pd.read_csv('cruces.csv', sep=';', encoding='latin-1')
    direcciones = pd.read_csv('direcciones.csv', sep=';', encoding='latin-1', low_memory=False)
    cruces = cruces.sort_values(by=['Codigo de vía tratado','Codigo de via que cruza o enlaza'] )
    direcciones = direcciones.sort_values(by=['Codigo de via'] )

    direcciones = direcciones[direcciones['Coordenada X (Guia Urbana) cm'] != '000000-100']
    direcciones['Numero'] = direcciones['Literal de numeracion'].str.replace('[a-zA-Z. ï¿½]', '')
    direcciones['Numero'] = direcciones['Numero'].astype(int)
    direcciones['Par'] = direcciones['Numero'] % 2 == 0
    direcciones['Par'] = direcciones['Par'].astype(int)


    vertices = {}                                               # Diccionario de vertices: {tuple(x,y): object(Vertice))}
    calle_act = 127                                             # Numero de la calle actual que estamos procesando
    vel = velocidad(list(cruces.itertuples())[0][3])            # Velocidad de la calle actual que estamos procesando
    nombre_calle = list(cruces.itertuples())[0][2]              # Nombre completo de la calle actual que estamos procesando
    nombre_calle_acortado = list(cruces.itertuples())[0][5]     # Nombre de la calle actual acortado
    dict_vertices = {}                                          # Diccionario de todos los vertices en la calle actual que estamos procesando, {numero: object(Vertice)}
    num_vertice = 0                                             # A cada vértice del grafo le asignaremos un numero  

    rotondas_procesadas = []                                    # Lista de rotondas que ya hemos procesado

    for fila in cruces.itertuples():

        calle = fila[1]
        coords = (fila[11], fila[12])

        if 'GLORIETA' in fila[3] or 'PLAZA' in fila[3]:
            if fila[2].strip() not in rotondas_procesadas:
                rotondas_procesadas.append(fila[2].strip())
                # si se trata de una rotonda, unificamos en los df de cruces y direcciones
                # todas las coordenadas de dicha rotonda como una sola coordenada
                cruces, coords = unificar_rotondas(calle, cruces)
            
    
        if coords not in vertices:

            # Si la coordenada no esta en el diccionario de vertices, la añadimos
            # considerandola como un nuevo vertice al grafo
            v = Vertice(coords, num_vertice)

            # la agregamos a todas las estructuras de datos que necesitamos
            # (diccionario de vertices, grafo de networkx, grafo1 y grafo2 del TAD grafo)
            vertices[coords] = v
            grafo1.agregar_vertice(v)
            grafo2.agregar_vertice(v)
            G.add_nodes_from([(v.num, {'coordenadas': v.coords})])

            num_vertice += 1

        # Ahora buscamos por cercania en coordenadas, el numero de calle correspondiente
        # a la coordenada actual en el df de direcciones
        menor_dist_calle = np.inf
        numero_calle = 0
        df_temporal = direcciones.loc[direcciones['Codigo de via'] == calle]

        # nos quedamos solo con pares/impares, del que tengamos mas:
        n_tot = len(df_temporal)
        n_pares = len(df_temporal[df_temporal['Par'] == 0])
        df_temporal = df_temporal[df_temporal['Par'] == 0] if n_pares > (n_tot-n_pares) else df_temporal[df_temporal['Par'] == 1]

        for fila2 in df_temporal.itertuples():
    
            try:
                dist = np.sqrt((coords[0] - int(fila2[17]))**2 + (coords[1] - int(fila2[18]))**2)
                if dist < menor_dist_calle:
                    menor_dist_calle = dist
                    numero_calle = int(''.join(i for i in fila2[6] if i.isdigit()))
            except:
                pass


        # Guardamos dentro del diccionario de calles de cada vertice, que numero de calle es el
        # que le corresponde a esa coordenada en esa calle
        vertices[coords].calles[calle] = numero_calle
        
        """
        GENERACIÓN DE ARISTAS:
        Dado que tenemos ordenados los df por calles, cuando cambie la calle actual, ordenamos todos
        los vertices que hemos recorrido por su numero dentro de la calle y enlazamos cada dos vertices 
        consecutivos con una arista.
        Esto lo haremos cada vez que pasemos a la siguiente calle, o cuando lleguemos al ultimo 
        cruce del df de cruces.
        """
        if (fila[0] == len(cruces) - 1) or (calle_act != calle):
            
            # Ordenamos los vertices de la calle actual por su numero de calle y guardamos el 
            # primer vertice para comenzar a enlazarlos dos a dos
            dict_vertices = dict(sorted(dict_vertices.items(), key=lambda item: item[0]))
            v = list(dict_vertices.values())[0]

            # Comenzamos a enlazar los vertices de la calle actual
            for u in list(dict_vertices.values())[1:]:

                # Calculamos la distancia entre los vertices
                distancia = np.sqrt((v.coords[0] - u.coords[0])**2 + (v.coords[1] - u.coords[1])**2)
                if distancia < 600000 and v != u:
                    grafo1.agregar_arista(v,u, {'distancia': distancia, 
                                                'calle': nombre_calle, 'num_calle':calle_act, 'nombre_acortado': nombre_calle_acortado,
                                                'velocidad': vel} ,distancia)
                    
                    # dividimos la distancia entre la velocidad de la calle y lo multiplicamos por 60 para obtener los minutos
                    # agregamos la arista al grafo 2
                    tiempo = (distancia / vel) * 60
                    grafo2.agregar_arista(v, u,  {'distancia': distancia, 
                                                  'calle': nombre_calle, 'num_calle':calle_act, 'nombre_acortado': nombre_calle_acortado,
                                                  'velocidad': vel}, tiempo)

                    # añadimos la arista al grafo de networkx
                    G.add_edges_from([(v.num, u.num, {'distancia': distancia, 
                                                      'calle': nombre_calle, 'num_calle':calle_act, 'nombre_acortado': nombre_calle_acortado,
                                                      'velocidad': vel})])
                    G.add_edges_from([(u.num, v.num, {'distancia': distancia, 
                                                      'calle': nombre_calle, 'num_calle':calle_act, 'nombre_acortado': nombre_calle_acortado,
                                                      'velocidad': vel})])
                 
                v = u

            # Hemos terminado con la calle anterior, ahora comenzamos con la nueva
            # guardamos toda su informacion actualizando las variables
            vel = velocidad(fila[3].strip())
            calle_act = calle
            dict_vertices = {}
            dict_vertices[numero_calle] = vertices[coords]
            nombre_calle = fila[2]
            nombre_calle_acortado = fila[5]

        else:
            # en caso contrario segumos añadiendo vertices
            #  a la calle actual
            if numero_calle in dict_vertices:
                # vemos si esta lo suficientemente lejos del otro para considerarlo un nuevo vertice
                dist = np.sqrt((vertices[coords].coords[0] - dict_vertices[numero_calle].coords[0])**2 + (vertices[coords].coords[1] - dict_vertices[numero_calle].coords[1])**2)
                if dist > 1000:
                    numero_calle += np.random.randint(1, 100) / 1000
                    
            dict_vertices[numero_calle] = vertices[coords]

    return grafo1, grafo2, G


def iniciar():
    """
    Funcion que lee los csv, los ordena por numero de calle y genera los grafos.
    """
    print(f'\n{bcolors.BOLDWHITE}Cargando grafos...{bcolors.ENDC}')
    i = time.time()
    grafo1, grafo2, G = generar_grafos()
    f = time.time()
    print(f'{bcolors.BOLDGREEN}Grafos cargados correctamente en {f-i} secs.{bcolors.ENDC}\n')
    return grafo1, grafo2, G


"""
FASE 2: Fase de generacion de rutas
"""

def Menu(grafo1, grafo2, G):
    """
    Funcion que muestra el menu principal del programa. Primero muestra la bienvenida y pregunta
    al usuario que inserte la direccion de origen y destino, y devuelve la mejor ruta en base a sus 
    preferencias (tiempo o distancia), hasta que el usuario introduzca un origen/destino vacíos, 
    o presione Ctrl+C para salir.
    """
    
    print(f'\n{bcolors.FONDOBLANCO}                 BIENVENIDO AL GPS BROSKI                  {bcolors.ENDC}\n')

    salir = False
    while not salir:
        print(f'{bcolors.BOLDWHITE}Introduce el origen y destino para calcular la ruta más corta')
        print(f'{bcolors.BOLDWHITE}1.{bcolors.ENDC} Introducir direccion')
        print(f'{bcolors.BOLDWHITE}2.{bcolors.ENDC} Introducir coordenadas en cm')
        
        opcion_invalida = True
        while opcion_invalida:
            try:
                opcion = int(input(f'Opcion: '))
                if opcion in [1,2]:
                    opcion_invalida = False
                else:
                    print(f'{bcolors.BOLDRED}Opción invalida, vuelve a intentarlo...{bcolors.ENDC}')
            except KeyboardInterrupt:
                print(f'{bcolors.BOLDRED}\nHas pulsado Ctrl+C, saliendo...{bcolors.ENDC}')
                salir = True
                opcion_invalida = False
            except:
                print(f'{bcolors.BOLDRED}Opción invalida, vuelve a intentarlo...{bcolors.ENDC}')
    
        if opcion == 1:
            print(f'\n{bcolors.BOLDWHITE}Introduce la direccion separando el nombre de la vía y el número con una coma {bcolors.ENDC}\n(ejemplo: {bcolors.CURSIVA}calle del conde de peñalver, 3) {bcolors.ENDC}')
            
            # 1) Preguntamos por el origen
            origen_valido = False
            while not salir and not origen_valido:
                try:
                    origen_string = input(f'Origen: ').strip()

                    if origen_string == '':
                        salir = True
                    else:
                        origen = encontrar_coordenadas_direccion_grafo(grafo1, origen_string)
                        if origen == None:
                            print(f'{bcolors.BOLDRED}Direccion no encontrada, vuelve a intentarlo{bcolors.ENDC}')
                        else:
                            origen_valido = True
                except KeyboardInterrupt:
                    print(f'{bcolors.BOLDRED}\nHas pulsado Ctrl+C, saliendo...{bcolors.ENDC}')
                    salir = True
                except:
                    print(f'{bcolors.BOLDRED}Direccion no encontrada, vuelve a intentarlo{bcolors.ENDC}')

            # 2) Preguntamos por el destino
            destino_valido = False
            while not salir and not destino_valido:
                try:
                    destino_string = input('Destino: ').strip()
                    
                    if destino_string == '':
                        salir = True
                    else:
                        destino = encontrar_coordenadas_direccion_grafo(grafo1, destino_string)
                        if destino == None:
                            print('Direccion no encontrada, vuelve a intentarlo')
                        else:
                            destino_valido = True
                except KeyboardInterrupt:
                    print('Saliendo...')
                    salir = True
                except:
                    print('Direccion no encontrada, vuelve a intentarlo')

        elif opcion == 2:
            # coordenadas en cm
            # 1) Preguntamos por el origen
            origen_valido = False
            while not salir and not origen_valido:
                try:
                    origen_string = input(f'Origen: ').strip()

                    if origen_string == '':
                        salir = True
                    else:
                        origen = [float(i) for i in origen_string.split(',')]
                        if len(origen) != 2:
                            raise ValueError
                        origen = encontrar_coordenadas_cm_grafo(grafo2, origen)
                        origen_valido = True
                except KeyboardInterrupt:
                    print(f'{bcolors.BOLDRED}\nHas pulsado Ctrl+C, saliendo...{bcolors.ENDC}')
                    salir = True
                except:
                    print(f'{bcolors.BOLDRED}Coordenadas invalidas, vuelve a intentarlo{bcolors.ENDC}')

            # 2) Preguntamos por el destino
            destino_valido = False
            while not salir:
                try:
                    destino_string = input(f'Destino: ').strip()

                    if destino_string == '':
                        salir = True
                    else:
                        destino = [float(i) for i in destino_string.split(',')]
                        if len(destino) != 2:
                            raise ValueError
                        destino = encontrar_coordenadas_cm_grafo(grafo2, destino)
                        destino_valido = True
                except KeyboardInterrupt:
                    print(f'{bcolors.BOLDRED}\nHas pulsado Ctrl+C, saliendo...{bcolors.ENDC}')
                    salir = True
                except:
                    print(f'{bcolors.BOLDRED}Coordenadas invalidas, vuelve a intentarlo{bcolors.ENDC}')
        
        if not salir:
            # calculamos la ruta mas corta, primero preguntamos si prefieren distancia o tiempo
            print(f'\n{bcolors.BOLDWHITE}¿Quieres calcular la ruta más corta en distancia o más rápida en tiempo?{bcolors.ENDC}')
            print(f'{bcolors.BOLDWHITE}1.{bcolors.ENDC} Más corta')
            print(f'{bcolors.BOLDWHITE}2.{bcolors.ENDC} Más rápida')
            opcion = 0
            while opcion not in [1, 2]:
                try:
                    opcion = int(input(f'{bcolors.BOLDWHITE}Opcion: {bcolors.ENDC}'))
                    if opcion not in [1, 2]:
                        raise ValueError
                except ValueError:
                    print(f'{bcolors.BOLDRED}Opcion invalida, vuelve a intentarlo{bcolors.ENDC}')
                except KeyboardInterrupt:
                    salir = True
                    break

            if not salir:
                # Escogemos el grafo que vamos a usar en funcion de las preferencias 
                # del usario (distancia o tiempo)
                if opcion == 1:
                    grafo = grafo1
                else:
                    grafo = grafo2

                # Calculamos la ruta mas corta
                ruta = grafo.camino_minimo(origen, destino)
                if ruta == None:
                    print(f'{bcolors.BOLDRED}\nLo siento, no se ha encontrado una ruta entre  {bcolors.ENDC}{bcolors.CURSIVA}{origen_string} {bcolors.ENDC}{bcolors.BOLDRED} y  {bcolors.ENDC}{bcolors.CURSIVA}{destino_string}{bcolors.ENDC}')
                else:
                    print(f'{bcolors.BOLDGREEN}\nRuta encontrada!\n{bcolors.ENDC}')
                    instrucciones, instrucciones_sin_color, dist_total, tiempo_total = cargar_instrucciones_ruta(ruta, grafo)
                    print(f'{bcolors.BOLDWHITE}1.{bcolors.ENDC} Mostrar instrucciones por pantalla')
                    print(f'{bcolors.BOLDWHITE}2.{bcolors.ENDC} Guardar instrucciones en un archivo\n')
                    opcion = 0
                    while opcion not in [1, 2]:
                        try:
                            opcion = int(input(f'{bcolors.BOLDWHITE}Opcion: {bcolors.ENDC}'))
                            if opcion not in [1, 2]:
                                raise ValueError
                        except ValueError:
                            print(f'{bcolors.BOLDRED}Opcion invalida, vuelve a intentarlo{bcolors.ENDC}')
                        except KeyboardInterrupt:
                            salir = True
                            break
                    
                    if not salir:
                        if opcion == 1:
                            print(f'{bcolors.BOLDWHITE}\nInstrucciones de la ruta entre {bcolors.ENDC}{bcolors.CURSIVA}{origen_string}{bcolors.ENDC}{bcolors.BOLDWHITE} y {bcolors.ENDC}{bcolors.CURSIVA}{destino_string}:{bcolors.ENDC}\n')
                            for i in instrucciones:
                                print(i)
                            print()
                            print(f'{bcolors.BOLDWHITE}\nDistancia total: {dist_total} metros{bcolors.ENDC}')
                            print(f'{bcolors.BOLDWHITE}Tiempo total: {tiempo_total} {bcolors.ENDC}\n')
                        else:
                            nombre_archivo = input(f'{bcolors.BOLDWHITE}¿Con qué nombre deseas el archivo?: {bcolors.ENDC}\n')
                            with open(f'{nombre_archivo}.txt', 'w') as f:
                                f.write(f'Direcciones de la ruta entre {origen_string} y {destino_string}:\n')
                                for i in instrucciones_sin_color:
                                    f.write(i + '\n')
                                f.write('\n')
                                f.write(f'\nDistancia total: {dist_total} metros\n')
                                f.write(f'Tiempo total: {tiempo_total} \n')
                            print(f'{bcolors.BOLDGREEN}\nArchivo guardado con éxito como {nombre_archivo}.txt !{bcolors.ENDC}\n')
                    
                    imprimir_mapa_ruta(ruta, G)


def encontrar_coordenadas_cm_grafo(grafo, coordenadas):
    """
    buscamos las coordenadas mas cercanas de nuestro grafo a las insertadas
    para ello calculamos la distancia de cada vertice a las coordenadas
    y nos quedamos con la minima
    """
    minimo = np.inf
    for v in grafo.vertices.keys():
        distancia = np.sqrt((v.coords[0] - coordenadas[0])**2 + (v.coords[1] - coordenadas[1])**2)
        if distancia < minimo:
            minimo = distancia
            vertice = v
    return vertice


def encontrar_numero_mas_cercano(grafo, calle, numero):
    """
    Buscamos dentro de nuestro grafo el vertice que mas se parezca a la direccion que nos han introducido. 
    Para ello, guardamos las las aristas en una lista para ir recorriendolas una a una y quedarnos con ellas
    cuyo nombre se parezca al nombre de la calle que nos han introducido. Para cada calle que sea
    parecida, nos quedamos con el vertice que tenga el numero mas cercano al que nos han introducido.
    """
    aristas = [a for v in grafo.vertices.keys() for a in grafo.vertices[v]]

    direcciones_posibles = {} 
    # dado que puede haber posibles resultados a la busqueda, vamos a guardar los resultados que mas
    # se acerquen a dicha busqueda, el formato es el siguiente:
    # {nombre_calle_completo: {'numero_mas_cercano': num, 'vertice': vertice}}

    for a in aristas:

        if re.search(a.data['nombre_acortado'].strip(), calle, re.I):

            if a.data['calle'].strip() not in direcciones_posibles.keys():
                direcciones_posibles[a.data['calle'].strip()] = {'numero_mas_cercano': np.inf, 'vertice': None}

            if abs(int(a.origen.calles[a.data['num_calle']]) - numero) < abs(direcciones_posibles[a.data['calle'].strip()]['numero_mas_cercano'] - numero):
                direcciones_posibles[a.data['calle'].strip()] = {'numero_mas_cercano': int(a.origen.calles[a.data['num_calle']]) , 'vertice': a.origen}

            if abs(int(a.destino.calles[a.data['num_calle']]) - numero) < abs(direcciones_posibles[a.data['calle'].strip()]['numero_mas_cercano'] - numero):
                direcciones_posibles[a.data['calle'].strip()] = {'numero_mas_cercano': int(a.destino.calles[a.data['num_calle']]) , 'vertice': a.destino}
    
    opciones_posibles = len(direcciones_posibles.keys())
    if opciones_posibles == 0:
        return None
    print(f'\n{bcolors.BOLDWHITE}¿A cual de las siguientes direcciones te refieres?{bcolors.ENDC}')
    for i, direccion in enumerate(direcciones_posibles.keys()):
        print(f'{bcolors.BOLDWHITE}{i+1}.{bcolors.ENDC} {bcolors.CURSIVA}{direccion}, {direcciones_posibles[direccion]["numero_mas_cercano"]}{bcolors.ENDC}')

    opcion_no_valida = True
    while opcion_no_valida:
        try:
            opcion = int(input(f'{bcolors.BOLDWHITE}Introduce una opcion: {bcolors.ENDC}'))
            if opcion > 0 and opcion <= opciones_posibles:
                opcion_no_valida = False
            else:
                print(f'{bcolors.BOLDRED}Opcion no valida{bcolors.ENDC}')
        except:
            print(f'{bcolors.BOLDRED}Opcion no valida{bcolors.ENDC}')
    
    return direcciones_posibles[list(direcciones_posibles.keys())[opcion-1]]['vertice']


def encontrar_coordenadas_direccion_grafo(grafo, direccion):
    """
    nos introducen el nombre de la via y el numero, separados por una coma, buscamos
    el vertice que este en esa calle y el numero mas cercano
    """
    calle, numero = direccion.split(',')
    calle = calle.strip().lower()
    # eliminamos las tildes
    tildes = {'á':'a', 'é':'e', 'í':'i', 'ó':'o', 'ú':'u'}
    for tile in tildes.keys():
        calle = calle.replace(tile, tildes[tile])
    numero = int(numero.strip())

    vertice = encontrar_numero_mas_cercano(grafo, calle, numero)
    return vertice


def cargar_instrucciones_ruta(ruta, grafo):
    """
    Dada una sucesion de vertices que componen la ruta, imprimimos las intrucciones para
    ir de cada vertice a otro.
    Para ello, vamos recorriendo la ruta y viendo que arista conecta a cada vertice con el
    siguiente e informando al usuario de que calles tiene que seguir. Para no ser redundantes,
    le indicamos cuantos metros tiene que permanecer el usuario en una calle hasta pasar a la 
    siguiente, y en el momento que cambie de calle, le indicamos hacia donde tiene que girar.
    """
    num = 1
    instrucciones = []
    instrucciones_sin_color = []
    i = 1
    actual = ruta[0]
    dist_total = 0
    tiempo_total = 0
    while i < len(ruta):
        # primero vemos que calle tienen en comun el vertice actual con el siguiente
        # y vamos acumulando la distancia de las aristas que recorremos hasta que los vertices
        # de la ruta dejen de tener en comun dicha calle
        arista = grafo.obtener_arista(actual, ruta[i])[0]
        calle = arista['calle'].strip()
        distancia = float(arista['distancia'])
        dist_total += distancia
        tiempo_total += (distancia / 100) / (float(arista['velocidad']) * 1000 / 60)
        i += 1
        if i < len(ruta):
            # vemos cual es la siguiente calle
            actual = ruta[i-1]
            arista = grafo.obtener_arista(actual, ruta[i])[0]
            calle2 = arista['calle'].strip()

            # en caso de que la siguiente calle sea la misma que la actual, seguimos acumulando la distancia
            while (i < len(ruta) - 1) and (calle == calle2):
                distancia += float(arista['distancia'])
                dist_total += float(arista['distancia'])
                tiempo_total += ((float(arista['distancia']) / 100) / (float(arista['velocidad']) * 1000 / 60))
                calle = calle2
                actual = ruta[i]
                arista = grafo.obtener_arista(actual, ruta[i + 1])[0]
                calle2 = arista['calle'].strip()
                i += 1
        
        if i == len(ruta):
            instrucciones.append(f'{bcolors.BOLDWHITE}{num}){bcolors.ENDC}{bcolors.CURSIVA} Siga recto por {bcolors.ENDC}{bcolors.BOLDWHITE}{calle} {bcolors.ENDC}{bcolors.CURSIVA}durante {bcolors.ENDC}{bcolors.BOLDWHITE}{distancia / 100}{bcolors.ENDC}{bcolors.CURSIVA} metros y llegará a su destino{bcolors.ENDC}')
            instrucciones_sin_color.append(f'{num}) Siga recto por {calle} durante {distancia / 100} metros y llegará a su destino')
        else:
            # no hemos llegado al destino pero si a un cambio de calle, vamos a ver los vertices origen y destino de la calle 
            # anterior y de la calle a la que cambiamos para ver la orientacion del giro
            vertice_ant = ruta[i-2]
            vertice_act = ruta[i-1]
            vertice_sig = ruta[i]
            v1 = (vertice_act.coords[0] - vertice_ant.coords[0], vertice_act.coords[1] - vertice_ant.coords[1])
            v2 = (vertice_sig.coords[0] - vertice_act.coords[0], vertice_sig.coords[1] - vertice_act.coords[1])
            # calculamos el angulo entre los dos vectores, queremos que en todo momento nos de un angulo entre 0 y 2pi
            angulo = np.arccos((v1[0] * v2[0] + v1[1] * v2[1]) / (np.sqrt(v1[0] ** 2 + v1[1] ** 2) * np.sqrt(v2[0] ** 2 + v2[1] ** 2)))
            if v1[0] * v2[1] - v1[1] * v2[0] < 0:
                angulo = 2 * np.pi - angulo
            if angulo < np.pi:
                instrucciones.append(f'{bcolors.BOLDWHITE}{num}){bcolors.ENDC}{bcolors.CURSIVA} Continue por {bcolors.ENDC}{bcolors.BOLDWHITE}{calle} {bcolors.CURSIVA}{bcolors.ENDC}durante {bcolors.ENDC}{bcolors.BOLDWHITE}{distancia / 100}{bcolors.ENDC}{bcolors.CURSIVA} metros y gire a la {bcolors.CURSIVA_AMARILLO}izquierda{bcolors.ENDC}{bcolors.CURSIVA} hacia {bcolors.ENDC}{bcolors.ENDC}{bcolors.BOLDWHITE}{calle2}{bcolors.ENDC}')
                instrucciones_sin_color.append(f'{num}) Continue por {calle} durante {distancia / 100} metros y gire a la izquierda hacia {calle2}')
            else:
                instrucciones.append(f'{bcolors.BOLDWHITE}{num}){bcolors.ENDC}{bcolors.CURSIVA} Continue por {bcolors.ENDC}{bcolors.BOLDWHITE}{calle} {bcolors.CURSIVA}{bcolors.ENDC}durante {bcolors.ENDC}{bcolors.BOLDWHITE}{distancia / 100}{bcolors.ENDC}{bcolors.CURSIVA} metros y gire a la {bcolors.CURSIVA_AZUL}derecha{bcolors.ENDC}{bcolors.CURSIVA} hacia {bcolors.ENDC}{bcolors.BOLDWHITE}{calle2}{bcolors.ENDC}')
                instrucciones_sin_color.append(f'{num}) Continue por {calle} durante {distancia / 100} metros y gire a la derecha hacia {calle2}')

        num += 1
    
    tiempo_total = pasar_a_horas(tiempo_total)

    return instrucciones, instrucciones_sin_color, dist_total / 100, tiempo_total


def pasar_a_horas(tiempo):
    # quitamos los decimales (los segundos)
    tiempo = int(tiempo)

    # recibimos tiempo en minutos y lo pasamos a horas y minutos
    horas = tiempo // 60
    minutos = tiempo % 60

    if horas > 0:
        if minutos > 0:
            return f'{horas} horas y {minutos} minutos'
        else:
            return f'{horas} horas'
    else:
        return f'{minutos} minutos'


def imprimir_mapa_ruta(ruta, G):
    pos = nx.get_node_attributes(G, 'coordenadas')
    figure = plt.figure(figsize=(100,100))
    nx.draw(G, pos, with_labels=False, node_size=10)

    # pintamos encima de la figure ya creada con el mapa
    # para ello creamos un nuevo grafo con los nodos de la ruta
    # y pintamos los nodos y las aristas de la ruta

    # creamos el grafo
    G_ruta = nx.Graph()
    # añadimos los nodos
    for i in range(len(ruta)):
        G_ruta.add_node(ruta[i].num, coordenadas=ruta[i].coords)
    # añadimos las aristas
    for i in range(len(ruta)-1):
        G_ruta.add_edge(ruta[i].num, ruta[i+1].num, calle=grafo1.obtener_arista(ruta[i], ruta[i+1])[0]['calle'])
    # pintamos el grafo sobre la figura
    pos = nx.get_node_attributes(G_ruta, 'coordenadas')
    nx.draw(G_ruta, pos, with_labels=False, node_size=20, width=5, node_color='red', edge_color='red')
    
    nombre_archivo = input(f'\n{bcolors.BOLDWHITE}\nIntroduce el nombre del archivo donde se guardara el mapa: {bcolors.ENDC}\n')
    plt.savefig(f'{nombre_archivo}.png')
    print(f'\n{bcolors.BOLDGREEN}Mapa guardado en {nombre_archivo}.png !!!{bcolors.ENDC}\n')
            


if __name__ == "__main__":

    warnings.filterwarnings("ignore")

    grafo1, grafo2, G = iniciar()
    
    Menu(grafo1, grafo2, G)
