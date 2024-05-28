import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Objeto3d import Objeto3d, Face
import random
from camera import Camera, Projetion
import luz

import numpy as np


class Cena3D:
    def __init__(self, polylines=[((220, 400), (600, 200), (220, 400))]):
        self.objetos = [Objeto3d(p) for p in polylines]
        self.width = 800
        self.height = 800
        self.z_buffer = np.full((self.height, self.width), -float('inf'))
        self.cor_buffer = np.full((self.height, self.width, 3), [
            174, 174, 174], dtype=np.uint8)
        for obj in self.objetos:
            obj.rotacaoX(6)
        self.axis = False
        self.camera_pos = [-1,0, 0]
        self.camera_lookat = [0, 0, 0]

        pg.font.init()
        self.font = pg.font.SysFont(None, 36)
        

        # self.__cores_faces = [[(random.uniform(0, 1), random.uniform(
        #     0, 1), random.uniform(0, 1)) for _ in obj.get_faces()] for obj in self.objetos]

    def create_objetos(self):
        self.camera = Camera(self.camera_pos, self.camera_lookat, (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(200)
        if self.axis:
            self.projetion = np.array([
                [1,0,0,0],
                [0,1,0,0],
                [0,0,1,0],
                [0,0,0,1]
            ])
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

        # for y in range(arestas[1]['ini'][1], arestas[1]['fim'][1]):
        #     lastIniX += arestas[1]['taxaX']
        #     lastFimX += arestas[2]['taxaX']
        #     lastIniZ += arestas[1]['taxaZ']
        #     lastFimZ += arestas[2]['taxaZ']

        #     lastIniX = round(lastIniX)
        #     lastFimX = round(lastFimX)

        #     varX = (lastFimX - lastIniX) + 1e-16
        #     if varX == 0:
        #         deltaZ = 0
        #     else:
        #         deltaZ = (lastFimZ - lastIniZ) / varX
        #     startZ = lastIniZ

        #     if swapped:
        #         for x in range(lastIniX, lastFimX):
        #             self.screen.set_at((x, y), color)
        #             startZ += deltaZ
        #     else:
        #         for x in range(lastFimX, lastIniX):
        #             self.screen.set_at((x, y), color)
        #             startZ += deltaZ

    def draw_vertices(self, points = []):
        for obj_idx, o in enumerate(self.objetos):
            # faces = o.get_faces_visible(self.camera_pos)
            # faces = o.get_faces()
            # vertices = o.get_vertices()
            # ones_column = np.ones((vertices.shape[0], 1))
            # new_array = np.hstack((vertices, ones_column))

            # vertices = self.create_objetos() @ new_array.T[:4]
            # vertices[[0, 1]] /= vertices[-1]
            # # vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            # vertices = vertices.T

            # for face_idx, face in enumerate(faces):
                # points = vertices[face.vertices].T[:2].T.astype(int)

                for p in points:
                    pg.draw.circle(self.screen, (255, 255, 255), p, 3)
                # self.fillpoly(face, vertices, (200//(face_idx+1),100//(face_idx+1),0))

                pass

    def fillpoli(self, face, all_vertices, color):
        vertices = all_vertices[face.vertices]
        # self.poly.pontos.sort(key=lambda p: p['y'])
        # v0, v1, v2 = self.poly.pontos[0], self.poly.pontos[1], self.poly.pontos[2]

        vertices = sorted(vertices, key=lambda v: v[1])
        # vertices = selected_vertices

        # (x0, y0), z0 = map(int, vertices[0][:2]), float(vertices[0][2])
        # (x1, y1), z1 = map(int, vertices[1][:2]), float(vertices[1][2])
        # (x2, y2), z2 = map(int, vertices[2][:2]), float(vertices[2][2])
        v0 = {
            'x': vertices[0][0],
            'y': vertices[0][1],
            'z': vertices[0][2],
        }
        v1 = {
            'x': vertices[1][0],
            'y': vertices[1][1],
            'z': vertices[1][2],
        }
        v2 = {
            'x': vertices[2][0],
            'y': vertices[2][1],
            'z': vertices[2][2],
        }

        arestas = [
            {
                'ini': v0,
                'fim': v1,
                'taxa': (v1['x'] - v0['x']) / (v1['y'] - v0['y']),
                'taxaZ': (v1['z'] - v0['z']) / (v1['y'] - v0['y']),
            },
            {
                'ini': v1,
                'fim': v2,
                'taxa': (v2['x'] - v1['x']) / (v2['y'] - v1['y']),
                'taxaZ': (v2['z'] - v1['z']) / (v2['y'] - v1['y']),
            },
            {
                'ini': v2,
                'fim': v0,
                'taxa': (v0['x'] - v2['x']) / (v0['y'] - v2['y']),
                'taxaZ': (v0['z'] - v2['z']) / (v0['y'] - v2['y']),
            }
        ]
        swaped = False
        lastIniX, lastFimX = arestas[0]['ini']['x'], arestas[0]['ini']['x']
        for y in range(round(v0['y']), round(v1['y'])):
            lastIniX += arestas[0]['taxa']
            lastFimX += arestas[2]['taxa']
            intervalo = [lastIniX, lastFimX]

            if intervalo[1] < intervalo[0]:
                swaped = True
                intervalo[0], intervalo[1] = intervalo[1], intervalo[0]

            intervalo[0] = round(intervalo[0])
            intervalo[1] = round(intervalo[1])

            z = v0['z']
            varX = intervalo[1] - intervalo[0] + 1e-16
            deltaZ = (v1['z'] - v0['z']) / varX
            for j in range(intervalo[0], intervalo[1]):
                if j >= 0 and y >= 0 and j < self.width and y < self.height: 
                    if z > self.z_buffer[j, y]:
                        self.screen.set_at((j, y), color)
                        self.z_buffer[j,y] = z
                z += deltaZ

        swaped = False
        lastIniX = arestas[1]['ini']['x']

        for y in range(round(v1['y']), round(v2['y'])):
            lastIniX += arestas[1]['taxa']
            lastFimX += arestas[2]['taxa']
            intervalo = [lastIniX, lastFimX]

            if intervalo[1] < intervalo[0]:
                intervalo[0], intervalo[1] = intervalo[1], intervalo[0]
                swaped = True

            intervalo[0] = round(intervalo[0])
            intervalo[1] = round(intervalo[1])

            z = v1['z']
            varX = intervalo[1] - intervalo[0]
            deltaZ = (v2['z'] - v1['z']) / varX

            for j in range(intervalo[0], intervalo[1]):
                if j >= 0 and y >= 0 and j < self.width and y < self.height: 
                    if z > self.z_buffer[j, y]:
                        self.screen.set_at((j, y), color)
                        self.z_buffer[j,y] = z
                z += deltaZ


    def render(self):
        for obj_idx, o in enumerate(self.objetos):
            faces = o.get_faces_visible(self.camera_pos)
            # faces = o.get_faces()
            vertices = o.get_vertices()
            ones_column = np.ones((vertices.shape[0], 1))
            new_array = np.hstack((vertices, ones_column))

            vertices = self.create_objetos() @ new_array.T[:4]
            if not self.axis:
                vertices[[0, 1]] /= vertices[-1]
            # vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            vertices = vertices.T

            # vertices = np.array([
            #     [100,100, 32],
            #     [100,440,24],
            #     [200,200,23],
            #     [440,140,32]
            # ])
            # faces = []
            # faces.append(Face(vertices, [0,3,2]))
            # faces.append(Face(vertices, [0,1,2]))
            # faces.append(Face(vertices, [1,2,3])) # Esse aqui apresenta erro 
            for face_idx, face in enumerate(faces):
                s = np.array(self.camera_pos) - np.array(face.centroide)
                s = s/np.linalg.norm(s)
                cor = luz.calc_luz(s, face.centroide, face.normal, (0.2,0.3,0.4),(0.5,0.3,0.1),(0.2,0.3,0.1),(255,255,255),(255,255,255), (0,0,0), 3)
                # print(cor, s, face.normal, face.centroide)
                cor = np.array(cor).astype(int)
                # cor = (255,0,0)
                print(cor)
                self.fillpoli(face, vertices, cor)
                # self.fillpoly(face, vertices, (100//(face_idx+1), 200//(face_idx+1),  face_idx))
                # self.fillpoli(face, vertices, ())

            self.draw_vertices(vertices.T[:2].T)
            pg.display.flip()

    def draw_mouse_coords(self, screen, x, y):
        coord_text = f"X: {x}, Y: {y}"
        # text_surf = self.font.render(coord_text, True, (0, 255, 255))
        # print(coord_text)
        # screen.blit(text_surf, (10, 70))

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
            # self.screen.fill(pg.Color('darkslategray'))
            self.render()
            # self.draw_vertices()
            self.draw_mouse_coords(self.screen, mouse_x, mouse_y)
            self.draw_cam_coords(
                self.screen, self.camera_pos[0], self.camera_pos[1], self.camera_pos[2])
            self.draw_lookat_coords(
                self.screen, self.camera_lookat[0], self.camera_lookat[1], self.camera_lookat[2])

            pg.display.flip()
            clock.tick(24)  # Limita o loop a 60 frames por segundo

        pg.quit()


if __name__ == '__main__':
    polylines = [
        # (((1, 0), (-1, 1), (1, 1), (1, 0))),
        # (((100, 0), (-200, 200), (-100, -100), (100, 0)))
        # Novo objeto adicionado
        ((100, 100), (150, 100))
        # ((-10, 10), (10, 10))
    ]
    Cena3D().run()
