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
    def __init__(self, polylines=[((0, 10), (10, 10))]):
        self.objetos = [Objeto3d(p) for p in polylines]
        for obj in self.objetos:
            obj.rotacaoX(36)

        self.cores_faces = [[(random.uniform(0, 1), random.uniform(
            0, 1), random.uniform(0, 1)) for _ in obj.get_faces()] for obj in self.objetos]

    def create_objetos(self):
        self.camera = Camera((3, 3, 0), (0, 0, 0), (0, 0, 1))
        self.projetion = Projetion().projetion_matrix(50)
        self.to_screen = Projetion().to_screen(0, 800, 0, 600, 0, 800, 0, 600)
        return self.to_screen @ self.projetion @ self.camera.camera_matrix()

    def draw_axes(self):
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(1000, 0, 0)
        glEnd()

        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1000, 0)
        glEnd()

        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 1000)
        glEnd()

    def draw_wireframe(self):
        glBegin(GL_LINES)
        glColor3f(1.0, 0.5, 0.0)
        for i, faces in enumerate(self.faces):
            for face in faces:
                f = Face(self.vertices[i], face)
                if f.is_visible((1, 10, 0)):
                    for vertex in face:
                        glVertex3fv(self.vertices[i][vertex])
        glEnd()

    def draw_triangles(self):
        glBegin(GL_TRIANGLES)
        for i, faces in enumerate(self.faces):
            for j, face in enumerate(faces):
                f = Face(self.vertices[i], face)
                if f.is_visible((1, 10, 0)):
                    glColor3f(*self.cores_faces[i][j])
                    for vertex in face:
                        glVertex3fv(self.vertices[i][vertex])
        glEnd()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_axes()
        self.render()
        pg.display.flip()

    def fillpoly(self, face, all_vertices):
        i_vertices = face.vertices
        vertices = sorted(all_vertices[[i_vertices]], key=lambda v: v[1])[0]

        # Test data
        x1, y1, z1 = 93, 251, -22.807
        x2, y2, z2 = 198, 241, -20.129
        x3, y3, z3 = 125, 107, -21.815

        # Calculate inverse slope coefficients for edges
        tx21 = (x2 - x1) / (y2 - y1) if (y2 - y1) != 0 else 0
        tx31 = (x3 - x1) / (y3 - y1) if (y3 - y1) != 0 else 0
        tx32 = (x3 - x2) / (y3 - y2) if (y3 - y2) != 0 else 0

        tz21 = (z2 - z1) / (y2 - y1) if (y2 - y1) != 0 else 0
        tz31 = (z3 - z1) / (y3 - y1) if (y3 - y1) != 0 else 0
        tz32 = (z3 - z2) / (y3 - y2) if (y3 - y2) != 0 else 0

        height = 300
        width = 400
        z_buffer = np.full((width, height), -float('inf'))
        cor_buffer = np.full((width, height, 3), [24, 24, 24], dtype=np.uint8)

        aresta1 = np.full((height, 2), 0.0)
        aresta2 = np.full((height, 2), 0.0)
        aresta3 = np.full((height, 2), 0.0)

        # Filling edges with vertices data
        x, z = float(x3), float(z3)
        for i in range(y3, y1):
            aresta1[i] = [x, z]
            x += tx31
            z += tz31

        x, z = float(x3), float(z3)
        for i in range(y3, y2):
            aresta2[i] = [x, z]
            x += tx32
            z += tz32

        x, z = float(x2), float(z2)
        for i in range(y2, y1):
            aresta3[i] = [x, z]
            x += tx21
            z += tz21

        # Fill the polygon
        for y in range(y3, y1):
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
                    if x >= 0 and y >= 0 and x < width and y < height:
                        if z > z_buffer[x, y]:
                            z_buffer[x, y] = z
                            cor_buffer[x, y] = [255, 0, 255] 
                    z += dz

        return cor_buffer

    def render(self):
        for o in self.objetos:
            faces = o.get_faces_visible((1, -1, 0))
            vertices = self.create_objetos() @ o.get_vertices().T
            vertices[[0, 1]] /= vertices[-1]
            vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            vertices = vertices.T

            cores = self.fillpoly(faces[0], vertices)
            for y, linha in enumerate(cores):
                for x, pixel in enumerate(linha):
                    self.screen.set_at((x, y), (pixel[0], pixel[1], pixel[2]))

    def handle_camera_movement(self, keys, camera_speed):
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            glTranslatef(-camera_speed, 0, 0)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            glTranslatef(camera_speed, 0, 0)
        if keys[pg.K_UP] or keys[pg.K_q]:
            glTranslatef(0, camera_speed, 0)
        if keys[pg.K_DOWN] or keys[pg.K_e]:
            glTranslatef(0, -camera_speed, 0)
        if keys[pg.K_w]:
            glTranslatef(0, 0, camera_speed)
        if keys[pg.K_s]:
            glTranslatef(0, 0, -camera_speed)

    def run(self):
        pg.init()
        display = (800, 600)
        self.screen = pg.display.set_mode(display,  RESIZABLE)
        camera_speed = 0.1
        clock = pg.time.Clock()
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.VIDEORESIZE:
                    pass
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False

            keys = pg.key.get_pressed()
            self.handle_camera_movement(keys, camera_speed)
            self.screen.fill(pg.Color('darkslategray'))
            self.render()
            self.draw()
            pg.display.flip()
            clock.tick(60)  # Limita o loop a 60 frames por segundo

        pg.quit()


if __name__ == '__main__':
    polylines = [
        (((1, 0), (-1, 1), (1, 1), (1, 0))),
        (((1, 0), (-2, 2), (-1, -1), (1, 0))),
        # Novo objeto adicionado
        (((-2, 0), (-3, 1), (-2, 1), (-2, 0)))
    ]
    Cena3D().run()
