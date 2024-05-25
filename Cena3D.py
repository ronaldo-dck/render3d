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
    def __init__(self, polylines=[((-1, 1), (1, 1))]):
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
        # self.draw_triangles()
        pg.display.flip()

    def pipeline():

        pass

    def render(self):
        # Teste da visibilidade

        # Pegar os objetos e passar ele pipeline
        for o in self.objetos:
            faces = o.get_faces_visible((1, -1, 0))
            #está processando informação de vertices não visiveis

            vertices = self.create_objetos() @ o.get_vertices().T
            vertices[[0,1]] /= vertices[-1]
            vertices[[0,1]] =  np.round(vertices[[0,1]], 1)
            print(vertices.T)
            # glBegin(GL_DOT3_RGB)
            # glColor3f(1.0, 0.5, 0.0)
            # for i, f in enumerate(faces):
            #     for vertex in f.vertices:
            #         glVertex3fv(o.get_vertices()[vertex])
            # glEnd()

    def resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (width / height), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(3, 3, 0,  # posição da camera
                  0, 0, 0,  # para onde a camera olha
                  0, 0, 1)  # viewUP

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
        screen = pg.display.set_mode(display, DOUBLEBUF | OPENGL | RESIZABLE)
        # Inicializar a perspectiva corretamente
        self.resize(display[0], display[1])

        camera_speed = 0.1
        clock = pg.time.Clock()
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.VIDEORESIZE:
                    self.resize(event.w, event.h)
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False

            keys = pg.key.get_pressed()
            self.handle_camera_movement(keys, camera_speed)

            screen.fill(pg.Color('darkslategray'))
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
