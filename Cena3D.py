import pygame as pg
import pygame_menu as pgm
from pygame.locals import *
from Objeto3d import Objeto3d, Face
from camera import Camera, Projetion
from recorte2d import *
import luz
import traceback
import numpy as np
import warnings


warnings.filterwarnings("ignore", category=RuntimeWarning)



class Cena3D:
    def __init__(self, polylines=[((220, 400), (600, 200), (220, 400))]):
        self.objetos = [Objeto3d(p) for p in polylines]
        self.width = 800
        self.height = 800
        self.dimensions = [-self.width//2, self.width//2, -self.height//2, self.height//2, 0, self.width, 0, self.height]
        self.z_buffer = np.full((self.height, self.width), -float('inf'))
        self.cor_buffer = np.full((self.height, self.width, 3), (24, 24, 24))
        self.rotacoes = 4
        for obj in self.objetos:
            obj.create(self.rotacoes)
        self.axis = False
        self.luz_pos = [0,0,0]
        self.luz_prop = [255,255,255]
        self.luz_ambiente = [255,255,255]
        self.plano_proj = 200
        self.camera_pos = [-15, 0, 0]
        self.camera_lookat = [0, 0, 0]
        self.current_shader = 'constante'
        self.is_wireframe = False
        self.is_menu_open = False
        self.selected_obj = 1
        self.controling_obj = False
        pg.font.init()
        self.font = pg.font.SysFont(None, 20)

    def create_objetos(self):
        # near = 0.1
        # far = 1000
        # z_min = near/far

        # recort3d = np.identity(4)
        
        self.camera = Camera(self.camera_pos, self.camera_lookat, (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(self.plano_proj)
        if self.axis:
            self.projetion = np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])
            # recort3d = np.array([  
            #         [1, 0, 0, 0],
            #         [0, 1, 0, 0],
            #         [0, 0, 1/(1+z_min), -z_min/(1+z_min)],
            #         [0, 0, -1, 0]
            #         ])
        
        self.to_screen = Projetion().to_screen(self.dimensions[0], self.dimensions[1], self.dimensions[2], self.dimensions[3], self.dimensions[4], self.dimensions[5], self.dimensions[6], self.dimensions[7])

        return  self.to_screen @ self.projetion @ self.camera.camera_matrix()

    def draw_vertices(self, points=[]):
        for p in points:
            pg.draw.circle(self.screen, (255, 255, 255), p, 3)

    def constante(self, face, all_vertices, color):
        vertices = all_vertices
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
                # if j >= 0 and y >= 0 and j < self.z_buffer.shape[0] and y < self.height:
                try:
                    if 0 <= j < self.dimensions[5] and 0 <= y < self.dimensions[7] and z > self.z_buffer[y, j]:
                        self.cor_buffer[y, j] = color
                        self.z_buffer[y, j] = z
                except:
                    print(j,y)
                    exit()
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
                # if j >= 0 and y >= 0 and j < self.z_buffer.shape[0] and y < self.height:
                if 0 <= j < self.width and 0 <= y < self.height and z > self.z_buffer[y, j]:
                    # self.screen.set_at((j, y), color)
                    self.z_buffer[y, j] = z
                    self.cor_buffer[y, j] = color
                z += deltaZ

    def gouraud(self, all_vertices, cor_v0, cor_v1, cor_v2):

        vertices_with_colors = [
            {'vertex': all_vertices[0], 'color': cor_v0},
            {'vertex': all_vertices[1], 'color': cor_v1},
            {'vertex': all_vertices[2], 'color': cor_v2}
        ]

        # Sort vertices based on the y-coordinate
        vertices_with_colors = sorted(vertices_with_colors, key=lambda vc: vc['vertex'][1])

        # Extract sorted vertices and their colors
        v0 = {
            'x': vertices_with_colors[0]['vertex'][0],
            'y': vertices_with_colors[0]['vertex'][1],
            'z': vertices_with_colors[0]['vertex'][2],
            'color': vertices_with_colors[0]['color']
        }
        v1 = {
            'x': vertices_with_colors[1]['vertex'][0],
            'y': vertices_with_colors[1]['vertex'][1],
            'z': vertices_with_colors[1]['vertex'][2],
            'color': vertices_with_colors[1]['color']
        }
        v2 = {
            'x': vertices_with_colors[2]['vertex'][0],
            'y': vertices_with_colors[2]['vertex'][1],
            'z': vertices_with_colors[2]['vertex'][2],
            'color': vertices_with_colors[2]['color']
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
                if 0 <=j < self.width and 0 <= y < self.height and z > self.z_buffer[y, j]:
                    try:
                            # self.screen.set_at((j, y), tuple(map(int, current_color)))
                            self.cor_buffer[y, j] = current_color
                        # print(y,current_color)
                    except:
                        print(y, np.array(current_color).astype(int), traceback.format_exc())
                        exit()
                    self.z_buffer[y, j] = z
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
                if 0 <= j < self.width and 0 <= y < self.height and z > self.z_buffer[y, j]:
                    try:
                        # self.screen.set_at((j, y), np.array(current_color).astype(int))
                        self.cor_buffer[y, j] = current_color
                        # print(y,current_color)
                    except Exception as e:
                        print(y, np.array(current_color).astype(int), traceback.format_exc())
                        exit()

                    self.z_buffer[y, j] = z

                z += deltaZ
                current_color = [current_color[i] + color_step[i] for i in range(3)]

    def phong(self, s, l_unit, all_vertices, vetor_v0, vetor_v1, vetor_v2, obj):
        
        vertices_with_colors = [
            {'vertex': all_vertices[0], 'color': vetor_v0},
            {'vertex': all_vertices[1], 'color': vetor_v1},
            {'vertex': all_vertices[2], 'color': vetor_v2}
        ]

        # Sort vertices based on the y-coordinate
        vertices_with_colors = sorted(vertices_with_colors, key=lambda vc: vc['vertex'][1])

        # Extract sorted vertices and their colors
        v0 = {
            'x': vertices_with_colors[0]['vertex'][0],
            'y': vertices_with_colors[0]['vertex'][1],
            'z': vertices_with_colors[0]['vertex'][2],
            'color': vertices_with_colors[0]['color']
        }
        v1 = {
            'x': vertices_with_colors[1]['vertex'][0],
            'y': vertices_with_colors[1]['vertex'][1],
            'z': vertices_with_colors[1]['vertex'][2],
            'color': vertices_with_colors[1]['color']
        }
        v2 = {
            'x': vertices_with_colors[2]['vertex'][0],
            'y': vertices_with_colors[2]['vertex'][1],
            'z': vertices_with_colors[2]['vertex'][2],
            'color': vertices_with_colors[2]['color']
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
                if 0 <= j < self.width and 0 <= y < self.height and z > self.z_buffer[y, j]:
                    try:
                        n = current_color/np.linalg.norm(current_color)
                        cor = luz.calc_luz_phong(s, l_unit ,n, obj.material_a, obj.material_d, obj.material_s, self.luz_ambiente, self.luz_prop, obj.index_reflex)
                        self.cor_buffer[y, j] = cor
                    except:
                        print(y, np.array(current_color).astype(int), traceback.format_exc())
                        exit()
                    self.z_buffer[y, j] = z
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
                if 0 <=j < self.width and 0 <= y < self.height and z > self.z_buffer[y, j]:
                    try:
                        n = current_color/np.linalg.norm(current_color)
                        cor = luz.calc_luz_phong(s, l_unit, n, obj.material_a, obj.material_d, obj.material_s, self.luz_ambiente, self.luz_prop, obj.index_reflex)
                        self.cor_buffer[y, j] = cor
                    except Exception as e:
                        print(y, np.array(current_color).astype(int), traceback.format_exc())
                        exit()

                    self.z_buffer[y, j] = z

                z += deltaZ
                current_color = [current_color[i] + color_step[i] for i in range(3)]


    def render(self):
        for obj_idx, o in enumerate(self.objetos):
            faces = o.get_faces_visible(self.camera_pos)
            # faces = o.get_faces()
            vertices = o.get_vertices()
            # ones_column = np.ones((vertices.shape[0], 1))
            # new_array = np.hstack((vertices, ones_column)).T
            vertices = self.create_objetos() @ vertices.T
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
                vet_norm1, vet_norm2, vet_norm3 = [o.normais_vetores[i] for i in face.vertices]
                v1, v2, v3 = vertices[face.vertices]

                s1 = np.array(self.camera_pos) - np.array(v1[:3])
                s1 = s1/np.linalg.norm(s1)
                s2 = np.array(self.camera_pos) - np.array(v2[:3])
                s2 = s2/np.linalg.norm(s2)
                s3 = np.array(self.camera_pos) - np.array(v3[:3])
                s3 = s3/np.linalg.norm(s3)

                cor1 = luz.calc_luz(s1, v1[:3], vet_norm1, o.material_a, o.material_d, o.material_s, self.luz_ambiente, self.luz_prop, self.luz_pos, o.index_reflex)
                cor2 = luz.calc_luz(s2, v2[:3], vet_norm2, o.material_a, o.material_d, o.material_s, self.luz_ambiente, self.luz_prop, self.luz_pos, o.index_reflex)
                cor3 = luz.calc_luz(s3, v3[:3], vet_norm3, o.material_a, o.material_d, o.material_s, self.luz_ambiente, self.luz_prop, self.luz_pos, o.index_reflex)

                cor1 = np.array(cor1).astype(int)
                cor2 = np.array(cor2).astype(int)
                cor3 = np.array(cor3).astype(int)

                s = np.array(self.camera_pos) - np.array(face.centroide)
                s = s/np.linalg.norm(s)

                cor = luz.calc_luz(s, face.centroide, face.normal, o.material_a, o.material_d, o.material_s, self.luz_ambiente, self.luz_prop, self.luz_pos, o.index_reflex)
        
                cor = np.array(cor).astype(int)

                clip_face, clip_face_colors = sutherland_hodgman_clip(
                    vertices[face.vertices], [cor1, cor2, cor3], self.dimensions[4], self.dimensions[6], self.dimensions[5], self.dimensions[7])
                if len(clip_face) > 0:
                    triangles, triangles_colors = triangulate_convex_polygon(clip_face, clip_face_colors)

                    luz_pos = np.array(self.luz_pos)
                    point = np.array(face.centroide)
                    L = luz_pos - point
                    l_unit = L/np.linalg.norm(L)      
                    


                    for t, tc in zip(triangles, triangles_colors):
                        if self.current_shader == 'constante':
                            self.constante(face, t, cor)
                        elif self.current_shader == 'gouraud':
                            self.gouraud(t, tc[0], tc[1], tc[2])
                        elif self.current_shader == 'phong':
                            self.phong(s, l_unit ,t, tc[0], tc[1], tc[2], o)
                    


        surf = pg.surfarray.make_surface(self.cor_buffer)
        self.screen.blit(surf, (0, 0))
        # self.draw_vertices(vertices.T[:2].T)
        pg.display.flip()
        self.cor_buffer = np.full((self.dimensions[7], self.dimensions[5], 3), (24, 24, 24))
        self.z_buffer = np.full((self.dimensions[7], self.dimensions[5]), -float('inf'))



    def wireframe(self):

        self.screen.fill((24,24,24))
        for obj_idx, o in enumerate(self.objetos):
            faces = o.get_faces_visible(self.camera_pos)
            # faces = o.get_faces()
            vertices = o.get_vertices()
            # ones_column = np.ones((vertices.shape[0], 1))
            # new_array = np.hstack((vertices, ones_column))

            vertices = self.create_objetos() @ vertices.T[:4]
            if not self.axis:
                vertices[[0, 1]] /= vertices[-1]
            # vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            vertices = np.array(vertices[:2].T).astype(int)

            for face_idx, face in enumerate(faces):
                pg.draw.polygon(self.screen, (255,200,0), vertices[face.vertices], width=1)
             
        # pg.display.flip()



    def draw_button(self, screen, rect, text, color):
        pg.draw.rect(screen, color, rect)
        text_surf = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def draw_cam_coords(self, screen, x, y, z):
        coord_text = f"X: {x}, Y: {y}, Z: {z}"
        text_surf = self.font.render(coord_text, True, (100, 100, 100))
        screen.blit(text_surf, (10, 10))

    def draw_lookat_coords(self, screen, x, y, z):
        coord_text = f"X: {x}, Y: {y}, Z: {z}"
        text_surf = self.font.render(coord_text, True, (100, 100, 200))
        screen.blit(text_surf, (10, 30))

    def draw_render_options(self, screen): 
        text = '1 - Constante | 2 - Gouraud | 3 - Phong | P - Alternar Perspectiva | M - Alternar Wireframe'
        text_surf = self.font.render(text, True, (100, 100, 100))
        screen.blit(text_surf, (150, 10))
    

    def run(self):
        pg.init()
        size = (self.width, self.height)
        self.screen = pg.display.set_mode(size, display=0)
        clock = pg.time.Clock()

        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    return 'QUIT', 1
                elif event.type == pg.VIDEORESIZE:
                    self.is_menu_open = True
                    self.width = event.w
                    self.height = event.h
                    self.dimensions = [self.dimensions[0], self.dimensions[1], self.dimensions[2], self.dimensions[3],
                                        0,event.w,0,event.h]
                    self.z_buffer = np.full(
                        (self.height, self.width), -float('inf'))
                    self.cor_buffer = np.full(
                        (self.height, self.width, 3), (24, 24, 24))

                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.is_menu_open = not self.is_menu_open
                    elif event.key == pg.K_l:
                        return '2D', 2
                    elif event.key == pg.K_1:
                        self.current_shader = 'constante'
                    elif event.key == pg.K_2:
                        self.current_shader = 'gouraud'
                    elif event.key == pg.K_3:
                        self.current_shader = 'phong'
                    elif event.key == pg.K_p:
                        self.axis = not self.axis
                    elif event.key == pg.K_m:
                        self.is_wireframe = not self.is_wireframe
                    elif self.controling_obj:
                        obj = self.objetos[self.selected_obj]
                        objPos = obj.get_centro_box_envolvente()
                        if event.key == pg.K_q:
                            obj.translado((-10, 0, 0))
                        elif event.key == pg.K_e:
                            obj.translado((10, 0, 0))
                        elif event.key == pg.K_d:
                            obj.translado((0, 0, -10))
                        elif event.key == pg.K_a:
                            obj.translado((0, 0, 10))
                        elif event.key == pg.K_w:
                            obj.translado((0, 10, 0))
                        elif event.key == pg.K_s:
                            obj.translado((0, -10, 0))
                        elif event.key == pg.K_UP:
                            obj.internal_rotate(6, 'X')
                        elif event.key == pg.K_DOWN:
                            obj.internal_rotate(-6, 'X')
                        elif event.key == pg.K_LEFT:
                            obj.internal_rotate(6, 'Y')
                        elif event.key == pg.K_RIGHT:
                            obj.internal_rotate(-6, 'Y')
                        elif event.key == pg.K_z:
                            obj.internal_rotate(6, 'Z')
                        elif event.key == pg.K_x:
                            obj.internal_rotate(-6, 'Z')
                    else:
                        if event.key == pg.K_q:
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

            
        # Define a posição onde o texto será renderizado
            # self.screen.fill(pg.Color('darkslategray'))j

            if self.is_menu_open:
                settings_menu_theme = pgm.themes.THEME_DARK.copy()
                settings_menu_theme.title_offset = (5, -2)
                settings_menu_theme.widget_alignment = pgm.locals.ALIGN_LEFT
                settings_menu_theme.widget_font_size = 20
                menu = pgm.Menu(
                    theme=settings_menu_theme,
                    title='Configuração',
                    width=self.width,
                    height=self.height
                )

                def setSizes(text):
                    try:
                        self.dimensions = [int(x) for x in text.strip('[]').split(',')]
                        self.cor_buffer = np.full((self.dimensions[7], self.dimensions[5], 3), (24, 24, 24))
                        self.z_buffer = np.full((self.dimensions[7], self.dimensions[5]), -float('inf'))
                    except ValueError:
                        print('Erro ao parse a string de tamanho da tela.')

                menu.add.text_input(
                    'Tamanho tela: ',
                    default=self.dimensions.__str__(),
                    onchange= setSizes
                )

                def setProj(num):
                    self.plano_proj = int(num)

                menu.add.text_input(
                    'Dist Proj: ',
                    default=self.plano_proj,
                    maxchar=3,
                    maxwidth=3,
                    input_type=pgm.locals.INPUT_INT,
                    onchange= setProj
                )

                def setLuzPos(text):
                    try:
                        self.luz_pos = [int(x) for x in text.strip('[]').split(',')]
                    except ValueError:
                        print('Erro ao parse a string de luz position.')

                menu.add.text_input(
                    title='Pos_Luz= ',
                    default=self.luz_pos.__str__(),
                    onreturn= setLuzPos
                )

                def setLuzColor(color):
                    try:
                        self.luz_prop = color
                    except ValueError:
                        print('Erro ao parse a string de luz color.')

                menu.add.color_input(
                    title='Cor_Luz= ',
                    color_type='rgb',
                    default=tuple(self.luz_prop),
                    onchange= setLuzColor
                )

                def setLuzAmbColor(color):
                    try:
                        self.luz_ambiente = color
                    except ValueError:
                        print('Erro ao parse a string de luz ambiente.')

                menu.add.color_input(
                    title='Luz_Amb= ',
                    color_type='rgb',
                    default=tuple(self.luz_ambiente),
                    onchange= setLuzAmbColor
                )

                #------------------------

                items = [str(i) for i in range(len(self.objetos))]
                
                def selectObj(text):
                    self.selected_obj = text[1]
                
                menu.add.selector(
                    'Selecione o obj:\t',
                    items,
                    default=self.selected_obj,
                    onchange=selectObj
                )
                
                def setRotacoes(num):
                    try:
                        self.rotacoes = int(num)
                        self.objetos[self.selected_obj].create(int(num))
                    except:
                        pass
                menu.add.text_input(
                    'Rotacoes: ',
                    default=self.objetos[self.selected_obj].rotacoes,
                    maxchar=3,
                    maxwidth=3,
                    input_type=pgm.locals.INPUT_INT,
                    cursor_selection_enable=False,
                    onchange= setRotacoes
                )

                def setMatAmbColor(text):
                    try:
                        self.objetos[self.selected_obj].material_a = [float(x) for x in text.strip('[]').split(',')]
                    except ValueError:
                        print('Erro ao parse a string de mat ambiente.')

                menu.add.text_input(
                    title='Mat_Amb= ',
                    default=(self.objetos[self.selected_obj].material_a).__str__(),
                    onchange=setMatAmbColor
                )

                def setMatDifColor(text):
                    try:
                        self.objetos[self.selected_obj].material_d = [float(x) for x in text.strip('[]').split(',')]
                    except ValueError:
                        print('Erro ao parse a string de mat dif.')

                menu.add.text_input(
                    title='Mat_Dif= ',
                    default=(self.objetos[self.selected_obj].material_d).__str__(),
                    onchange=setMatDifColor
                )

                def setMatSpecColor(text):
                    try:
                        self.objetos[self.selected_obj].material_s = [float(x) for x in text.strip('[]').split(',')]
                    except ValueError:
                        print('Erro ao parse a string de mat spec.')

                menu.add.text_input(
                    title='Mat_Spec= ',
                    default=(self.objetos[self.selected_obj].material_s).__str__(),
                    onchange=setMatSpecColor
                )

                def setMatReflex(text):
                    try:
                        self.objetos[self.selected_obj].index_reflex = float(text)
                    except ValueError:
                        print('Erro ao parse a string de mat spec.')

                menu.add.text_input(
                    title='Reflex= ',
                    default=(self.objetos[self.selected_obj].index_reflex).__str__(),
                    onchange=setMatReflex
                )

                def setMatscaler(text):
                    try:
                        self.objetos[self.selected_obj].scale(float(text))
                    except ValueError:
                        print('Erro ao parse a string de fator.')

                menu.add.text_input(
                    title='Fator escala= ',
                    default='1',
                    onchange=setMatscaler
                )

                

                def controlObj():
                    self.controling_obj = True
                    self.is_menu_open = False
                    menu.disable()
                menu.add.button('Controlar objeto', controlObj)

                def quit():
                    self.controling_obj = False
                    self.is_menu_open = False
                    menu.disable()
                    # pgm.events.EXIT
                menu.add.button('Sair', quit)

                menu.mainloop(self.screen)
            else:
                if self.is_wireframe:
                    self.wireframe()
                else:
                    self.render()
                # self.draw_vertices()
                self.draw_cam_coords(
                    self.screen, self.camera_pos[0], self.camera_pos[1], self.camera_pos[2])
                self.draw_lookat_coords(
                    self.screen, self.camera_lookat[0], self.camera_lookat[1], self.camera_lookat[2])
                self.draw_render_options(self.screen)


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
