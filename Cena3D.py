import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Objeto3d import Objeto3d, Face
import random
from camera import Camera, Projetion
from recorte2d import *
import luz
import traceback
import numpy as np


class Cena3D:
    def __init__(self, polylines=[((220, 400), (600, 200), (220, 400))]):
        self.objetos = [Objeto3d(p) for p in polylines]
        self.width = 800
        self.height = 800
        self.z_buffer = np.full((self.height, self.width), -float('inf'))
        self.cor_buffer = np.full((self.height, self.width, 3), (24, 24, 24))
        for obj in self.objetos:
            obj.rotacaoX(4)
        self.axis = True
        self.camera_pos = [-10, 0, 0]
        self.camera_lookat = [0, 0, 0]
        pg.font.init()
        self.font = pg.font.SysFont(None, 36)

    def create_objetos(self):
        self.camera = Camera(self.camera_pos, self.camera_lookat, (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(10)
        if self.axis:
            self.projetion = np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
        self.to_screen = Projetion().to_screen(-self.width//2, self.width//2, -
                                               self.height//2, self.height//2, 0, self.width, 0, self.height)

        return self.to_screen @ self.projetion @ self.camera.camera_matrix()

    def draw_vertices(self, points=[]):
        for p in points:
            pg.draw.circle(self.screen, (255, 255, 255), p, 3)

    def constante(self, face, all_vertices, color):
        vertices = all_vertices[face.vertices]
        vertices = sorted(vertices, key=lambda v: v[1])
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
                if j >= 0 and y >= 0 and j < self.z_buffer.shape[0] and y < self.height:
                    if z > self.z_buffer[j, y]:
                        self.screen.set_at((j, y), color)
                        self.z_buffer[j, y] = z
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
                if j >= 0 and y >= 0 and j < self.z_buffer.shape[0] and y < self.height:
                    if z > self.z_buffer[j, y]:
                        self.screen.set_at((j, y), color)
                        self.z_buffer[j, y] = z
                z += deltaZ

    def gouraud(self, all_vertices, cor_v0, cor_v1, cor_v2):
        vertices = all_vertices
        vertices = sorted(vertices, key=lambda v: v[1])

        v0 = {
            'x': vertices[0][0],
            'y': vertices[0][1],
            'z': vertices[0][2],
            'color': cor_v0
        }
        v1 = {
            'x': vertices[1][0],
            'y': vertices[1][1],
            'z': vertices[1][2],
            'color': cor_v1
        }
        v2 = {
            'x': vertices[2][0],
            'y': vertices[2][1],
            'z': vertices[2][2],
            'color': cor_v2
        }

        arestas = [
            {
                'ini': v0,
                'fim': v1,
                'taxa': (v1['x'] - v0['x']) / (v1['y'] - v0['y']),
                'taxaZ': (v1['z'] - v0['z']) / (v1['y'] - v0['y']),
                'taxaColor': [(v1['color'][i] - v0['color'][i]) / (v1['y'] - v0['y']) for i in range(3)]
            },
            {
                'ini': v1,
                'fim': v2,
                'taxa': (v2['x'] - v1['x']) / (v2['y'] - v1['y']),
                'taxaZ': (v2['z'] - v1['z']) / (v2['y'] - v1['y']),
                'taxaColor': [(v2['color'][i] - v1['color'][i]) / (v2['y'] - v1['y']) for i in range(3)]
            },
            {
                'ini': v2,
                'fim': v0,
                'taxa': (v0['x'] - v2['x']) / (v0['y'] - v2['y']),
                'taxaZ': (v0['z'] - v2['z']) / (v0['y'] - v2['y']),
                'taxaColor': [(v0['color'][i] - v2['color'][i]) / (v0['y'] - v2['y']) for i in range(3)]
            }
        ]

        swaped = False
        lastIniX, lastFimX = arestas[0]['ini']['x'], arestas[0]['ini']['x']
        color_ini = v0['color'][:]
        color_fim = v0['color'][:]

        for y in range(round(v0['y']), round(v1['y'])):
            lastIniX += arestas[0]['taxa']
            lastFimX += arestas[2]['taxa']
            color_ini = [color_ini[i] + arestas[0]['taxaColor'][i]
                         for i in range(3)]
            color_fim = [color_fim[i] + arestas[2]['taxaColor'][i]
                         for i in range(3)]
            
            intervalo = [lastIniX, lastFimX]
            tempColorIni = color_ini[:]
            tempColorFim = color_fim[:]
            
            if intervalo[1] < intervalo[0]:
                swaped = True
                intervalo[0], intervalo[1] = intervalo[1], intervalo[0]
                tempColorIni, tempColorFim = tempColorFim, tempColorIni

            intervalo[0] = round(intervalo[0])
            intervalo[1] = round(intervalo[1])

            z = v0['z']
            varX = intervalo[1] - intervalo[0] + 1e-16
            deltaZ = (v1['z'] - v0['z']) / varX
            color_step = [(tempColorFim[i] - tempColorIni[i]) / varX for i in range(3)]

            current_color = tempColorIni[:]

            for j in range(intervalo[0], intervalo[1]):
                if z > self.z_buffer[j, y]:
                    try:
                        # self.screen.set_at((j, y), tuple(map(int, current_color)))
                        self.cor_buffer[j, y] = current_color
                        # print(y,current_color)
                    except:
                        print(y, np.array(current_color).astype(int), traceback.format_exc())
                        exit()
                    self.z_buffer[j, y] = z
                z += deltaZ
                current_color = [current_color[i] + color_step[i] for i in range(3)]

        if not swaped:
            lastIniX = arestas[1]['ini']['x']
            color_ini = v1['color'][:]

        for y in range(round(v1['y']), round(v2['y'])):
            lastIniX += arestas[1]['taxa']
            lastFimX += arestas[2]['taxa']
            color_ini = [color_ini[i] + arestas[1]['taxaColor'][i]
                         for i in range(3)]
            color_fim = [color_fim[i] + arestas[2]['taxaColor'][i]
                         for i in range(3)]

            intervalo = [lastIniX, lastFimX]
            tempColorIni = color_ini[:]
            tempColorFim = color_fim[:]
            if intervalo[1] < intervalo[0]:
                intervalo[0], intervalo[1] = intervalo[1], intervalo[0]
                # color_ini, color_fim = color_fim, color_ini
                tempColorIni, tempColorFim = tempColorFim, tempColorIni
                swaped = True

            intervalo[0] = round(intervalo[0])
            intervalo[1] = round(intervalo[1])

            z = v1['z']
            varX = intervalo[1] - intervalo[0]
            deltaZ = (v2['z'] - v1['z']) / varX
            color_step = [(tempColorFim[i] - tempColorIni[i]) / varX for i in range(3)]

            current_color = tempColorIni[:]
            for j in range(intervalo[0], intervalo[1]):
                if z > self.z_buffer[j, y]:
                    try:
                        # self.screen.set_at((j, y), np.array(current_color).astype(int))
                        self.cor_buffer[j, y] = current_color
                        # print(y,current_color)
                    except Exception as e:
                        print(y, np.array(current_color).astype(int), traceback.format_exc())
                        exit()

                    self.z_buffer[j, y] = z

                z += deltaZ
                current_color = [current_color[i] + color_step[i] for i in range(3)]

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
            # faces.append(Face(vertices, [2,1,3]))
            # faces.append(Face(vertices, [0,1,2]))
            # faces.append(Face(vertices, [0,1,2]))
            # faces.append(Face(vertices, [1,2,3])) # Esse aqui apresenta erro
            for face_idx, face in enumerate(faces):

                o.calc_normais_vertices()
                vet_norm1, vet_norm2, vet_norm3 = [
                    o.normais_vetores[i] for i in face.vertices]
                v1, v2, v3 = vertices[face.vertices]

                s1 = np.array(self.camera_pos) - np.array(v1[:3])
                s1 = s1/np.linalg.norm(s1)
                s2 = np.array(self.camera_pos) - np.array(v2[:3])
                s2 = s2/np.linalg.norm(s2)
                s3 = np.array(self.camera_pos) - np.array(v3[:3])
                s3 = s3/np.linalg.norm(s3)

                cor1 = luz.calc_luz(s1, v1[:3], vet_norm1, (0.2, 0.3, 0.4), (0.5, 0.3, 0.1), (
                    0.2, 0.3, 0.1), (255, 255, 255), (255, 255, 255), (0, 0, 0), 3)
                cor2 = luz.calc_luz(s2, v2[:3], vet_norm2, (0.2, 0.3, 0.4), (0.5, 0.3, 0.1), (
                    0.2, 0.3, 0.1), (255, 255, 255), (255, 255, 255), (0, 0, 0), 3)
                cor3 = luz.calc_luz(s3, v3[:3], vet_norm3, (0.2, 0.3, 0.4), (0.5, 0.3, 0.1), (
                    0.2, 0.3, 0.1), (255, 255, 255), (255, 255, 255), (0, 0, 0), 3)

                cor1 = np.array(cor1).astype(int)
                cor2 = np.array(cor2).astype(int)
                cor3 = np.array(cor3).astype(int)

                s = np.array(self.camera_pos) - np.array(face.centroide)
                s = s/np.linalg.norm(s)

                cor = luz.calc_luz(s, face.centroide, face.normal, (0.2, 0.3, 0.4), (0.5, 0.3, 0.1), (
                    0.2, 0.3, 0.1), (255, 255, 255), (255, 255, 255), self.camera_pos, 3)
                
                cor = np.array(cor).astype(int)

                # cor1 = (255, 0, 0)
                # cor2 = (0, 255, 0)
                # cor3 = (0, 0, 255)
                # cor = cor1

                clip_face, clip_face_colors = sutherland_hodgman_clip(
                    vertices[face.vertices], [cor1, cor2, cor3], 0, 0, self.width-1, self.height)
                
                # print(clip_face)
                if len(clip_face) > 0:
                    triangles, triangles_colors = triangulate_convex_polygon(clip_face, clip_face_colors)

                    for t, tc in zip(triangles, triangles_colors):
                        self.gouraud(t, tc[0], tc[1], tc[2])
                    
                    # self.gouraud(t, cor, cor, cor)
                # self.fillpoli(face, vertices, cor)
                # self.constante(face, vertices, cor)
        surf = pg.surfarray.make_surface(self.cor_buffer)
        self.screen.blit(surf, (0, 0))
        self.draw_vertices(vertices.T[:2].T)
        pg.display.flip()
        self.cor_buffer = np.full((self.height, self.width, 3), (24, 24, 24))
        self.z_buffer = np.full((self.height, self.width), -float('inf'))
        # pg.display.flip()


    def draw_button(self, screen, rect, text, color):
        pg.draw.rect(screen, color, rect)
        text_surf = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)


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
        self.screen = pg.display.set_mode(size, display=0)
        clock = pg.time.Clock()

        button_pespctiva = pg.Rect(50,50,100,50)

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    if button_pespctiva.collidepoint(mouse_pos):
                        self.axis = not self.axis
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
                    elif event.key == pg.K_q:
                        self.camera_pos[0] -= 1
                    elif event.key == pg.K_e:
                        self.camera_pos[0] += 1
                    elif event.key == pg.K_d:
                        self.camera_pos[2] += 1
                    elif event.key == pg.K_a:
                        self.camera_pos[2] -= 1
                    elif event.key == pg.K_w:
                        self.camera_pos[1] += 1
                    elif event.key == pg.K_s:
                        self.camera_pos[1] -= 1
                    elif event.key == pg.K_UP:
                        self.camera_lookat[1] += 1
                    elif event.key == pg.K_DOWN:
                        self.camera_lookat[1] -= 1
                    elif event.key == pg.K_LEFT:
                        self.camera_lookat[2] -= 1
                    elif event.key == pg.K_RIGHT:
                        self.camera_lookat[2] += 1

            self.draw_button(self.screen, button_pespctiva, 'Pespctiva', (155,100,100))
            

                # Obtém a posição atual do mouse
            mouse_x, mouse_y = pg.mouse.get_pos()

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
        ((100, 100), (150, 100), (200, 200)),
        ((-10, 10), (10, 10))
    ]
    cena = Cena3D(polylines)
    cena.run()
