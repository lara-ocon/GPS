from typing import List, Tuple, Dict
# import networkx as nx
import sys

import heapq

INFTY=sys.float_info.max

class Data:

    def __init__(self):
        ...
        # todo esto lo definiremos mas adelante, pero  guardaremos info como la vel max...

# ESTO NO LO USAMOSSSSS
class Arista:

    def __init__(self, origen, destino, data, peso):
        self.origen = origen           # esto es el nodo origen
        self.destino = destino         # esto es el nodo destino
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
        # ESTO NO VA PORQUE S Y T SON OBJETOS, NO VÉRTICES
        if s.num and t.num in [vertice.num for vertice in list(self.vertices.values())]:
            self.aristas.append(Arista(s, t, data, weight)) # no es dirigido
            if self.dirigido:
                self.aristas.append(Arista(t, s, data, weight)) # añadimos las aristas por duplicado si no es grafo dirigido

    
    def eliminar_vertice(self, v:object) -> None:
        """ Si el objeto v es un vértice del grafo lo elimiina.
        Si no, no hace nada.
        
        Args: v vértice que se quiere eliminar
        Returns: None
        """
        # ESTO NO VA PORQUE V ES OBJETO, NO VÉRTICE
        if v.coordenadas in [vertice.coordenadas for vertice in self.vertices]:
            self.vertices.remove(v)
        
        # HABRIA QUE ELIMINAR LAS ARISTAS QUE PASAN POR V!!!



    def eliminar_arista(self, s:object, t:object) -> None:
        """ Si los objetos s y t son vértices del grafo y existe
        una arista de u a v la elimina.
        Si no, no hace nada.
        
        Args:
            s: vértice de origen de la arista
            t: vértice de destino de la arista
        Returns: None
        """
        if (s.coordenadas and t.coordenadas in [vertice.coordenadas for vertice in self.vertices]):
            for a in self.aristas:
                if (a.origen.coordenadas == s.coordenadas) and (a.destino.coordenadas == t.coordenadas):
                    self.aristas.remove(a)
                if not self.dirigido:
                    # si no es dirido, las aristas estan duplicadas, eliminamos su duplicada
                    if (a.origen.coordenadas == t.coordenadas) and (a.destino.coordenadas == s.coordenadas):
                        self.aristas.remove(a)
        
        # HABRIA QUE ELIMINAR LOS VERTICES SI SE QUEDAN SIN ARISTAS???
    

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
        if (s.coordenadas and t.coordenadas in [vertice.coordenadas for vertice in self.vertices]):
            for a in self.aristas:
                if (a.origen.coordenadas == s.coordenadas) and (a.destino.coordenadas == t.coordenadas):
                    return tuple(a.data, a.peso)
                if not self.dirigido:
                    # si no es dirido, las aristas estan duplicadas (devolvemos la primera que encuentre)
                    if (a.origen.coordenadas == t.coordenadas) and (a.destino.coordenadas == s.coordenadas):
                        return tuple(a.data, a.peso)

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
        if u.coordenadas in [vertice.coordenadas for vertice in self.vertices]:
            lista = []
            for a in self.aristas:
                if a.origen.coordenadas == u.coordenadas:                   # Esto lo hace bien tanto para dirigido como para no dirigido (en el caso de no dirigido, las aristas estan duplicadas)
                    lista.append(a.destino)
                """ Esto creo que no es asi porque en los grafos dirigidos
                la adyacencia es solo aquellos en los que u es origen
                elif a.destino == u:
                    lista.append(a.origen)
                """
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
        if v.coordenadas in [vertice.coordenadas for vertice in self.vertices]:
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
        if v.coordenadas in [vertice.coordenadas for vertice in self.vertices]:
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
        if v in self.vertices:
            # esto funciona para dirigido y no dirigido, porque en no dirigido las aristas estan duplicadas
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
        pass

    def camino_minimo(self, origen:object, destino:object) -> List[object]:
        pass


    def prim(self)-> Dict[object,object]:
        """ Calcula un Árbol Abarcador Mínimo para el grafo
        usando el algoritmo de Prim.
        
        Args: None
        Returns: Devuelve un diccionario que indica, para cada vértice del
        grafo, qué vértice es su padre en el árbol abarcador mínimo.
        """
        pass
                    

    def kruskal(self)-> List[Tuple[object,object]]:
        """ Calcula un Árbol Abarcador Mínimo para el grafo
        usando el algoritmo de Prim.
        
        Args: None
        Returns: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
        de los pares de vértices del grafo
        que forman las aristas del arbol abarcador mínimo.
        """
        pass
                
    
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
    