import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class Face:
    def __init__(self, all_vertices, face):
        v0 = np.array(all_vertices[face[0]])
        v1 = np.array(all_vertices[face[1]])
        v2 = np.array(all_vertices[face[2]])
        normal = np.cross(v2 - v1, v0 - v1)
        # print(normal)
        comprimento = np.linalg.norm(normal)
        self.vertices = face
        self.normal = normal / comprimento
        self.centroide = np.mean([v0, v1, v2], axis=0)

    def is_visible(self, observador):
        O = np.array(observador) - self.centroide
        O_norm = np.linalg.norm(O)
        O_unit = O / O_norm
        angle = np.dot(O_unit, self.normal)
        # print(self.vertices)
        # print(self.centroide)
        # print(self.normal, O_unit)
        # print(angle)
        return angle > 0

    def get_dist(self, observador=(0, 20, 0)) -> int:
        diferenca = self.centroide - np.array(observador)
        distancia = np.linalg.norm(diferenca)
        return distancia


class Objeto3d:
    def __init__(self, polyline: list) -> None:
        self.__polyline = polyline


    def rotacaoX(self, segments=4):
        """ Cria um modelo 3D rotacionando uma polilinha em torno do eixo X. """

        polyline = [[x, y, 0] for x, y in self.__polyline]
        vertices = []
        faces = []
        edges = []

        # Adiciona vértices para cada segmento de rotação
        for i in range(segments):
            angle = (360 / segments) * i
            for point in polyline:
                rotated_point = self.rotate_point(point, angle)
                vertices.append(rotated_point)

        # Cria faces e arestas conectando os vértices
        for i in range(segments):
            for j in range(len(polyline) - 1):
                p1 = i * len(polyline) + j
                p2 = ((i + 1) % segments) * len(polyline) + j
                p3 = ((i + 1) % segments) * len(polyline) + (j + 1)
                p4 = i * len(polyline) + (j + 1)

                # Criação das faces
                faces.append(Face(vertices, [p1, p2, p3]))
                faces.append(Face(vertices, [p1, p3, p4]))

                # Criação das arestas
                edges.append([p1, p2])
                edges.append([p2, p3])
                edges.append([p3, p4])
                edges.append([p4, p1])
                edges.append([p1, p3])

        self.__vertices = np.array(vertices)
        self.__faces = np.array(faces)
        self.__edges = np.array(edges)

    def rotate_point(self, point, angle, axis='x'):
        """ Rotaciona um ponto em torno de um eixo por um determinado ângulo. """
        angle_rad = np.radians(angle)

        rotation_matrix = np.array([
            [1, 0, 0],
            [0, np.cos(angle_rad), -np.sin(angle_rad)],
            [0, np.sin(angle_rad), np.cos(angle_rad)]
        ])

        return np.dot(rotation_matrix, point)

    def get_faces(self):
        return self.__faces

    def get_edges(self):
        return self.__edges

    def get_vertices(self):
        # Criação de um array de 1s com a mesma quantidade de linhas
        ones_column = np.ones((self.__vertices.shape[0], 1))

        # Concatenando a coluna de 1s ao array original
        new_array = np.hstack((self.__vertices, ones_column))

        return new_array

    def get_centro_box_envolvente(self):
        vertices_array = np.array(self.__vertices)
        x_min, y_min, z_min = np.min(vertices_array, axis=0)
        x_max, y_max, z_max = np.max(vertices_array, axis=0)
        centro_x = (x_min + x_max) / 2
        centro_y = (y_min + y_max) / 2
        centro_z = (z_min + z_max) / 2
        return (centro_x, centro_y, centro_z)

    def pintor(self, observador=(1, 0, 0)):
        ordem = list()
        for i, f in enumerate(self.__faces):
            ordem.append([i, f.get_dist(observador)])

        ordem.sort(key=lambda x: x[1], reverse=True)

        faces_ordenadas = [i for i, _ in ordem]
        return faces_ordenadas

    def get_faces_visible(self, observador):
        ordem = list()
        for i, f in enumerate(self.__faces):
            if f.is_visible(observador):
                ordem.append([i, f.get_dist(observador), f])

        ordem.sort(key=lambda x: x[1], reverse=True)

        faces_ordenadas = [f for _, _, f in ordem]
        print(len(faces_ordenadas), len(self.__faces))
        return faces_ordenadas


    def visualize(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plotando vértices
        vertices = self.get_vertices()
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2])

        # Plotando faces
        for face in self.__faces:
            v0, v1, v2 = face.vertices
            tri = Poly3DCollection([[
                vertices[v0][:3],
                vertices[v1][:3],
                vertices[v2][:3]
            ]])
            tri.set_color((0, 1, 0, 0.5))  # Define cor verde com transparência
            tri.set_edgecolor('k')  # Define cor das arestas
            ax.add_collection3d(tri)

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        plt.show()


if __name__ == '__main__':
    obj1 = Objeto3d([(0, 10), (20, 20),(20,10), (0, 10)])
    obj1.rotacaoX(3)

    # print("Arestas:", obj1.get_edges())
    print("Vértices:\n", np.round(obj1.get_vertices(),1))
    # for f in obj1.get_faces_visible((-1, 0, 0)):
    #     print(f.vertices)


    for f in obj1.get_faces():
        print(f.vertices)

    obj1.visualize()