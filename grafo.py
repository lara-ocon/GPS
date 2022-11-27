from typing import List, Tuple, Dict
# import networkx as nx
import sys
import numpy as np

import heapq

INFTY=sys.float_info.max

class Data:

    def __init__(self, velocidad, nombre, distancia):
        self.vel = velocidad
        self.nombre = nombre
        self.distancia = distancia

        # todo esto lo definiremos mas adelante, pero  guardaremos info como la 
        # velocidad maxima de la vía, su nombre, su distancia, igual su tiempo...
        # en el peso guardaremos en función de lo que elija el usuario:
        # camino mas rapido -> peso = self.tiempo = self.distancia * self.velocidad
        # camino con menor distancia -> peso = self.distancia 


class Arista:

    def __init__(self, origen, destino, data, peso):
        self.origen = origen           # esto es el nodo origen (objeto vertice)
        self.destino = destino         # esto es el nodo destino (objeto vertice)
        self.data = data               # data es un objeto que puede ser cualquier cosa
        self.peso = peso


class Vertice:

    def __init__(self, num, coordenadas):
        self.num = num
        self.calles = []               # Las calles pasan por este vertice
        # self.adyacentes = []           # Esto no estoy segura si hay que ponerlo
        self.coordenadas = coordenadas # [x,y]


class Grafo:
    #Diseñar y construirl a clase grafo

    def __init__(self,dirigido=False):
        """ Crea un grafo dirigido o no dirigido.
        
        Args:
            dirigido: Flag que indica si el grafo es dirigido o no.
        Returns: Grafo o grafo dirigido (según lo indicado por el flag)
        inicializado sin vértices ni aristas.
        """
        self.dirigido = dirigido
        self.vertices = {}
        self.aristas = []

    #### Operaciones básicas del TAD ####
    def es_dirigido(self)->bool:
        """ Indica si el grafo es dirigido o no
        
        Args: None
        Returns: True si el grafo es dirigido, False si no.
        """
        return self.dirigido
        
    
    def agregar_vertice(self, v:object) -> None:
        """ Agrega el vértice v al grafo.
        
        Args: v vértice que se quiere agregar
        Returns: None
        """
        self.vertices[(v.coordenadas[0], v.coordenadas[1])] = v


    def agregar_arista(self, s:object, t:object, data:object, weight:float = 1) -> None:
        """ Si los objetos s y t son vértices del grafo, agrega
        una orista al grafo que va desde el vértice s hasta el vértice t
        y le asocia los datos "data" y el peso weight.
        En caso contrario, no hace nada.
        
        Args:
            s: vértice de origen (source)
            t: vértice de destino (target)
            data: datos de la arista
            weight: peso de la arista
        Returns: None
        """
        # recorremos la lista con los numeros asociados a los vertices para comprobar si existen
        # dichos vertices
        if (s.num and t.num in [vertice.num for vertice in list(self.vertices.values())]):
            self.aristas.append(Arista(s, t, data, weight)) # no es dirigido
            if not self.dirigido:
                # añadimos las aristas por duplicado si no es grafo dirigido
                self.aristas.append(Arista(t, s, data, weight))
    
    def eliminar_vertice(self, v:object) -> None:
        """ Si el objeto v es un vértice del grafo lo elimiina.
        Si no, no hace nada.
        
        Args: v vértice que se quiere eliminar
        Returns: None
        """
        # buscamos las coordenadas del vertice, en caso de no existir ducho vertice
        # no haremos nada (como teneos guardados los vertices en un diccionario donde 
        # las claves son las coordenadas, la búsqueda será más rápida)
        if (v.coordenadas[0], v.coordenadas[1]) in self.vertices:
            vertice = self.vertices.pop((v.coordenadas[0], v.coordenadas[1]))
            # eliminamos sus aristas entrantes y salientes
            for a in self.aristas:
                if vertice.num in [a.origen.num, a.destino.num]:
                    self.aristas.pop(a) # eliminamos la arista que pasa por el nodo


    def eliminar_arista(self, s:object, t:object) -> None:
        """ Si los objetos s y t son vértices del grafo y existe
        una arista de u a v la elimina.
        Si no, no hace nada.
        
        Args:
            s: vértice de origen de la arista
            t: vértice de destino de la arista
        Returns: None
        """
        if ((s.coordenadas[0], s.coordenadas[1]) and (t.coordenadas[0],t.coordenadas[1])  in [vertice for vertice in self.vertices]):
            for a in self.aristas:
                if (a.origen.coordenadas == s.coordenadas) and (a.destino.coordenadas == t.coordenadas):
                    self.aristas.remove(a)
                if not self.dirigido:
                    # si no es dirido, las aristas estan duplicadas, eliminamos su duplicada
                    if (a.origen.coordenadas == t.coordenadas) and (a.destino.coordenadas == s.coordenadas):
                        self.aristas.remove(a)
    

    def obtener_arista(self, s:object, t:object) -> Tuple[object, float] or None:
        """ Si los objetos s y t son vértices del grafo y existe
        una arista de u a v, devuelve sus datos y su peso en una tupla.
        Si no, devuelve None
        
        Args:
            s: vértice de origen de la arista
            t: vértice de destino de la arista
        Returns: Una tupla (a,w) con los datos de la arista "a" y su peso
        "w" si la arista existe. None en caso contrario.
        """
        if (s.coordenadas and t.coordenadas in [vertice.coordenadas for vertice in self.vertices.values()]):
            for a in self.aristas:
                if (a.origen.coordenadas == s.coordenadas) and (a.destino.coordenadas == t.coordenadas):
                    return (a.data, a.peso)
                if not self.dirigido:
                    # si no es dirido, las aristas estan duplicadas (devolvemos la primera que encuentre)
                    if (a.origen.coordenadas == t.coordenadas) and (a.destino.coordenadas == s.coordenadas):
                        return (a.data, a.peso)

        return None


    def lista_adyacencia(self, u:object) -> List[object] or None:
        """ Si el objeto u es un vértice del grafo, devuelve
        su lista de adyacencia.
        Si no, devuelve None.
        
        Args: u vértice del grafo
        Returns: Una lista [v1,v2,...,vn] de los vértices del grafo
        adyacentes a u si u es un vértice del grafo y None en caso
        contrario
        """
        print(f"Vamos a hacer lista de adyacencia del nodo {u.num}")
        if (u.coordenadas[0], u.coordenadas[1]) in self.vertices:
            print("EL vertice está")
            lista = []
            for a in self.aristas:
                # Esto lo hace bien tanto para dirigido como para no 
                # dirigido (en el caso de no dirigido, las aristas estan 
                # duplicadas)
                if a.origen.coordenadas == u.coordenadas:
                    print("tenemos arista")
                    lista.append(a.destino)

            return lista
        else:
            return None


    #### Grados de vértices ####
    def grado_saliente(self, v:object)-> int or None:
        """ Si el objeto u es un vértice del grafo, devuelve
        su grado saliente.
        Si no, devuelve None.
        
        Args: u vértice del grafo
        Returns: El grado saliente (int) si el vértice existe y
        None en caso contrario.
        """
        if (v.coordenadas[0], v.coordenadas[1]) in self.vertices:
            grado = 0
            for a in self.aristas:
                if a.origen.coordenadas == v.coordenadas:
                    grado += 1
            return grado
        else:
            return None
    

    def grado_entrante(self, v:object)-> int or None:
        """ Si el objeto u es un vértice del grafo, devuelve
        su grado entrante.
        Si no, devuelve None.
        
        Args: u vértice del grafo
        Returns: El grado entrante (int) si el vértice existe y
        None en caso contrario.
        """
        if (v.coordenadas[0], v.coordenadas[1]) in self.vertices:
            grado = 0
            for a in self.aristas:
                if a.destino.coordenadas == v.coordenadas:
                    grado += 1
            return grado
        else:
            return None


    def grado(self, v:object) -> int or None:
        """ Si el objeto u es un vértice del grafo, devuelve
        su grado si el grafo no es dirigido y su grado saliente si
        es dirigido.
        Si no pertenece al grafo, devuelve None.
        
        Args: u vértice del grafo
        Returns: El grado (int) o grado saliente (int) según corresponda
        si el vértice existe y None en caso contrario.
        """
        if (v.coordenadas[0], v.coordenadas[1]) in self.vertices:
            # esto funciona para dirigido y no dirigido, porque en 
            # no dirigido las aristas estan duplicadas
            return self.grado_saliente(v)
        else:
            return None


    #### Algoritmos ####
    def dijkstra(self,origen:object)-> Dict[object,object]:
        """ Calcula un Árbol Abarcador Mínimo para el grafo partiendo
        del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
        el árbol de la componente conexa que contiene a "origen".
        
        Args: origen vértice del grafo de origen
        Returns: Devuelve un diccionario que indica, para cada vértice alcanzable
        desde "origen", qué vértice es su padre en el árbol abarcador mínimo.
        """
        # inicializamos los diccionarios con la distancia, padre, y estado de cada vertice
        distancia = dict()
        padre = dict()
        visitado = dict()
        # recordamos que self.vertices es un diccionario del tipo {coordenadas:obj(vertice)}
        for v in self.vertices.values():
            distancia[v.num] = np.inf
            padre[v.num] = None
            visitado[v.num] = False
        distancia[origen.num] = 0
        
        # inicialmente Q solo contiene el vertice origen
        Q = [origen]
        while Q:
            # Extraer v de Q de menor d
            d = np.inf
            for nodo in Q:
                if distancia[nodo.num] < d:
                    d = distancia[nodo.num]
                    u = nodo

            if visitado[u.num] == False:
                visitado[u.num] = True
                Q.remove(u)
                for w in self.lista_adyacencia(u): # nodos adyacentes
                    dist_entre = list(self.obtener_arista(u, w))[1] # sacamos su peso
                    if distancia[w.num] > distancia[u.num] + dist_entre: # actualizar el valor de su distancia (distancia asociada a la arista con u y v)
                        distancia[w.num] = distancia[u.num]+ dist_entre
                        padre[w.num] = u
                        Q.append(w)
            else:
                Q.remove(u)
                
        return padre



    def camino_minimo(self, origen:object, destino:object) -> List[object]:
        pass


    def prim(self)-> Dict[object,object]:
        """ Calcula un Árbol Abarcador Mínimo para el grafo
        usando el algoritmo de Prim.
        
        Args: None
        Returns: Devuelve un diccionario que indica, para cada vértice del
        grafo, qué vértice es su padre en el árbol abarcador mínimo.
        """
        Q = []
        coste_minimo = dict()
        padre = dict()
        for v in self.vertices:
            coste_minimo[v] = np.inf
            padre[v] = None
            Q.append(v)
        # como en la primera iteracion sacamos el primero establecemos su coste a 0
        coste_minimo[Q[0]]=0
        while Q:
            # extraer nodo con coste minimo
            cost_min = np.inf
            for nodo,coste in coste_minimo.items():
                if coste < cost_min:
                    cost_min = coste
                    nodo_min = nodo
            # trabajamos sobre el nodo de coste minimo
            Q.pop(nodo_min)
            for w in self.lista_adyacencia(nodo_min):
                if w in Q:
                    dist_entre = list(self.obtener_arista(u, w))[0]['distancia']
                    if dist_entre < coste_minimo[w]:
                        coste_minimo[w] = dist_entre
                        padre[w] = nodo_min
                        # actualizar peso de w a dist_entre en Q
        
        return padre
                    

    def kruskal(self)-> List[Tuple[object,object]]:
        """ Calcula un Árbol Abarcador Mínimo para el grafo
        usando el algoritmo de Prim.
        
        Args: None
        Returns: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
        de los pares de vértices del grafo
        que forman las aristas del arbol abarcador mínimo.
        """
        aristas_aam = [] # aristas del árbol abarcador minimo

        # ordenamos el peso de las aristas: generar diccionario con peso y arista, 
        # ordenar diccionario y convertir en lista que contenga solo las aristas
        pesos_aristas = dict()
        for a in self.aristas:
            id_a = f'({a.origen},{a.destino})'
            pesos_aristas[id_a] = a.peso
        dict_minimo = dict(sorted(pesos_aristas.items(), key=lambda x:x[1]))
        lista_min = dict_minimo.keys()

        C = dict()
        for v in self.vertices:
            C[v.coordenadas] = {v.coordenadas}

        while lista_min:
            arista_min = L[0]
            if C[arista_min.origen.coordenadas] != C[arista_min.destino.coordenadas]:
                aristas_aam.append(arista_min)
                C[arista_min.origen.coordenadas]=C[arista_min.origen.coordenadas]+'-'+C[arista_min.destino.coordenadas]
                for w in C.keys():
                    C[w] = C[arista_min.origen.coordenadas]
   
    
    #### NetworkX ####
    #def convertir_a_NetworkX(self)-> nx.Graph or nx.DiGraph:
        """ Construye un grafo o digrafo de Networkx según corresponda
        a partir de los datos del grafo actual.
        
        Args: None
        Returns: Devuelve un objeto Graph de NetworkX si el grafo es
        no dirigido y un objeto DiGraph si es dirigido. En ambos casos,
        los vértices y las aristas son los contenidos en el grafo dado.
        """
        #pass
    