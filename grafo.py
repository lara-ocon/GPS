# Librería Grafo - Practica final Matemática Discreta - IMAT
# ICAI, Universidad Pontificia Comillas
# Grupo 2: Lucía Prado Fernandez-Vega y Lara Ocón Madrid


# importamos las librerías que vamos a usar
from typing import List, Tuple, Dict
import networkx as nx
import sys
import numpy as np
import heapq


INFTY=sys.float_info.max


# definimos una clase arista donde guardaremos información sobre las aristas
class Arista:
    def __init__(self, origen, destino, data, peso):
        self.origen = origen           # esto es el nodo origen (objeto vertice)
        self.destino = destino         # esto es el nodo destino (objeto vertice)
        self.data = data               # data es un objeto que puede ser cualquier cosa
        self.peso = peso               # peso es un número real


# constuimos la clase grafo
class Grafo:

    def __init__(self,dirigido=False):
        """ Crea un grafo dirigido o no dirigido.
        
        Args:
            dirigido: Flag que indica si el grafo es dirigido o no.
        Returns: Grafo o grafo dirigido (según lo indicado por el flag)
        inicializado sin vértices ni aristas.
        """
        self.dirigido = dirigido
        self.vertices = {}       # diccionario = {object : [aristas]} donde aristas son objects


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
        self.vertices[v] = [] # inicialmente consideramos que no tiene aristas


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
        # recorremos la lista con los numeros asociados a los vertices para 
        # comprobar si existen dichos vertices, y en caso de que existan, añadimos
        # la arista, además, si no es dirigido, también la añadimos
        if (s and t in self.vertices):
            self.vertices[s].append(Arista(s,t, data, weight))
            if not self.dirigido:
                # añadimos las aristas por duplicado si no es grafo dirigido
                self.vertices[t].append(Arista(t,s, data, weight))
    

    def eliminar_vertice(self, v:object) -> None:
        """ Si el objeto v es un vértice del grafo lo elimiina.
        Si no, no hace nada.
        
        Args: v vértice que se quiere eliminar
        Returns: None
        """
        # buscamos las coordenadas del vertice, en caso de no existir ducho vertice
        # no haremos nada (como teneos guardados los vertices en un diccionario donde 
        # las claves son las coordenadas, la búsqueda será más rápida)
        if v in self.vertices:
            vertice = self.vertices.pop(v)
            # eliminamos sus aristas entrantes y salientes
            # recorremos la lista de aristas de cada vertice
            for vertice in self.vertices:
                for arista in self.vertices[vertice]:
                    if arista.destino == v:
                        self.vertices[vertice].remove(arista)
                

    def eliminar_arista(self, s:object, t:object) -> None:
        """ Si los objetos s y t son vértices del grafo y existe
        una arista de u a v la elimina.
        Si no, no hace nada.
        
        Args:
            s: vértice de origen de la arista
            t: vértice de destino de la arista
        Returns: None
        """
        if (s and t  in self.vertices):
            for arista in self.vertices[s]:     # miramos las aristas de s
                if arista.origen == s and arista.destino == t:
                    self.vertices[s].remove(arista)

            if not self.dirigido:
                # tambien eliminamos las aristas en sentido contrario
                for arista in self.vertices[t]:    # buscamos las aristas de t
                    if arista.origen == t and arista.destino == s:
                        self.vertices[t].remove(arista)
    

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
        if s and t in self.vertices:
            for arista in self.vertices[s]:
                if arista.origen == s and arista.destino == t:
                    return arista.data, arista.peso
            if not self.dirigido:
                # buscamos tambien en el otro sentido por si aún la ha encontrado la arista
                for arista in self.vertices[t]:
                    if arista.origen == t and arista.destino == s:
                        return arista.data, arista.peso
        # si aun no ha encontrado la arista, devolvemos None
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
        # dado que nuestro diccionario de vertices, guarda de por si para cada
        # clave vertice, su lista de adyacencia, solo tenemos que devolver los 
        # destinos de las aristas que salen del vertice
        if u in self.vertices:
            return [a.destino for a in self.vertices[u]]
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
        # dado que nuestro diccionario de vertices, guarda de por si para cada
        # clave vertice, su lista de adyacencia, solo tenemos que devolver la 
        # longitud de dicha lista
        if v in self.vertices:
            return len(self.vertices[v])
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
        # Tenemos que recorrer las aristas de todos los vertices, en busca 
        # de aristas que tengan como destino a v
        if v in self.vertices:
            grado = 0
            for vertice in self.vertices:
                for arista in self.vertices[vertice]:
                    if arista.destino == v:
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
        if v in self.vertices:
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
        for v in self.vertices:
            distancia[v] = np.inf
            padre[v] = None
            visitado[v] = False
        distancia[origen] = 0
        
        # inicialmente Q solo contiene el vertice origen
        Q = [origen]
        while Q:
            # Extraer v de Q de menor d
            d = np.inf

            heap = [(distancia[v],v) for v in Q]
            d, u = heapq.nsmallest(1, heap)[0]

                
            if visitado[u] == False:
                visitado[u] = True
                Q.remove(u)
                for w in self.lista_adyacencia(u): # en lista de adyacencia tenemos los vertices adyacentes a u
                    dist_entre = list(self.obtener_arista(u, w))[1] # sacamos su peso
                    if distancia[w] > distancia[u] + dist_entre: # actualizar el valor de su distancia (distancia asociada a la arista con u y v)
                        distancia[w] = distancia[u]+ dist_entre
                        padre[w] = u
                        if visitado[w] == False:
                            Q.append(w)
            else:
                Q.remove(u)
                
        return padre


    def camino_minimo(self, origen:object, destino:object) -> List[object]:
        distancia = dict()
        padre = dict()
        visitado = dict()
        # recordamos que self.vertices es un diccionario del tipo {coordenadas:obj(vertice)}
        for v in self.vertices:
            distancia[v] = np.inf
            padre[v] = None
            visitado[v] = False
        distancia[origen] = 0
        
        # inicialmente Q solo contiene el vertice origen
        Q = [origen]
        while Q:
            # Extraer u de Q de menor d
            heap = [(distancia[v],v) for v in Q]
            d, u = heapq.nsmallest(1, heap)[0]
                
            if u == destino:
                C = [destino]
                while padre[C[-1]] != None:
                    C.append(padre[C[-1]])
                C.reverse()

                return C

            if visitado[u] == False:
                visitado[u] = True
                Q.remove(u)
                for w in self.lista_adyacencia(u): # en lista de adyacencia tenemos los vertices adyacentes a u
                    dist_entre = list(self.obtener_arista(u, w))[1] # sacamos su peso
                    # actualizar el valor de su distancia (distancia asociada a la arista con u y v)
                    if distancia[w] > distancia[u] + dist_entre: 
                        distancia[w] = distancia[u]+ dist_entre
                        padre[w] = u
                        if visitado[w] == False:
                            Q.append(w)
            else:
                Q.remove(u)
                

    def prim(self) -> Dict[object,object]:
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
        coste_minimo[Q[0]] = 0
        while Q:
            # extraer nodo con coste minimo
            
            # ordenamos costes minimos
            heap = [(value, key) for key,value in coste_minimo.items()]
            cost_min, nodo_min = heapq.nsmallest(1, heap)[0]
     
            # trabajamos sobre el nodo de coste minimo
            Q.remove(nodo_min)
            coste_minimo.pop(nodo_min)
            # recorremos w que esten en la interseccion de Q y la lista de adyacencia de nodo_min
            for w in self.lista_adyacencia(nodo_min):
                if w in Q:
                    dist_entre = list(self.obtener_arista(nodo_min, w))[1]  # obtenemos su peso
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
        C = {}
        aristas_aam = []
        L = [] # lista de aristas ordenadas por peso
        i = 0
        for v in self.vertices:
            for arista in self.vertices[v]:
                if arista not in L:
                    # ponemos i para que a la hora de elegir entre dos 
                    # aristas con el mismo peso, elija la que ha llegado primero
                    L.append((arista.peso, i, arista))
                    i += 1

        # ordenamos con heapq.nsmallest
        L = heapq.nsmallest(len(L), L)
  
        for v in self.vertices:
            # creamos una componente para dicho V
            C[v] = set([v])
        
        while L:
            # extraemos la arista de menor peso
            a = L.pop(0)[2] # sacamos la arista con menor peso
          
            # comprobamos si los vertices de la arista estan en la misma componente
            if C[a.origen] != C[a.destino]:
                # agregamos la arista a aristas_aam
                aristas_aam.append(a)
                # unimos las componentes
                C[a.origen] = C[a.origen].union(C[a.destino])
                C[a.destino] = C[a.origen]

                # hacemos lo mismo para todos los vertices de la componente
                for w in C[a.origen]:
                    C[w] = C[a.origen]

        return aristas_aam
                    
    
    #### NetworkX ####
    def convertir_a_NetworkX(self) -> nx.Graph or nx.DiGraph:
        """ Construye un grafo o digrafo de Networkx según corresponda
        a partir de los datos del grafo actual.
        
        Args: None
        Returns: Devuelve un objeto Graph de NetworkX si el grafo es
        no dirigido y un objeto DiGraph si es dirigido. En ambos casos,
        los vértices y las aristas son los contenidos en el grafo dado.
        """
        print("EL grafo esss: ", self.es_dirigido())
        # creamos un grafo dirigido o no dirigido segun corresponda
        if self.es_dirigido:
            G = nx.DiGraph()
        else:
            G = nx.Graph()

        G.add_nodes_from(list(self.vertices.keys()))
        aristas = []
        for a in list(self.vertices.values()):
  
            # concatenamos todas las listas de aristas para pasarselas a nx
            aristas += a
        
        for arista in aristas:
        
            if not self.es_dirigido():
                if (arista.destino, arista.origen) not in G.edges():
            
                    G.add_edge(arista.origen, arista.destino, weight=arista.peso)

            else:
                G.add_edge(arista.origen, arista.destino, weight=arista.peso)

        return G