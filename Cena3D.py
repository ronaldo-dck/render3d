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
        self.width = 1000
        self.height = 900
        self.z_buffer = np.full((self.height, self.width), -float('inf'))
        self.cor_buffer = np.full((self.height, self.width, 3), [
            174, 174, 174], dtype=np.uint8)
        for obj in self.objetos:
            obj.rotacaoX(30)

        self.cores_faces = [[(random.uniform(0, 1), random.uniform(
            0, 1), random.uniform(0, 1)) for _ in obj.get_faces()] for obj in self.objetos]

    def create_objetos(self):
        self.camera = Camera((-1, 0, 0), (0, 0, 0), (0, 1, 0))
        self.projetion = Projetion().projetion_matrix(150)
        self.to_screen = Projetion().to_screen(-self.width//2, self.width//2, -
                                               self.width//2, self.height//2, 0, self.width, 0, self.height)
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
        glColor3f(1.0, 0.4, 0.0)
        # for i, faces in enumerate(self.objetos[0].get_faces()):
        for face in self.objetos[0].get_faces():
            vertices = self.objetos[0].get_vertices().T[:3].T
            f = Face(vertices, face.vertices)
            if f.is_visible((1, 10, 0)):
                for vertex in face.vertices:
                    glVertex3fv(vertices[vertex])
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

    def fillpoly(self, face, all_vertices, color):
        i_vertices = face.vertices
        vertices = sorted(all_vertices[[i_vertices]], key=lambda v: v[1])[0]

        (x1, y1), z1 = map(int, vertices[0][:2]), float(vertices[0][2])
        (x2, y2), z2 = map(int, vertices[1][:2]), float(vertices[1][2])
        (x3, y3), z3 = map(int, vertices[2][:2]), float(vertices[2][2])
        # print(vertices)
        # exit()
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
                            self.cor_buffer[y, x] = [70, 50, 100]
                    z += dz

    def render(self):
        for obj_idx, o in enumerate(self.objetos):
            # faces = o.get_faces_visible((1, 0, 0))
            faces = o.get_faces()
            vertices = self.create_objetos() @ o.get_vertices().T
            vertices[[0, 1]] /= vertices[-1]
            vertices[[0, 1]] = np.round(vertices[[0, 1]], 1)
            vertices = vertices.T

            for face_idx, face in enumerate(faces):
                self.fillpoly(face, vertices, [0, 0, 0])
                # pg.surfarray.blit_array(self.screen, cores)

            for y, linha in enumerate(self.cor_buffer):
                for x, pixel in enumerate(linha):
                    self.screen.set_at((x, y), (pixel[0], pixel[1], pixel[2]))
                    # self.screen.blit_array(sel, (pixel[0], pixel[1], pixel[2]))

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
        display = (self.width, self.height)
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(1, 2, 0,  # posição da camera
                  0, 0, 0,  # para onde a camera olha
                  0, 1, 0)  # viewUP
        self.screen = pg.display.set_mode(display,  RESIZABLE)
        camera_speed = 0.5
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

            keys = pg.key.get_pressed()
            self.handle_camera_movement(keys, camera_speed)
            self.screen.fill(pg.Color('darkslategray'))
            self.render()
            # self.draw()
            # self.draw_axes()
            # self.draw_wireframe()
            pg.display.flip()
            clock.tick(24)  # Limita o loop a 60 frames por segundo

        pg.quit()


if __name__ == '__main__':
    polylines = [
        # (((1, 0), (-1, 1), (1, 1), (1, 0))),
        (((100, 0), (-200, 200), (-100, -100), (100, 0))),
        # Novo objeto adicionado
        (((200, 400), (300, 100), (200, 1), (10, 0)))
    ]
    Cena3D().run()
