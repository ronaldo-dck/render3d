import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Objeto3d import Objeto3d, Face
import random
from camera import Camera, Projetion
import numpy as np


class Cena3D:
    def __init__(self, polylines=[((10, 0), (20, 10))]):
        self.objetos = [Objeto3d(p) for p in polylines]
        self.width = 620
        self.height = 620
        self.z_buffer = np.full((self.height, self.width), -float('inf'))
        self.cor_buffer = np.full((self.height, self.width, 3), [
            174, 174, 174], dtype=np.uint8)
        for obj in self.objetos:
            obj.rotacaoX(4)

        self.camera_pos = (-1, 0, 0)
        self.camera_lookat = (0, 0, 0)

        self.__cores_faces = [[(random.uniform(0, 1), random.uniform(
            0, 1), random.uniform(0, 1)) for _ in obj.get_faces()] for obj in self.objetos]

    def create_objetos(self):
        self.camera = Camera(self.camera_pos, self.camera_lookat, (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(100)
        self.to_screen = Projetion().to_screen(-self.width//2, self.width//2, -
                                               self.width//2, self.height//2, 0, self.width, 0, self.height)

        # self.to_screen = Projetion().to_screen(-8, 8, -6, 6, 0, self.width, 0, self.height)

        return self.to_screen @ self.projetion @ self.camera.camera_matrix()

    def fillpoly(self, face, all_vertices, color):

        i_vertices = face.vertices
        selected_vertices = all_vertices[i_vertices]
        vertices = sorted(selected_vertices, key=lambda v: v[1], reverse=False)

        (x1, y1), z1 = map(int, vertices[0][:2]), float(vertices[0][2])
        (x2, y2), z2 = map(int, vertices[1][:2]), float(vertices[1][2])
        (x3, y3), z3 = map(int, vertices[2][:2]), float(vertices[2][2])

        # Test data
        # x1, y1, z1 = 93, 251, -22.807
        # x2, y2, z2 = 198, 241, -20.129
        # x3, y3, z3 = 125, 107, -21.815

        # Calculate inverse slope coefficients for edges
        tx21 = (x2 - x1) / (y2 - y1) if (y2 - y1) != 0 else 0
        tx31 = (x3 - x1) / (y3 - y1) if (y3 - y1) != 0 else 0
        tx32 = (x3 - x2) / (y3 - y2) if (y3 - y2) != 0 else 0

        tz21 = (z2 - z1) / (y2 - y1) if (y2 - y1) != 0 else 0
        tz31 = (z3 - z1) / (y3 - y1) if (y3 - y1) != 0 else 0
        tz32 = (z3 - z2) / (y3 - y2) if (y3 - y2) != 0 else 0

        height = self.height
        width = self.width

        aresta1 = np.full((height, 2), 0.0)
        aresta2 = np.full((height, 2), 0.0)
        aresta3 = np.full((height, 2), 0.0)

        # Filling edges with vertices data
        x, z = float(x3), float(z3)
        for i in range(y3, y1):
            if x >= 0 and i >= 0 and x < width and i < height:
                aresta1[i] = [x, z]
                x += tx31
                z += tz31

        x, z = float(x3), float(z3)
        for i in range(y3, y2):
            if x >= 0 and i >= 0 and x < width and i < height:
                aresta2[i] = [x, z]
                x += tx32
                z += tz32

        x, z = float(x2), float(z2)
        for i in range(y2, y1):
            if x >= 0 and i >= 0 and x < width and i < height:
                aresta3[i] = [x, z]
                x += tx21
                z += tz21

        # Fill the polygon
        for y in range(y3, y1):
            if y >= self.height:
                break
            if y < 0:
                continue

            if aresta1[y][0] > aresta2[y][0]:
                aresta1[y], aresta2[y] = aresta2[y], aresta1[y]

            x_start = int(aresta1[y][0])
            x_end = int(aresta2[y][0])

            if x_start != x_end:
                z_start = aresta1[y][1]
                z_end = aresta2[y][1]
                dz = (z_end - z_start) / (x_end - x_start)

                z = z_start
                for x in range(x_start, x_end):

                    if x > 0 and y > 0 and x < width and y < height:
                        if z > self.z_buffer[y, x]:
                            self.z_buffer[y, x] = z
                            self.cor_buffer[y, x] = color
                    z += dz

    def render(self):
        for obj_idx, o in enumerate(self.objetos):
            faces = o.get_faces_visible(self.camera_pos)
            # faces = o.get_faces()

            vertices = self.create_objetos() @ o.get_vertices().T
            vertices[[0, 1]] /= vertices[-1]
            # vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            vertices = vertices.T

            # vertices = np.array(
            #     [
            #         [21.2, 34.1, 18.8, 5.9,	20],
            #         [0.7,	3.4,	5.6,	2.9,	20.9],
            #         [42.3,	27.2,	14.6,	29.7,	31.6],
            #     ]
            # ).T
            # faces = list()
            # faces.append(Face(vertices, [0, 1, 4]))
            # faces.append(Face(vertices, [1, 2, 4]))
            # faces.append(Face(vertices, [2, 3, 4]))
            # faces.append(Face(vertices, [3, 0, 4]))

            # vertices = np.array([
            #     [93, 251, -22.807],  # vértice 0
            #     [198, 241, -20.129],  # vértice 1
            #     [125, 107, -21.815],  # vértice 2
            #     [400, 100, -19.815],  # vértice 3 (novo)
            #     [400, 500, -8.815],  # vértice 4 (novo)
            #     [200, 550, -17.815]  # vértice 5 (novo)
            # ])
            # faces = list()

            # faces.append(
            #     Face(vertices, [0, 1, 2])
            # )
            # faces.append(
            #     Face(vertices, [3, 4, 5])
            # )
            # faces.append(Face(vertices, [1, 4, 5]))

            (randomColor1, randomColor2, randomColor3) = (
                random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
            
            for face_idx, face in enumerate(faces):
                # points = vertices[face.vertices].T[:2].T
                # pg.draw.polygon(self.screen, (255, 0, 0), points)
                self.fillpoly(face, vertices, [
                            face_idx*10*randomColor1, face_idx*40*randomColor2, face_idx*30*randomColor3])
                # pg.surfarray.blit_array(self.screen, cores)

            for y, linha in enumerate(self.cor_buffer):
                for x, pixel in enumerate(linha):
                    self.screen.set_at((x, y), (pixel[0], pixel[1], pixel[2]))
                    # pg.display.flip()
                    # self.screen.blit_array(self.screen, (pixel[0], pixel[1], pixel[2]))

    def run(self):
        pg.init()
        size = (self.width, self.height)
        self.screen = pg.display.set_mode(size, display=0, flags=RESIZABLE)
        clock = pg.time.Clock()

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.VIDEORESIZE:
                    self.width = event.w
                    self.height = event.h
                    self.z_buffer = np.full(
                        (self.height, self.width), -float('inf'))
                    self.cor_buffer = np.full(
                        (self.height, self.width, 3), (24, 24, 24))

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False

            self.screen.fill(pg.Color('darkslategray'))
            self.render()

            pg.display.flip()
            clock.tick(24)  # Limita o loop a 60 frames por segundo

        pg.quit()


if __name__ == '__main__':
    polylines = [
        # (((1, 0), (-1, 1), (1, 1), (1, 0))),
        # (((100, 0), (-200, 200), (-100, -100), (100, 0))),
        # Novo objeto adicionado
        ((-10, 10), (10, 10))
    ]
    Cena3D(polylines).run()
