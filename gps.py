import grafo as gf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import time, os, sys
import regex as re

# creamos una clase vertice que dado el atributo coordenadas, 
# si tiene las mismas coordenadas considere que es el mismo objeto
# es decir que tenga el mismo hash
class Vertice:
    def __init__(self, coords, num):
        self.calles = {}                    # Diccionario de calles: {calle: numero}
        self.coords = coords
        self.num = num

    def __hash__(self):
        return hash(self.coords)

    def __eq__(self, other):
        # esto lo que hace es que si dos vertices tienen las mismas coordenadas
        # se consideran iguales y por tanto tienen el mismo hash
        try:
            eq = (self.coords == other.coords)
        except:
            eq = False

        return eq

    def __repr__(self):
        return str(self.num)

G = nx.Graph()

grafo1 = gf.Grafo(False)                    # Grafo donde los pesos son las distancias
grafo2 = gf.Grafo(False)                    # Grafo donde los pesos son los tiempos
VELOCIDADES = {
        'AUTOVIA': 100,'AVENIDA': 90,'CARRETERA': 70,'CALLEJON': 30,'CAMINO': 30,
        'ESTACION DE METRO': 20, 'PASADIZO': 20, 'PLAZUELA': 20, 'COLONIA': 20
        }

def velocidad(tipo):
    if tipo in VELOCIDADES.keys():
        return VELOCIDADES[tipo]
    else:
        return 50


def unificar_rotondas_1(rotonda, df):
    # cogemos las coordenadas que componen la rotonda y las unimos en una unica
    # coordenada que será la media
    coords = (df[df['Codigo de vía tratado'] == rotonda]['Coordenada X (Guia Urbana) cm (cruce)'].mean(), df[df['Codigo de vía tratado'] == rotonda]['Coordenada Y (Guia Urbana) cm (cruce)'].mean())
    df.loc[df['Codigo de vía tratado'] == rotonda, 'Coordenada X (Guia Urbana) cm (cruce)'] = coords[0]
    df.loc[df['Codigo de vía tratado'] == rotonda, 'Coordenada Y (Guia Urbana) cm (cruce)'] = coords[1]
    return df, coords

def unificar_rotondas_2(rotonda, df):
    # cogemos las coordenadas que componen la rotonda y las unimos en una unica
    # coordenada que será la media
    df.loc[df['Codigo de via'] == rotonda, 'Coordenada X (Guia Urbana) cm'] = df[df['Codigo de via'] == rotonda]['Coordenada X (Guia Urbana) cm'].mean()
    df.loc[df['Codigo de via'] == rotonda, 'Coordenada Y (Guia Urbana) cm'] = df[df['Codigo de via'] == rotonda]['Coordenada Y (Guia Urbana) cm'].mean()
    return df


def ordenar_csv():  

    """
    ORDENAR CSV:
        - Leer cruces y direcciones y ordenar por numero de via
        - Para cada fila de cruces, su numero será la coordenada mas cercana del de direcciones
    """
    cruces = pd.read_csv('cruces.csv', sep=';', encoding='latin-1')
    direcciones = pd.read_csv('direcciones.csv', sep=';', encoding='latin-1', low_memory=False)
    cruces = cruces.sort_values(by=['Codigo de vía tratado','Codigo de via que cruza o enlaza'] )
    direcciones = direcciones.sort_values(by=['Codigo de via'] )

    
    vertices = {}                           # Diccionario de vertices: {coordenadas: objeto vertice (info)}
    calle_act = 127                         # Calle actual siendo procesada
    tipo_via = list(cruces.itertuples())[0][3]    # Tipo de via de la calle actual
    nombre_calle = list(cruces.itertuples())[0][5]    # Nombre de la calle actual
    dict_vertices = {}
    actualizar = False

    """
    GENERAR GRAFOS:
        - Procesar el fichero por filas procesando cada calle
        - Si las coordenadas de dicha fila no se encuntran en el diccionario
        de vértices, añadimos un nuevo vértice para estas
        - Empleamos el fichero de direcciones para asignar el número de la 
        coordenada más cercana
    """
    num_vertice = 0
    for fila in cruces.itertuples():

        calle = fila[1]
        coords = (fila[11], fila[12])  

        if 'GLORIETA' in fila[3]:
            # unificamos las coordenadas de la rotonda
            cruces, coords = unificar_rotondas_1(calle, cruces)
            direcciones = unificar_rotondas_2(calle, direcciones)
            
    
        if coords not in vertices:
            # agrgamos el vertice
            v = Vertice(coords, num_vertice)
            vertices[coords] = v
            grafo1.agregar_vertice(v)
            grafo2.agregar_vertice(v)
            # añadimos al grafo de networkx el nodo y sus coordenadas
            G.add_nodes_from([(v.num, {'coordenadas': v.coords})])
            num_vertice += 1

        # Asignar nº de coordenada más cercana
        menor_dist_calle = np.inf
        numero_calle = 0
        df_temporal = direcciones.loc[direcciones['Codigo de via'] == calle]

        for fila2 in df_temporal.itertuples():
    
            try:
                dist = np.sqrt((coords[0] - int(fila2[17]))**2 + (coords[1] - int(fila2[18]))**2)
                if dist < menor_dist_calle:
                    menor_dist_calle = dist
                    numero_calle = int(''.join(i for i in fila2[6] if i.isdigit()))
            except:
                pass

            if menor_dist_calle < 1500:
                #print('menor distancia', menor_dist_calle)
                # si esta muy cerca le asigno esos numeros
                break

        # añadimos el numero de calle a la lista de calles del vertice
        vertices[coords].calles[calle] = numero_calle

        """
        ORDENAR POR NÚMERO:
        - Al pasar a la siguiente calle dentro del fichero de cruces,
        se deben ordenar los vértices de la calle por clave
        - Una vez ordenadas, generar las aristas
        """
        # si estamos en el ultimo vertice del csv o cambiamos de calle
        # agregamos las aristas de esa calle
        if (fila[0] == len(cruces) - 1) or (calle_act != calle):
    
            dict_vertices = dict(sorted(dict_vertices.items(), key=lambda item: item[0]))
            v = list(dict_vertices.values())[0] # el anterior, para despues enlazarlos

            # cogemos desde la segunda hasta el final
            for u in list(dict_vertices.values())[1:]:
                # calcular distancia y agregamos la arista al grafo 1
                distancia = np.sqrt((v.coords[0] - u.coords[0])**2 + (v.coords[1] - u.coords[1])**2)
                if distancia < 600000 and v != u:
                    grafo1.agregar_arista(v,u, {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)} ,distancia)
                    grafo1.agregar_arista(u,v, {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)}, distancia)
                    
                    # dividimos la distancia entre la velocidad de la calle y lo multiplicamos por 60 para obtener los minutos
                    # agregamos la arista al grafo 2
                    tiempo = distancia / velocidad(tipo_via) * 60
                    grafo2.agregar_arista(v, u,  {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)}, tiempo)
                    grafo2.agregar_arista(u, v,  {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)}, tiempo)

                    # añadimos la arista al grafo de networkx
                    G.add_edges_from([(v.num, u.num, {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)})])
                    G.add_edges_from([(u.num, v.num, {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)})])
                 
                v = u
        
            tipo_via = fila[3]
            calle_act = calle
            dict_vertices = {}
            dict_vertices[numero_calle] = vertices[coords]
            nombre_calle = fila[2]

        else:
            # en caso contrario segumos añadiendo vertices
            #  a la calle actual
            dict_vertices[numero_calle] = vertices[coords]

    return grafo1, grafo2, G

def pasar_network_x(grafo, nombre):
    G = nx.Graph()
    G.add_nodes_from([(v.num, {'coordenadas': v.coords}) for v in list(grafo.vertices.keys())])
    # en el grafo guardamos en cada vertice todas las aristas que pasan por el, concatenamos todas 
    # estas listas y hacemos un set para eliminar duplicados
    aristas = set([a for v in grafo.vertices.keys() for a in grafo.vertices[v]])
    G.add_edges_from([(a.origen.num, a.destino.num, {'distancia': a.data['distancia'], 'calle': a.data['calle'], 'numero_calle': a.data['num_calle']}) for a in aristas])
    pos = nx.get_node_attributes(G, 'coordenadas')
    plt.figure(figsize=(100,100))
    # ponemos las labels a las aristas (con el numero de la calle)
    nx.draw(G, pos=pos, with_labels=True, font_size=5, node_size=10)
    # vamos a resaltar l
    labels = nx.get_edge_attributes(G,'num_calle')
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=labels, font_size=5)
    # guardamos la figura
    plt.savefig(nombre)


def iniciar():
    # leemos los csv, los ordenamos y creamos el grafo
    print('\nCargando grafos...')
    i = time.time()
    grafo1, grafo2, G = ordenar_csv()
    f = time.time()
    print(f'Grafos cargados correctamente en {f-i} secs\n')
    return grafo1, grafo2, G


def encontrar_coordenadas_cm_grafo(grafo, coordenadas):
    # buscamos las coordenadas mas cercanas de nuestro grafo a las insertadas
    # para ello calculamos la distancia de cada vertice a las coordenadas
    # y nos quedamos con el minimo
    minimo = np.inf
    for v in grafo.vertices.keys():
        distancia = np.sqrt((v.coords[0] - coordenadas[0])**2 + (v.coords[1] - coordenadas[1])**2)
        if distancia < minimo:
            minimo = distancia
            vertice = v
    return vertice



def encontrar_numero_mas_cercano(grafo, calle, numero):
    # buscamos en las aristas de nuestro grafo el nombre de la calle, y nos guardamos
    # el vertice origen/destino con el numero mas cercano
    aristas = [a for v in grafo.vertices.keys() for a in grafo.vertices[v]]
    mas_cercano = None
    dist_mas_cercano = np.inf
    for a in aristas:
        if re.search(calle, a.data['calle'], re.I):
            if a.origen.num == numero:
                return a.origen
            elif a.destino.num == numero:
                return a.destino
            elif abs(a.origen.num - numero) < dist_mas_cercano:
                mas_cercano = a.origen
                dist_mas_cercano = abs(a.origen.num - numero)
            elif abs(a.destino.num - numero) < dist_mas_cercano:
                mas_cercano = a.destino
                dist_mas_cercano = abs(a.destino.num - numero)
    return mas_cercano


def encontrar_coordenadas_direccion_grafo(grafo, direccion):
    # nos meteran el nombre de la via y el numero, separados por una coma, buscamos
    # el vertice que este en esa calle y el numero mas cercano
    calle, numero = direccion.split(',')
    calle = calle.strip().split(' ')
    # si la calle tiene mas de una palabra, significa que es una calle con nombre
    # por lo que nos quedamos con la ultima
    calle = calle[-1]
    numero = int(numero.strip())
    # buscamos el numero mas cercano
    vertice = encontrar_numero_mas_cercano(grafo, calle, numero)
    return vertice


def imprimir_instrucciones_ruta(ruta, grafo):
    instrucciones = []
    i = 1
    actual = ruta[0]
    while i < len(ruta):
        # primero vemos que calle tienen en comun el vertice actual con el siguiente
        # y vamos acumulando la distancia de las aristas que recorremos hasta que los vertices
        # de la ruta dejen de tener en comun dicha calle
        arista = grafo.obtener_arista(actual, ruta[i])[0]
        calle = arista['calle'].strip()
        distancia = float(arista['distancia'])
        i += 1
        if i < len(ruta):
            # vemos cual es la siguiente call
            actual = ruta[i-1]
            arista = grafo.obtener_arista(actual, ruta[i])[0]
            calle2 = arista['calle'].strip()

            # en caso de que la siguiente calle sea la misma que la actual, seguimos acumulando la distancia
            while (i < len(ruta) - 1) and (calle == calle2):
                distancia += float(arista['distancia'])
                calle = calle2
                actual = ruta[i]
                arista = grafo.obtener_arista(actual, ruta[i + 1])[0]
                calle2 = arista['calle'].strip()
                i += 1
        
        if i == len(ruta):
            instrucciones.append(f'Siga recto por {calle} durante {distancia / 100} metros y llegará a su destino')
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
                instrucciones.append(f'Continue por {calle} durante {distancia / 100} metros y gire a la izquierda hacia {calle2}')
            else:
                instrucciones.append(f'Continue por {calle} durante {distancia / 100} metros y gire a la derecha hacia {calle2}')

    return instrucciones


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
    nx.draw(G_ruta, pos, with_labels=False, node_size=20, width=10, node_color='red', edge_color='red')
    
    nombre_archivo = input('Introduce el nombre del archivo donde se guardara el mapa: ')
    plt.savefig(f'{nombre_archivo}.png')
    plt.show()

def Menu(grafo1, grafo2, G):
    # limipamos la pantalla
    print('\n------------      BIENVENIDO AL GPS BROSKI      ----------------\n')
    salir = False
    while not salir:
        print('Introduce el origen y destino para calcular la ruta más corta')
        print('1. Introducir direccion')
        print('2. Introducir coordenadas en cm')
        # print('3. Introducir coordenadas en grados')
        opcion_invalida = True
        while opcion_invalida:
            try:
                opcion = int(input('Opcion: '))
                if opcion in [1,2]:
                    opcion_invalida = False
                else:
                    print('Elige una opcion valida')
            except KeyboardInterrupt:
                print('Saliendo...')
                salir = True
                opcion_invalida = False
            except:
                print('Opcion invalida')
    
        if opcion == 1:
            # nos introduce las coordenadas como el nombre de una calle
            # y el numero de la calle
            origen_valido = False
            while not salir and not origen_valido:
                try:
                    origen = input('Origen: ').strip()
                    if origen == '':
                        salir = True
                    else:
                        origen = encontrar_coordenadas_direccion_grafo(grafo1, origen)
                        if origen == None:
                            print('Direccion no encontrada, vuelve a intentarlo')
                        else:
                            origen_valido = True
                except KeyboardInterrupt:
                    print('Saliendo...')
                    salir = True
                except:
                    print('Direccion no encontrada, vuelve a intentarlo')
            destino_valido = False
            while not salir and not destino_valido:
                try:
                    destino = input('Destino: ').strip()
                    if destino == '':
                        salir = True
                    else:
                        destino = encontrar_coordenadas_direccion_grafo(grafo1, destino)
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
            origen_valido = False
            while not salir and not origen_valido:
                try:
                    origen = input('Origen: ').strip()
                    if origen == '':
                        salir = True
                    else:
                        origen = [float(i) for i in origen.split(',')]
                        if len(origen) != 2:
                            raise ValueError
                        origen = encontrar_coordenadas_cm_grafo(grafo2, origen)
                        origen_valido = True
                except KeyboardInterrupt:
                    print('Saliendo...')
                    salir = True
                except:
                    print('Coordenadas invalidas, vuelve a intentarlo')

            destino_valido = False
            while not salir:
                try:
                    destino = input('Destino: ').strip()
                    if destino == '':
                        salir = True
                    else:
                        destino = [float(i) for i in destino.split(',')]
                        if len(destino) != 2:
                            raise ValueError
                        destino = encontrar_coordenadas_cm_grafo(grafo2, destino)
                        destino_valido = True
                except KeyboardInterrupt:
                    print('Saliendo...')
                    salir = True
                except:
                    print('Coordenadas invalidas, vuelve a intentarlo')
        
        if not salir:
            # calculamos la ruta mas corta, primero preguntamos si prefieren distancia o tiempo
            print('¿Quieres calcular la ruta más corta en distancia o más rápida en tiempo?')
            print('1. Más corta')
            print('2. Más rápida')
            opcion = 0
            while opcion not in [1, 2]:
                try:
                    opcion = int(input('Opcion: '))
                    if opcion not in [1, 2]:
                        raise ValueError
                except ValueError:
                    print('Opcion invalida, intentelo de nuevo')
                except KeyboardInterrupt:
                    salir = True
                    break

            if not salir:
                if opcion == 1:
                    grafo = grafo1
                else:
                    grafo = grafo2

                ruta = grafo.camino_minimo(origen, destino)
                if ruta == None:
                    print('No se puede llegar desde el origen al destino')
                else:
                    print('Las instrucciones son: \n')
                    instrucciones = imprimir_instrucciones_ruta(ruta, grafo)
                    print('1. Mostrar instrucciones por pantalla')
                    print('2. Guardar instrucciones en un archivo')
                    opcion = 0
                    while opcion not in [1, 2]:
                        try:
                            opcion = int(input('Opcion: '))
                            if opcion not in [1, 2]:
                                raise ValueError
                        except ValueError:
                            print('Opcion invalida, intentelo de nuevo')
                        except KeyboardInterrupt:
                            salir = True
                            break
                    
                    if not salir:
                        if opcion == 1:
                            for i in instrucciones:
                                print(i)
                        else:
                            nombre_archivo = input('Introduce el nombre del archivo: ')
                            with open(f'{nombre_archivo}.txt', 'w') as f:
                                for i in instrucciones:
                                    f.write(i + '\n')
                            print('Archivo guardado correctamente')
                    
                    input('\nPulse para ver el map con la ruta')
                    imprimir_mapa_ruta(ruta, G)


                


if __name__ == "__main__":
    grafo1, grafo2, G = iniciar()
    Menu(grafo1, grafo2, G)
