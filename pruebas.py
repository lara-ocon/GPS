import grafo as gf
import random
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

grafo = gf.Grafo()

coords = [[0,1], [0,0], [0,-1], [1,-1], [2,-1], [-1,0]]
aristas = {(1,2):5, (2,3):2, (2,4): 1, (4,5):1, (1,5):8, (1,6):3, (2,6):9, (3,6):7, (3,5):5, (4,1):6}

for i in range(len(coords)):
    grafo.agregar_vertice(gf.Vertice(i+1, coords[i]))

for aristaa in aristas.keys():
    for vertice in grafo.vertices.values():
        if vertice.num == aristaa[0]:
            print("Encuentro origen")
            s = vertice
        elif vertice.num == aristaa[1]:
            print("Encuentro destino")
            t = vertice
    grafo.agregar_arista(s,t,{},aristas[aristaa])

G = nx.Graph()

G.add_nodes_from([(v.num, {'coordenadas': v.coordenadas}) for v in list(grafo.vertices.values())])
G.add_edges_from([(a.origen.num, a.destino.num, {'peso':a.peso}) for a in grafo.aristas])

pos = nx.get_node_attributes(G, 'coordenadas')
plt.figure(figsize=(100,100))
nx.draw(G, pos=pos, with_labels=False, node_size=10)
plt.show()
