

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


class Vertice:

    def __init__(self, num, coordenadas):
        self.num = num
        self.calles = []               # Las calles pasan por este vertice
        # self.adyacentes = []           # Esto no estoy segura si hay que ponerlo
        self.coordenadas = coordenadas # [x,y]
        self.aristas = []              # Aquí iremos añadiendo las aristas que salen del vertice

        def __eq__(slef,vertice):
            pass
        def __hash__(self):
            pass
    

