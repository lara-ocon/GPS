"""
test_grafo.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Descripción:
Script para verificación básica del funcionamiento de la librería grafo.py.

Las listas "vertices" y "aristas" describen un grafo (dirigido o no dirigido).
El script construye dicho grafo tomando pesos aleatorios en las aristas
usando la librería grafo.py.

Después realiza vairas operaciones básicas sobre el grafo y ejecuta sobre él:
    - Dijkstra
    - Búsqueda de un camino mínimo con Dijkstra
    - Prim
    - Kruskal
"""
import grafo
import random

MIN_PESO_ARISTA=1
MAX_PESO_ARISTA=12

#Listas de vértices y aristas del grafo
dirigido=False
vertices=[1,2,3,4,5,6]
aristas=[(1,2),(1,3),(1,4),(1,5),(2,4),(3,4),(3,5),(5,6)]

#Creación del grafo
G=grafo.Grafo(dirigido)
for v in vertices:
    G.agregar_vertice(v)
for a in aristas:
    G.agregar_arista(a[0],a[1],None,random.randrange(MIN_PESO_ARISTA,MAX_PESO_ARISTA))
    #Imprimimos el contenido de las aristas creadas para ver el peso asignaado
    print(a[0],a[1],":",G.obtener_arista(a[0],a[1]))

#Eliminación de un vértice y una arista
G.eliminar_vertice(6)
# print(G.vertices)                                               # BORRAR ESTA LINEA ===============================
G.eliminar_arista(1,5)
# ==========================================BORRAR=================================================================#
"""
for arista in G.vertices[1]:
    print(arista.origen, arista.destino, arista)
for arista in G.vertices[5]:
    print(arista.origen, arista.destino, arista)

"""    
# ==========================================BORRAR=================================================================#

#Grados de vértices y listas de adyacencia
for v in vertices:
    print(v,":" , G.grado(v),G.grado_entrante(v),G.grado_saliente(v),G.lista_adyacencia(v))

#Dijkstra y camino mínimo
acm=G.dijkstra(1)
print(acm)


camino=G.camino_minimo(1,5)
print(camino)


if(not dirigido):
    #Árbol abarcador mínimo
    aam=G.kruskal()
    print(aam)

    aam2=G.prim()
    print(aam2)






# NUESTRAS PRUEBAS ===================================================================================================#

# prueba dijsktra ej clase: No va, el padre de d es a (a nosotras nos da b)
G3 = grafo.Grafo()

vertices3 = ['A', 'B', 'C', 'D', 'E', 'V']
aristas3 = {('A', 'B'): 5, ('V', 'B'): 9, ('C', 'B'): 2, ('D', 'B'): 1, ('D', 'E'): 1, ('A', 'E'): 8, ('V', 'A'): 3, ('V', 'C'): 7, ('C', 'E'): 5, ('A', 'D'):6}

for vertice in vertices3:
    G3.agregar_vertice(vertice)

for arista in aristas3:
    G3.agregar_arista(arista[0], arista[1], {}, aristas3[arista])

print("\ncamino minimo")
print(G3.camino_minimo('V', 'E'))




# Prueba de prim (ejercicio de clase)
vertices2 = ['A', 'B', 'C', 'D', 'E', 'F']

aristas2 = {('A', 'B'): 5, ('B', 'C'): 3, ('C', 'D'): 4, ('D', 'E'): 2, ('E', 'A'): 3, ('A', 'F'): 5, ('B', 'F'): 5, ('C', 'F'): 6, ('D', 'F'): 3, ('E', 'F'): 4}

G2 = grafo.Grafo()

for vertice in vertices2:
    G2.agregar_vertice(vertice)

for arista in aristas2:
    G2.agregar_arista(arista[0], arista[1], {}, aristas2[arista])

print("\nSOlucion a prim ej 3 hoja 6a")
print(G2.prim())


# prueba de kruskal (ejercicio de clase)
vertices4 = ['A', 'B', 'C', 'D', 'E', 'F']

aristas4 = {('A', 'B'): 5, ('B', 'C'): 3, ('C', 'D'): 4, ('D', 'E'): 2, ('E', 'A'): 3, ('A', 'F'): 5, ('B', 'F'): 5, ('C', 'F'): 6, ('D', 'F'): 3, ('E', 'F'): 4}

G4 = grafo.Grafo()

for vertice in vertices4:
    G4.agregar_vertice(vertice)

for arista in aristas4:
    G4.agregar_arista(arista[0], arista[1], {}, aristas4[arista])

print("\nSolucion kruskal ej 4 hoja 6A")
sol_kruskal = G4.kruskal()

for arista in sol_kruskal:
    print(arista.origen, arista.destino, arista.peso)

G5 = grafo.Grafo()
vertices5 = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

aristas5 = {('A', 'B'): 11, ('B', 'C'): 2, ('A', 'C'): 7, ('C', 'D'): 3, ('C', 'E'): 1, ('A', 'G'): 20, ('E', 'F'): 13, ('C', 'G'): 12, ('D', 'E'): 4, ('D', 'G'): 6, ('F', 'G'): 8}

for vertice in vertices5:
    G5.agregar_vertice(vertice)
for arista in aristas5:
    G5.agregar_arista(arista[0], arista[1], {}, aristas5[arista])

print("\nSOlucion kruskal 2b hoja 6A")
sol_kruskal = G5.kruskal()

for arista in sol_kruskal:
    print(arista.origen, arista.destino, arista.peso)

# pasamos a network x g5
G5_nx = G5.convertir_a_NetworkX()

# imprimimos los nodos
print(G5_nx.nodes())
print(G5_nx.edges())

if ('A','C') in G5_nx.edges():
    print("existe")