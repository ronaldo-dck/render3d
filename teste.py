import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from camera import Camera, Projetion

class Segment:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

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

    def is_visible(self, observador):
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

    def rotacaoX(self, segments=4):
        polyline = [[x, y, 0] for x, y in self.__polyline]
        vertices = []
        faces = []
        edges = []

        for i in range(segments):
            angle = (360 / segments) * i
            for point in polyline:
                rotated_point = self.rotate_point(point, angle)
                vertices.append(rotated_point)

        for i in range(segments):
            for j in range(len(polyline) - 1):
                p1 = i * len(polyline) + j
                p2 = ((i + 1) % segments) * len(polyline) + j
                p3 = ((i + 1) % segments) * len(polyline) + (j + 1)
                p4 = i * len(polyline) + (j + 1)

                faces.append(Face(vertices, [p1, p2, p3]))
                faces.append(Face(vertices, [p1, p3, p4]))

                edges.append(Segment(p1, p2))
                edges.append(Segment(p2, p3))
                edges.append(Segment(p3, p4))
                edges.append(Segment(p4, p1))
                edges.append(Segment(p1, p3))

        self.__vertices = np.array(vertices)
        self.__faces = np.array(faces)
        self.__edges = np.array(edges)

    def rotate_point(self, point, angle, axis='x'):
        angle_rad = np.radians(angle)
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, np.cos(angle_rad), -np.sin(angle_rad)],
            [0, np.sin(angle_rad), np.cos(angle_rad)]
        ])
        return np.dot(rotation_matrix, point)

    def get_faces(self):
        return self.__faces

    def set_vertices(self,vertices):
        self.__vertices = vertices

    def get_edges(self):
        return self.__edges

    def get_vertices(self):
        ones_column = np.ones((self.__vertices.shape[0], 1))
        new_array = np.hstack((self.__vertices, ones_column))
        # print(self.__vertices.shape, new_array.shape)
        return self.__vertices

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
        return faces_ordenadas

    def create_objetos(self, obs):
        self.camera = Camera(obs, (0,0,0), (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(410)
        self.to_screen = Projetion().to_screen(-800//2, 800//2, -800//2, 800//2, 0, 800, 0, 800)
        return self.to_screen @ self.projetion @ self.camera.camera_matrix()

    def visualize(self, observador=(20,-20,20)):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        vertices = (self.create_objetos(observador) @ self.get_vertices().T)
        vertices /= vertices[-1]

        vertices = vertices.T
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2])
        for face in self.get_faces_visible(observador):
            v0, v1, v2 = face.vertices
            tri = Poly3DCollection([[
                vertices[v0][:3],
                vertices[v1][:3],
                vertices[v2][:3]
            ]])
            tri.set_color((0, 1, 0, 0.5))
            tri.set_edgecolor('k')
            ax.add_collection3d(tri)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()


        
def render_poly(poly, z_buffer, color_buffer):
    width, height = z_buffer.shape[1], z_buffer.shape[0]
    for face in poly.get_faces():
        scanline_edges = []
        face_indices = face.vertices
        v0, v1, v2 = [poly.get_vertices()[i][:3] for i in face_indices]
        v = v1 - v0
        u = v2 - v0
        n = np.cross(v, u)
        a, c = n[0], n[2]
        z_delta = -(a / c)
        lowest_y = float('inf')
        highest_y = float('-inf')
        for i in range(len(face_indices)):
            p1 = poly.get_vertices()[face_indices[i % 3]][:3]
            p2 = poly.get_vertices()[face_indices[(i + 1) % 3]][:3]
            if p2[1] == p1[1]:
                highest_x, lowest_x = int(max(p1[0], p2[0])), int(min(p1[0], p2[0]))
                const_y = int(p1[1])
                if const_y < 0 or const_y >= height:
                    continue
                start_z = p1[2] if p1[0] > p2[0] else p2[2]
                for j in range(lowest_x, highest_x + 1):
                    if j < 0 or j >= width:
                        continue
                    if z_buffer[const_y, j] > start_z:
                        z_buffer[const_y, j] = start_z
                        color_buffer[const_y, j] = poly.get_color()
                    start_z += z_delta
                continue

            if p1[1] < p2[1]:
                p1, p2 = p2, p1

            edge = {
                'max_y': int(p1[1]), 'max_y_x': int(p1[0]), 'max_y_z': p1[2],
                'min_y': int(p2[1]), 'min_y_x': int(p2[0]), 'min_y_z': p2[2],
                'x_y_delta': (p1[0] - p2[0]) / (p1[1] - p2[1]),
                'z_y_delta': (p1[2] - p2[2]) / (p1[1] - p2[1])
            }

            if edge['min_y'] < lowest_y:
                lowest_y = edge['min_y']
            if edge['max_y'] > highest_y:
                highest_y = edge['max_y']

            scanline_edges.append(edge)

        scanline_edges.sort(key=lambda edge: edge['min_y'])
        current_y = int(lowest_y)
        end_y = int(highest_y)
        active_edges = []

        while current_y <= end_y:
            for j in range(len(scanline_edges) - 1, -1, -1):
                if scanline_edges[j]['min_y'] == current_y:
                    active_edge = {
                        'min_y_x': scanline_edges[j]['min_y_x'], 'min_y_z': scanline_edges[j]['min_y_z'],
                        'y_max': scanline_edges[j]['max_y'], 'y_min': scanline_edges[j]['min_y'],
                        'm_inversed': scanline_edges[j]['x_y_delta'], 'm_z_inversed': scanline_edges[j]['z_y_delta']
                    }
                    active_edges.append(active_edge)
                    del scanline_edges[j]

            for j in range(len(active_edges) - 1, -1, -1):
                if current_y == active_edges[j]['y_max']:
                    del active_edges[j]

            if len(active_edges) < 2:
                current_y += 1
                continue

            active_edges.sort(key=lambda edge: edge['min_y_x'])
            for i in range(0, len(active_edges) - 1, 2):
                x_start = int(active_edges[i]['min_y_x'])
                x_end = int(active_edges[i + 1]['min_y_x'])
                z_start = active_edges[i]['min_y_z']
                z_delta = (active_edges[i + 1]['min_y_z'] - active_edges[i]['min_y_z']) / (x_end - x_start)
                for j in range(x_start, x_end):
                    if j < 0 or j >= z_buffer.shape[1] or current_y < 0 or current_y >= z_buffer.shape[0]:
                        continue
                    if z_buffer[current_y, j] > z_start:
                        z_buffer[current_y, j] = z_start
                        color_buffer[current_y, j] = [0, 255, 0]  # Define a cor para verde
                    z_start += z_delta

            for edge in active_edges:
                edge['min_y_x'] += edge['m_inversed']
                edge['min_y_z'] += edge['m_z_inversed']

            current_y += 1


if __name__ == '__main__':
    width, height = 800, 800
    z_buffer = np.full((height, width), float('inf'))
    color_buffer = np.zeros((height, width, 3), dtype=np.uint8)

    obj1 = Objeto3d([(0, 100), (150, 500), (200,120)])
    obj1.rotacaoX(30)

    render_poly(obj1, z_buffer, color_buffer)

    plt.imshow(color_buffer)
    plt.show()
