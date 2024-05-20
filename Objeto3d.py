import math

class Objeto3d:

    def __init__(self, polyline: list) -> None:
        self.__polyline: list = polyline
        self.__vertices = list()
        self.__faces = list()
        self.__arestas = list()        
        pass

    def rotacaoX(self, divisions: int) -> None:
        vertices = []
        print(self.__polyline)
        for i in range(divisions):
            angle = 2 * math.pi * i / divisions
            cos_angle = math.cos(angle)
            sin_angle = math.sin(angle)
            for x, y in self.__polyline:
                z_rotated = round(y * sin_angle, 2)
                y_rotated = round(y * cos_angle, 2)
                vertices.append((x, y_rotated, z_rotated))

        for i in range(len(vertices)):
            self.__arestas.append((vertices[i], vertices[(i+2)%len(vertices)]))

        for v in vertices:
            print(v)
        
        for a in self.__arestas:
            print(a)
        return vertices
