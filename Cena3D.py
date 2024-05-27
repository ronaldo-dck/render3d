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
        self.width = 800
        self.height = 800
        self.z_buffer = np.full((self.height, self.width), -float('inf'))
        self.cor_buffer = np.full((self.height, self.width, 3), [
            174, 174, 174], dtype=np.uint8)
        for obj in self.objetos:
            obj.rotacaoX(4)

        self.camera_pos = [20, -20, 20]
        self.camera_lookat = [0, 0, 0]

        pg.font.init()
        self.font = pg.font.SysFont(None, 36)

        self.__cores_faces = [[(random.uniform(0, 1), random.uniform(
            0, 1), random.uniform(0, 1)) for _ in obj.get_faces()] for obj in self.objetos]

    def create_objetos(self):
        self.camera = Camera(self.camera_pos, self.camera_lookat, (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(410)
        self.to_screen = Projetion().to_screen(-self.width//2, self.width//2, -
                                               self.height//2, self.height//2, 0, self.width, 0, self.height)

        # self.to_screen = Projetion().to_screen(-8, 8, -6, 6, 0, self.width, 0, self.height)

        return self.to_screen @ self.projetion @ self.camera.camera_matrix()


    def fillpoly(self, face, all_vertices, color):
        i_vertices = face.vertices
        selected_vertices = all_vertices[i_vertices]
        vertices = sorted(selected_vertices, key=lambda v: v[1])
        # vertices = selected_vertices

        (x0, y0), z0 = map(int, vertices[0][:2]), float(vertices[0][2])
        (x1, y1), z1 = map(int, vertices[1][:2]), float(vertices[1][2])
        (x2, y2), z2 = map(int, vertices[2][:2]), float(vertices[2][2])

        arestas = [
            {
                'ini': (x0, y0, z0),
                'fim': (x1, y1, z1),
                'taxaX': ((x1 - x0) / ((y1 - y0) + 1e-16)),
                'taxaZ': ((z1 - z0) / ((y1 - y0) + 1e-16))
            },
            {
                'ini': (x1, y1, z1),
                'fim': (x2, y2, z2),
                'taxaX': ((x2 - x1) / ((y2 - y1) + 1e-16)),
                'taxaZ': ((z2 - z1) / ((y2 - y1 + 1e-16)))
            },
            {
                'ini': (x2, y2, z2),
                'fim': (x0, y0, z0),
                'taxaX': ((x0 - x2) / ((y0 - y2) + 1e-16)),
                'taxaZ': ((z0 - z2) / ((y0 - y2) + 1e-16))
            }
        ]

        arestas.sort(key=lambda x: x['ini'][1])

        # print(arestas)

        lastIniX = arestas[0]['ini'][0]
        lastFimX = arestas[0]['ini'][0]
        lastIniZ = arestas[0]['ini'][2]
        lastFimZ = arestas[0]['ini'][2]

        swapped = False
        if (arestas[0]['ini'][0] > arestas[1]['ini'][0]):
            swapped = True

        for y in range(arestas[0]['ini'][1], arestas[0]['fim'][1]):
            lastIniX += arestas[0]['taxaX']
            lastFimX += arestas[2]['taxaX']
            lastIniZ += arestas[0]['taxaZ']
            lastFimZ += arestas[2]['taxaZ']

            lastIniX = round(lastIniX)
            lastFimX = round(lastFimX)

            varX = (lastFimX - lastIniX) + 1e-16
            if varX == 0:
                deltaZ = 0
            else:
                deltaZ = (lastFimZ - lastIniZ) / varX
            startZ = lastIniZ

            # print(lastIniX, lastFimX)
            if swapped:
                for x in range(lastIniX, lastFimX):
                    self.screen.set_at((x, y), color)
                    startZ += deltaZ
            else:
                for x in range(lastFimX, lastIniX):
                    self.screen.set_at((x, y), color)
                    startZ += deltaZ

        lastIniZ = arestas[1]['ini'][2]

        for y in range(arestas[1]['ini'][1], arestas[1]['fim'][1]):
            lastIniX += arestas[1]['taxaX']
            lastFimX += arestas[2]['taxaX']
            lastIniZ += arestas[1]['taxaZ']
            lastFimZ += arestas[2]['taxaZ']

            lastIniX = round(lastIniX)
            lastFimX = round(lastFimX)

            varX = (lastFimX - lastIniX) + 1e-16
            if varX == 0:
                deltaZ = 0
            else:
                deltaZ = (lastFimZ - lastIniZ) / varX
            startZ = lastIniZ

            if swapped:
                for x in range(lastIniX, lastFimX):
                    self.screen.set_at((x, y), color)
                    startZ += deltaZ
            else:
                for x in range(lastFimX, lastIniX):
                    self.screen.set_at((x, y), color)
                    startZ += deltaZ



    def render(self):
        for obj_idx, o in enumerate(self.objetos):
            # faces = o.get_faces_visible(self.camera_pos)
            faces = o.get_faces()

            vertices = self.create_objetos() @ o.get_vertices().T
            vertices[[0, 1]] /= vertices[-1]
            # vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            vertices = vertices.T
            # print(np.round(np.array(vertices), 1))
            # print(np.round(o.get_vertices(), 1))
            # print(np.array([f.vertices for f in faces ]))

            
            for face_idx, face in enumerate(faces):
                # points = vertices[face.vertices].T[:2].T
                # pg.draw.polygon(self.screen, (255, 0, 0), points)
                self.fillpoly(face, vertices, (200//(face_idx+1),100//(face_idx+1),0))
                # pg.surfarray.blit_array(self.screen, cores)

            # for y, linha in enumerate(self.cor_buffer):
            #     for x, pixel in enumerate(linha):
            #         self.screen.set_at((x, y), (pixel[0], pixel[1], pixel[2]))
            #         # pg.display.flip()
                    # self.screen.blit_array(self.screen, (pixel[0], pixel[1], pixel[2]))
    def draw_mouse_coords(self, screen, x, y):
        coord_text = f"X: {x}, Y: {y}"
        text_surf = self.font.render(coord_text, True, (0, 0, 0))
        screen.blit(text_surf, (10, 70))

    def draw_cam_coords(self, screen, x, y, z):
        coord_text = f"X: {x}, Y: {y}, Z: {z}"
        text_surf = self.font.render(coord_text, True, (100, 100, 100))
        screen.blit(text_surf, (10, 140))

    def draw_lookat_coords(self, screen, x, y, z):
        coord_text = f"X: {x}, Y: {y}, Z: {z}"
        text_surf = self.font.render(coord_text, True, (100, 100, 200))
        screen.blit(text_surf, (10, 105))

    def run(self):
        pg.init()
        size = (self.width, self.height)
        self.screen = pg.display.set_mode(size, display=1, flags=RESIZABLE)
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
                    elif event.key == pg.K_a:
                        self.camera_pos[0] -= 1
                    elif event.key == pg.K_d:
                        self.camera_pos[0] += 1
                    elif event.key == pg.K_w:
                        self.camera_pos[2] += 1
                    elif event.key == pg.K_s:
                        self.camera_pos[2] -= 1
                    elif event.key == pg.K_q:
                        self.camera_pos[1] += 1
                    elif event.key == pg.K_e:
                        self.camera_pos[1] -= 1
                    elif event.key == pg.K_UP:
                        self.camera_lookat[1] += 1
                    elif event.key == pg.K_DOWN:
                        self.camera_lookat[1] -= 1
                    elif event.key == pg.K_LEFT:
                        self.camera_lookat[0] -= 1
                    elif event.key == pg.K_RIGHT:
                        self.camera_lookat[0] += 1


                # Obtém a posição atual do mouse
            mouse_x, mouse_y = pg.mouse.get_pos()


            # Cria uma superfície com as coordenadas do mouse

        # Define a posição onde o texto será renderizado
            self.screen.fill(pg.Color('darkslategray'))
            self.render()
            self.draw_mouse_coords(self.screen, mouse_x, mouse_y)
            self.draw_cam_coords(self.screen, self.camera_pos[0], self.camera_pos[1], self.camera_pos[2])
            self.draw_lookat_coords(self.screen, self.camera_lookat[0], self.camera_lookat[1], self.camera_lookat[2])

            pg.display.flip()
            clock.tick(4)  # Limita o loop a 60 frames por segundo

        pg.quit()


if __name__ == '__main__':
    polylines = [
        # (((1, 0), (-1, 1), (1, 1), (1, 0))),
        # (((100, 0), (-200, 200), (-100, -100), (100, 0)))
        # Novo objeto adicionado
        ((10,10),(15,10))
        # ((-10, 10), (10, 10))
    ]
    Cena3D(polylines).run()
