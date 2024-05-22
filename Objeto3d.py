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
            self.__arestas.append(
                (vertices[i], vertices[(i + len(self.__polyline)) % len(vertices)]))

        for j in range(0, divisions * len(self.__polyline), len(self.__polyline)):
            self.__arestas.append((vertices[j], vertices[j + 1]))

        for i in range(len(vertices)):
            face = list()
            face.append(vertices[i])
            face.append(vertices[(i+1) % len(vertices)])
            face.append(vertices[(i + len(self.__polyline)) % len(vertices)])
            face.append(vertices[(i+1 + len(self.__polyline)) % len(vertices)])
            self.__faces.append(face)

        for v in vertices:
            print(v)

        for a in self.__arestas:
            print(a)
        print('faces')
        for f in self.__faces:
            print(f)

        self.__vertices = vertices
        return vertices

    def atribuirLetrasEArestas(self):
        if not self.__vertices:
            print("Execute a rotação antes de atribuir letras e arestas.")
            return

        letras = [chr(i) for i in range(65, 65 + len(self.__vertices))]
        vertice_letra_map = {letras[i]: self.__vertices[i]
                             for i in range(len(self.__vertices))}

        print("Vértices com letras:")
        for letra, vertice in vertice_letra_map.items():
            print(f"{letra}: {vertice}")

        arestas_com_letras = []
        for a in self.__arestas:
            v1_letra = [letra for letra,
                        vertice in vertice_letra_map.items() if vertice == a[0]]
            v2_letra = [letra for letra,
                        vertice in vertice_letra_map.items() if vertice == a[1]]
            if v1_letra and v2_letra:
                arestas_com_letras.append((v1_letra[0], v2_letra[0]))

        print("Arestas com letras:")
        for a in arestas_com_letras:
            print(a)

        print("Faces com letras:")
        for face in self.__faces:
            face_letras = [
                letra for letra, vertice in vertice_letra_map.items() if vertice in face]
            if len(face_letras) == len(face):
                print(f"{face_letras}")


if __name__ == '__main__':
    obj1 = Objeto3d([(200, 200), (400, 200)])
    obj2 = Objeto3d([(200, 200), (400, 200), (600, 200)])
    obj1.rotacaoX(4)
    obj2.rotacaoX(4)
    obj1.atribuirLetrasEArestas()
    obj2.atribuirLetrasEArestas()
    pass
