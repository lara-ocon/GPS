import grafo as gf
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.pyplot as plt
import time

class Vertice:
    def __init__(self, coords):
        self.calles = {} # diccionario de calles, la clave es la calle, y el valor el numero
        self.coords = coords

grafo1 = gf.Grafo(False) # grafo donde los pesos son las distancias
grafo2 = gf.Grafo(False) # grafo donde los pesos son los tiempos

# primero ordenamos los csv

def ordenar_csv():
    # leemos cruces y direcciones y ordenamos por numero de via
    cruces = pd.read_csv('cruces.csv', sep=';', encoding='latin-1')
    direcciones = pd.read_csv('direcciones.csv', sep=';', encoding='latin-1', low_memory=False)

    cruces = cruces.sort_values(by=['Codigo de vía tratado','Codigo de via que cruza o enlaza'] )
    direcciones = direcciones.sort_values(by=['Codigo de via'] )
    # tiempo = 2.5 segundos

    vertices = {} # guardamos un diccionario de vertices, las coordenadas son la clave
    # y despues guardamos el resto de informacion en un objeto vertice

    # para cada fila de cruces, su numero será la coordenada mas cercana del de direcciones
    
    calle = 127
    dict_vertices = {}

    for fila in cruces.itertuples():
        calle1 = fila[1]                    # calle en la que estamos
        # calle2 = fila[6]                    # calle que cruza

        coords = (fila[11], fila[12]) # coordenadas

        if coords not in vertices:
            # si no esta en el diccionario de vertices, lo añadimos
            vertices[coords] = Vertice(coords)

        # buscamos en el de direcciones y le asignamos el numero de la coordenada mas cercana
        menor_dist_calle1 = np.inf
        #menor_dist_calle2 = np.inf
        numero_calle1 = 0
        #numero_calle2 = 0
        df_temporal = direcciones.loc[direcciones['Codigo de via'] == calle1]
        for fila2 in df_temporal.itertuples():
            if fila2[2] == calle1:
                try:
                    dist = np.sqrt((coords[0] - int(fila2[17]))**2 + (coords[1] - int(fila2[18]))**2)
                    if dist < menor_dist_calle1:
                        menor_dist_calle1 = dist
                        numero_calle1 = int(''.join(i for i in fila2[6] if i.isdigit()))
                except:
                    ...
            if menor_dist_calle1 < 1500:
                print('menor distancia', menor_dist_calle1)
                # si esta muy cerca le asigno esos numeros
                break

        vertices[coords].calles[calle1] = numero_calle1

        if calle == calle1:
            dict_vertices[numero_calle1] = vertices[coords]
        else:
            # ordenamos todos los vertices de la calle (pues ya hemos saltado a la siguiente)
            # y creamos todas sus aristas
            # ordenamos por la clave
            dict_vertices = dict(sorted(dict_vertices.items(), key=lambda item: item[0]))
            # creamos las aristas
            for u in dict_vertices.values()[1:]:
                grafo1.agregar_arista(dict_vertices[u.calles[calle]], u, gf.distancia(dict_vertices[u.calles[calle]].coords, u.coords))
                grafo2.agregar_arista(dict_vertices[u.calles[calle]], u, gf.distancia(dict_vertices[u.calles[calle]].coords, u.coords)/gf.velocidad(calle))

        

i = time.time()
ordenar_csv()
f = time.time()
print(f-i)