import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from camera import Camera, Projetion
from matrix_functions import *


class Face:
    def __init__(self, all_vertices, face):
        v0 = np.array(all_vertices[face[0]])
        v1 = np.array(all_vertices[face[1]])
        v2 = np.array(all_vertices[face[2]])
        normal = np.cross(v2 - v1, v0 - v1)
        comprimento = np.linalg.norm(normal)
        self.vertices = face
        self.normal = normal / comprimento
        self.centroide = np.mean([v0, v1, v2], axis=0)

    def is_visible(self, observador, open_surface):
        O = np.array(observador) - self.centroide
        O_norm = np.linalg.norm(O)
        O_unit = O / O_norm
        angle = np.dot(O_unit, self.normal)
        if open_surface:
            return angle != 0
        return angle > 0

    def get_dist(self, observador=(0, 20, 0)) -> int:
        diferenca = self.centroide - np.array(observador)
        distancia = np.linalg.norm(diferenca)
        return distancia


class Objeto3d:
    def __init__(self, polyline: list) -> None:
        self.__polyline = polyline
        self.normais_vetores = []
        self.rotacoes = 4
        self.material_a = (0.2, 0.3, 0.4)
        self.material_d = (0.2, 0.3, 0.4)
        self.material_s = (0.2, 0.3, 0.4)
        self.index_reflex = 10

    def set_materiais(self, material_a, material_d, mateirial_s, n):
        self.material_a = material_a
        self.material_d = material_d
        self.material_s = mateirial_s
        self.index_reflex = n

    def create(self, segments=4):
        """ Cria um modelo 3D rotacionando uma polilinha em torno do eixo X. """

        self.rotacoes = segments
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
        vertices = np.array(vertices)
        ones_column = np.ones((vertices.shape[0], 1))
        new_array = np.hstack((vertices, ones_column))
        self.__vertices_h = new_array

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
        # ones_column = np.ones((self.__vertices.shape[0], 1))
        # new_array = np.hstack((self.__vertices, ones_column))
        # return new_array
        return self.__vertices_h

    def rotacao(self, angle, axis):
        if axis == 'Y':
            vertices = rotate_y(angle)  @ self.get_vertices().T
        if axis == 'X':
            vertices = rotate_x(angle)  @ self.get_vertices().T
        if axis == 'Z':
            vertices = rotate_z(angle)  @ self.get_vertices().T
        self.__vertices = vertices.T[:2].T
        self.__vertices_h = vertices.T

    def translado(self, point = (0,0,0)):
        vertices = self.get_vertices()
        ones_column = np.ones((vertices.shape[0], 1))
        new_array = np.hstack((vertices, ones_column))
        vertices = translate(point) @ new_array.T[:4]
        self.__vertices = vertices[:3].T
        self.__vertices_h = vertices.T

    def internal_rotate(self, angle, axis):
        G = np.array(self.get_centro_box_envolvente())
        print(self.__vertices)
        if axis == 'Y':
            vertices = translate(G) @ rotate_y(angle) @ translate(-G)  @ self.__vertices_h.T
        if axis == 'X':
            vertices = translate(G) @ rotate_x(angle) @ translate(-G)  @ self.__vertices_h.T
        if axis == 'Z':
            vertices = translate(G) @ rotate_z(angle) @ translate(-G)  @ self.__vertices_h.T
        self.__vertices = vertices[:3].T
        self.__vertices_h = vertices.T
        print(vertices)
        


    def scale(self, fator):
        vertices = translate(fator) @ self.get_vertices().T
        self.__vertices = vertices[:3].T
        self.__vertices_h = vertices.T


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
        
        open_surface = False
        if not np.array_equal(self.__polyline[-1], self.__polyline[0]):
            open_surface = True
        for i, f in enumerate(self.__faces):
            if f.is_visible(observador, open_surface):
                ordem.append([i, f.get_dist(observador), f])

        ordem.sort(key=lambda x: x[1], reverse=True)

        faces_ordenadas = [f for _, _, f in ordem]
        return faces_ordenadas

    def create_objetos(self, obs):
        self.camera = Camera(obs, (0, 0, 0), (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(410)
        self.to_screen = Projetion().to_screen(-800//2, 800//2, -
                                               800//2, 800//2, 0, 800, 0, 800)

        # self.to_screen = Projetion().to_screen(-8, 8, -6, 6, 0, self.width, 0, self.height)

        return self.to_screen @ self.projetion @ self.camera.camera_matrix()

    def visualize(self, observador=(20, -20, 20)):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # Plotando vértices
        vertices = (self.create_objetos(observador) @ self.get_vertices().T)
        vertices /= vertices[-1]
        vertices = vertices.T
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2])
        # Plotando apenas as faces visíveis
        for face in self.get_faces_visible(observador):
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

    def calc_normais_vertices(self):
        self.normais_vetores = []
        for i, v in enumerate(self.__vertices):
            n_unit = np.array([0.0, 0.0, 0.0])
            for f in self.__faces:
                if i in f.vertices:
                    n_unit += np.array(f.normal)

            norm = np.linalg.norm(n_unit)
            n_unit /= norm
            self.normais_vetores.append(n_unit)


if __name__ == '__main__':
    obj1 = Objeto3d([(-15, 10), (15, 15)])
    obj1.rotacaoX(4)

    # print("Arestas:", obj1.get_edges())
    # print("Vértices:\n", np.round(obj1.get_vertices(),1))
    # for f in obj1.get_faces_visible((-1, 0, 0)):
    #     print(f.vertices)

    # for f in obj1.get_faces():
    #     print(f.vertices)

    obj1.calc_normais_vertices()
