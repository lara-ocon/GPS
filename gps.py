import grafo as gf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import time, os, sys

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

    return grafo1, grafo2

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
    grafo1, grafo2 = ordenar_csv()
    f = time.time()
    print(f'Grafos cargados correctamente en {f-i} secs\n')
    return grafo1, grafo2


def encontrar_coordenadas_grafo(grafo, coordenadas):
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


def Menu(grafo1, grafo2):
    # limipamos la pantalla
    print('\n------------      BIENVENIDO AL GPS BROSKI      ----------------\n')
    salir = False
    while not salir:
        print('Introduce las coordenadas (en cm) de origen y destino para calcular la ruta más corta')
        coordenadas_incorrectas = True
        # seguiremos preguntando por coordenadas hasta que el usuario decida salir que será cuando
        # no introduzca coordenadas de origen o destino
        while coordenadas_incorrectas:
            try:
                origen = input('Origen: ').strip()
                destino = input('Destino: ').strip()

                if '' in [origen, destino]:
                    # salimo del programa
                    coordenadas_incorrectas = False
                    salir = True
                else:
                    origen = [float(i) for i in origen.split(',')]
                    destino = [float(i) for i in destino.split(',')]

                    if len(origen) != 2 or len(destino) != 2:
                        raise ValueError
                    coordenadas_incorrectas = False
            except ValueError:
                print('Coordenadas invalidas, intentelo de nuevo')
        
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
                if opcion == 1:          # distancia
                    grafo = grafo1
                else:                    # tiempo
                    grafo = grafo2
                
                # buscamos la ruta mas corta aplicando el algoritmo de dijkstra
                origen = encontrar_coordenadas_grafo(grafo, origen)
                destino = encontrar_coordenadas_grafo(grafo, destino)

                ruta = grafo.camino_minimo(origen, destino)
                print('La ruta más corta es: ')
                for i in range(len(ruta)-1):
                    print(f'{i+1}. {ruta[i].data["calle"]}, {ruta[i].data["num_calle"]}')

                


if __name__ == "__main__":
    grafo1, grafo2 = iniciar()
    Menu(grafo1, grafo2)
