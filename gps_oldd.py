import grafo as gf
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.pyplot as plt
import time

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
        return self.coords == other.coords

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

        if actualizar:
            calle_act = fila[1]
            actualizar = False

        calle = fila[1]                    
        coords = (fila[11], fila[12])  
    
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
            for u in list(dict_vertices.values())[1:]:
                # calcular distancia y agregamos la arista al grafo 1
                distancia = np.sqrt((v.coords[0] - u.coords[0])**2 + (v.coords[1] - u.coords[1])**2)
                grafo1.agregar_arista(v,u, {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)} ,distancia)
                grafo1.agregar_arista(u,v, {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)}, distancia)
                
                # dividimos la distancia entre la velocidad de la calle y lo multiplicamos por 60 para obtener los minutos
                # agregamos la arista al grafo 2
                tiempo = distancia / velocidad(tipo_via) * 60
                grafo2.agregar_arista(v, u,  {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)}, tiempo)
                grafo2.agregar_arista(u, v,  {'distancia': distancia, 'calle': nombre_calle, 'num_calle':calle_act, 'velocidad': velocidad(tipo_via)}, tiempo)
                v = u 

            tipo_via = fila[3]
            actualizar = True
            dict_vertices = {}
            dict_vertices[numero_calle] = vertices[coords]
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
    G.add_edges_from([(a.origen.num, a.destino.num, {'distancia': a.data['distancia'], 'calle': a.data['calle']}) for a in aristas])
    pos = nx.get_node_attributes(G, 'coordenadas')
    plt.figure(figsize=(100,100))
    nx.draw(G, pos=pos, with_labels=False, node_size=10)
    # guardamos la figura
    plt.savefig(nombre)


def Menu():

    print('------------      BIENVENIDO AL GPS BROSKI      ----------------')
    origen = input('Origen: ')
    destino = input('Destino: ')
#         Permitir´a al usuario seleccionar dos direcciones (origen y destino) de la base de datos de direcciones (“direcciones.csv”).
# 3) Permitir´a elegir al usuario si desea encontrar la ruta m´as corta o m´as r´apida entre estos puntos.
# 4) Usando el grafo correspondiente en funci´on de lo elegido en el punto (3), se calcular´a el camino m´ınimo desde el
# origen al destino. Para ello, se deber´an usar las funciones programadas en grafo.py.
# 5) La aplicaci´on analizar´a dicho camino y construir´a una lista de instrucciones detalladas que permitan a un autom´ovil
# navegar desde el origen hasta el destino.
# 6) Finalmente, usando NetworkX, se mostrar´a la ruta elegida resaltada sobre el grafo del callejero.
# 7) Tras mostrar la ruta, se volver´a al punto 2 para seleccionar una nueva ruta hasta que se introduzca un origen o
# destino vac´ıos.

# instrucciones:
# distancia (en metros) se debe continuar por cada v´ıa antes de tomar un giro hacia otra calle.
# Al tomar un desv´ıo, cu´al ser´a el nombre de la siguiente calle por la que se deber´a circular.
#  A la hora de girar, si se debe girar a la izquierda o a la derecha. Opcionalmente, si hay un cruce m´ultiple, se precisar´a
# por qu´e salida debe continuarse.
#  El navegador no deber´ıa dar instrucciones redundantes mientras se contin´ue por la misma calle (m´as all´a de continuar
# por dicha calle X metros)

i = time.time()
grafo1, grafo2 = ordenar_csv()
f = time.time()
print(f-i)
pasar_network_x(grafo1, 'grafo1.png')
pasar_network_x(grafo2, 'grafo2.png')
