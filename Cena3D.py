import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from teste import Objeto3d, Face, render_poly
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

        self.camera_pos = [-20, 0, 0]
        self.camera_lookat = [0, 0, 0]

        pg.font.init()
        self.font = pg.font.SysFont(None, 36)

        self.__cores_faces = [[(random.uniform(0, 1), random.uniform(
            0, 1), random.uniform(0, 1)) for _ in obj.get_faces()] for obj in self.objetos]

    def create_objetos(self):
        self.camera = Camera(self.camera_pos, self.camera_lookat, (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(300)
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

    def draw_vertices(self, points):
        for obj_idx, o in enumerate(self.objetos):
            # faces = o.get_faces_visible(self.camera_pos)
            # faces = o.get_faces()

            # vertices = self.create_objetos() @ o.get_vertices().T
            # vertices[[0, 1]] /= vertices[-1]
            # # vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            # vertices = vertices.T
            # print(np.round(np.array(vertices), 1))
            # print(np.round(o.get_vertices(), 1))
            # print(np.array([f.vertices for f in faces ]))

            # for face_idx, face in enumerate(faces):
            #     points = vertices[face.vertices].T[:2].T.astype(int)

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

        lastIniX, lastFimX = arestas[0]['ini']['x'], arestas[0]['ini']['x']
        for y in range(round(v0['y']), round(v1['y'])):
            lastIniX += arestas[0]['taxa']
            lastFimX += arestas[2]['taxa']
            intervalo = [lastIniX, lastFimX]

            if intervalo[1] < intervalo[0]:
                intervalo[0], intervalo[1] = intervalo[1], intervalo[0]

            intervalo[0] = round(intervalo[0])
            intervalo[1] = round(intervalo[1])

            z = v0['z']
            varX = intervalo[1] - intervalo[0]
            deltaZ = (v1['z'] - v0['z']) / varX
            for j in range(intervalo[0], intervalo[1]):
                self.screen.set_at((j, y), color)
                z += deltaZ

        for y in range(round(v1['y']), round(v2['y'])):
            lastIniX += arestas[1]['taxa']
            lastFimX += arestas[2]['taxa']
            intervalo = [lastIniX, lastFimX]

            if intervalo[1] < intervalo[0]:
                intervalo[0], intervalo[1] = intervalo[1], intervalo[0]

            intervalo[0] = round(intervalo[0])
            intervalo[1] = round(intervalo[1])

            z = v1['z']
            varX = intervalo[1] - intervalo[0]
            deltaZ = (v2['z'] - v1['z']) / varX

            for j in range(intervalo[0], intervalo[1]):
                self.screen.set_at((j, y), color)
                z += deltaZ

    def render(self):
        for obj_idx, o in enumerate(self.objetos):
            faces = o.get_faces_visible(self.camera_pos)
            # faces = o.get_faces()
            vertices = o.get_vertices()
            ones_column = np.ones((vertices.shape[0], 1))
            new_array = np.hstack((vertices, ones_column))
            
            vertices = self.create_objetos() @ new_array.T[:4]
            vertices[[0, 1]] /= vertices[-1]
            # vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            vertices = vertices.T


            # vertices = [(100, 100, 23), (400, 300, -45), (200, 500, 23)]
            # bvertices = [(100, 100), (400, 300), (200, 500)]
            # z_values = [0.5, 0.3, 0.7]

            # Rasterizando o triângulo e atualizando os buffers
            # self.rasterize_triangle(
            #     bvertices, z_values, colors, self.z_buffer, cor_buffer)

            for face_idx, face in enumerate(faces):
                # vs = vertices[face.vertices][:2]
                # points = vertices[face.vertices].T[:2].T
                self.fillpoli(face, vertices,
                          (200//(2+1), 100//(3+1), 0))
                # self.fillpoli(face, vertices, ())
            # self.draw_vertices(bvertices)
            # pg.draw.polygon(self.screen, (255, 0, 255), bvertices)
            # pg.surfarray.blit_array(self.screen, cores)


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

    def rasterize_triangle(self, vertices, z_values, z_buffer=0, colors=0, color_buffer=0):
        # Ordena os vértices verticalmente
        sorted_vertices = sorted(vertices, key=lambda vertex: vertex[1])
    # Obtém os vértices ordenados
        v0, v1, v2 = sorted_vertices
        # Calcula os gradientes de profundidade (z) e cor
        dz_dx = [(v2[1] - v1[1]) * z_values[0] + (v1[0] - v2[0]) * z_values[2],
                 (v0[1] - v2[1]) * z_values[1] + (v2[0] - v0[0]) * z_values[2],
                 (v1[1] - v0[1]) * z_values[1] + (v0[0] - v1[0]) * z_values[0]]
        dc_dx = [(v2[1] - v1[1]) * colors[0] + (v1[0] - v2[0]) * colors[2],
                 (v0[1] - v2[1]) * colors[1] + (v2[0] - v0[0]) * colors[2],
                 (v1[1] - v0[1]) * colors[1] + (v0[0] - v1[0]) * colors[0]]

        # Determina a variação vertical de cada aresta
        dy_01 = v1[1] - v0[1]
        dy_12 = v2[1] - v1[1]
        dy_20 = v0[1] - v2[1]

        # Itera por cada scanline (linha de varredura)
        for y in range(int(v0[1]), int(v2[1]) + 1):
            # Determina a proporção da varredura entre os vértices
            alpha = (y - v0[1]) / dy_20 if dy_20 != 0 else 0
            beta = (y - v1[1]) / dy_01 if dy_01 != 0 else 0
            gamma = (y - v2[1]) / dy_12 if dy_12 != 0 else 0

            # Calcula os valores de profundidade (z) e cor para a linha de varredura
            z_start = v0[0] + alpha * (v2[0] - v0[0])
            z_end = v1[0] + beta * (v2[0] - v1[0])
            dz_dx_scan = z_start + (z_end - z_start) * (np.arange(v0[0], v1[0] + 1) - v0[0]) / (
                v1[0] - v0[0]) if v0[0] != v1[0] else np.full((v1[0] - v0[0] + 1), v1[0])

            c_start = v0[0] + alpha * (v2[0] - v0[0])
            c_end = v1[0] + beta * (v2[0] - v1[0])
            dc_dx_scan = c_start + (c_end - c_start) * (np.arange(v0[0], v1[0] + 1) - v0[0]) / (
                v1[0] - v0[0]) if v0[0] != v1[0] else np.full((v1[0] - v0[0] + 1), v1[0])

            # Itera por cada pixel na linha de varredura
            for x, z, color in zip(range(int(z_start), int(z_end) + 1), dz_dx_scan, dc_dx_scan):

                if x < self.width and y < self.height and x >= 0 and y >= 0:
                    try:
                        if z > self.z_buffer[y, x]:
                            self.z_buffer[y, x] = z
                            self.screen.set_at(((x, y)), (255, 0, 0))
                    except Exception as e:

                        print(e)
                        print(x, y, self.z_buffer.shape)
                        exit()

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
            # self.screen.fill(pg.Color('darkslategray'))
            self.render()
            # self.draw_vertices()
            self.draw_mouse_coords(self.screen, mouse_x, mouse_y)
            self.draw_cam_coords(
                self.screen, self.camera_pos[0], self.camera_pos[1], self.camera_pos[2])
            self.draw_lookat_coords(
                self.screen, self.camera_lookat[0], self.camera_lookat[1], self.camera_lookat[2])

            pg.display.flip()
            clock.tick(4)  # Limita o loop a 60 frames por segundo

        pg.quit()


if __name__ == '__main__':
    polylines = [
        # (((1, 0), (-1, 1), (1, 1), (1, 0))),
        # (((100, 0), (-200, 200), (-100, -100), (100, 0)))
        # Novo objeto adicionado
        ((100, 100), (150, 100))
        # ((-10, 10), (10, 10))
    ]
    Cena3D(polylines).run()
