import numpy as np

class Face:
    def __init__(self, all_vertices, face):
        v0 = np.array(all_vertices[face[0]])
        v1 = np.array(all_vertices[face[1]])
        v2 = np.array(all_vertices[face[2]])
        normal = np.cross(v1 - v0, v2 - v0)
        comprimento = np.linalg.norm(normal)
        self.vertices = face
        self.normal = normal / comprimento
        self.centroide = np.mean([v0, v1, v2], axis=0)

    def is_visible(self, observador=(-10, 20, 0)):
        O = np.array(observador) - self.centroide
        O_norm = np.linalg.norm(O)
        O_unit = O / O_norm
        angle = np.dot(O_unit, self.normal)
        return angle > 0

    def get_dist(self, observador=(0, 20, 0)) -> int:
        diferenca = self.centroide - np.array(observador)
        distancia = np.linalg.norm(diferenca)
        return distancia

class Objeto3d:
    def __init__(self, polyline: list) -> None:
        self.__polyline = polyline
        self.__vertices = []
        self.__faces = []
        self.__arestas = []

    def rotacaoX(self, divisions: int) -> None:
        if len(self.__polyline) < 2:
            print("Erro: Insuficientes pontos para rotação.")
            return

        vertices = self.__generate_vertices(divisions)
        self.__vertices = vertices
        faces = self.__generate_faces(divisions, len(self.__polyline))
        self.__faces = faces
        arestas = self.__generate_edges(divisions, len(self.__polyline))
        self.__arestas = arestas

    def __generate_vertices(self, divisions: int):
        vertices = []
        theta = np.linspace(0, 2 * np.pi, divisions, endpoint=False)
        for x, y in self.__polyline:
            for angle in theta:
                y_rot = round(y * np.cos(angle), 2)
                z = round(y * np.sin(angle), 2)
                vertices.append([x, y_rot, z])
        return np.array(vertices)

    def __generate_faces(self, divisions: int, num_points: int):
        faces = []
        for i in range(num_points - 1):
            for j in range(divisions):
                current = i * divisions + j
                next_ = i * divisions + (j + 1) % divisions
                current_bottom = (i + 1) * divisions + j
                next_bottom = (i + 1) * divisions + (j + 1) % divisions

                faces.append(Face(self.__vertices,[current, next_, next_bottom]))
                faces.append(Face(self.__vertices,[current, next_bottom, current_bottom]))
        return faces

    def __generate_edges(self, divisions: int, num_points: int):
        arestas = []
        for i in range(num_points):
            for j in range(divisions):
                current = i * divisions + j
                next_in_row = i * divisions + (j + 1) % divisions
                next_row = (i + 1) * divisions + j

                arestas.append((current, next_in_row))
                if i < num_points - 1:
                    arestas.append((current, next_row))
        return arestas

    def get_faces(self):
        return self.__faces

    def get_edges(self):
        return self.__arestas

    def get_vertices(self):
        return self.__vertices

    def get_centro_box_envolvente(self):
        vertices_array = np.array(self.__vertices)
        x_min, y_min, z_min = np.min(vertices_array, axis=0)
        x_max, y_max, z_max = np.max(vertices_array, axis=0)
        centro_x = (x_min + x_max) / 2
        centro_y = (y_min + y_max) / 2
        centro_z = (z_min + z_max) / 2
        return (centro_x, centro_y, centro_z)

    def pintor(self, observador = (1,0,0)): 
        ordem = list()
        for i,f in enumerate(self.__faces):
            ordem.append([i, f.get_dist(observador)])
        

        ordem.sort(key=lambda x: x[1], reverse=True)
        
        faces_ordenadas = [i for i, _ in ordem]
        return faces_ordenadas



if __name__ == '__main__':
    obj1 = Objeto3d([(2, 4), (4, 4)])
    obj1.rotacaoX(3)
    obj1.pintor()

    # print("Arestas:", obj1.get_edges())
    # print("Faces:", obj1.get_faces())
    # print("Vértices:", obj1.get_vertices())
    # print("Centro da caixa envolvente:", obj1.get_centro_box_envolvente())
