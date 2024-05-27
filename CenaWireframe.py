import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Objeto3d import Objeto3d, Face
import random
from camera import Camera

class CenaWireframe:
    def __init__(self, polylines=[((1,0),(-1, 1), (1, 1), (1, 0))]):
        self.objetos = [Objeto3d(p) for p in polylines]
        print(polylines)
        for obj in self.objetos:
            obj.rotacaoX(16)
        self.edges = [obj.get_edges() for obj in self.objetos]
        self.faces = [obj.get_faces() for obj in self.objetos]
        self.vertices = [obj.get_vertices() for obj in self.objetos]
        self.cores_faces = [[(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)) for _ in obj.get_faces()] for obj in self.objetos]

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
        for i,o in enumerate(self.objetos):
            for face in o.get_faces_visible((0,0,0)):
            # for face in o.get_faces():
                    for vertex in face.vertices:
                        glVertex3fv(self.vertices[i][vertex][:3])
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
        self.draw_wireframe()
        # self.draw_triangles()
        pg.display.flip()

    def resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (width / height), 0.1, 10000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(-200, 0, 0,  # posição da camera
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
        self.resize(display[0], display[1])  # Inicializar a perspectiva corretamente
        

        camera_speed = 0.5
        clock = pg.time.Clock()
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.VIDEORESIZE:
                    self.resize(event.w, event.h)

            keys = pg.key.get_pressed()
            self.handle_camera_movement(keys, camera_speed)

            screen.fill(pg.Color('darkslategray'))
            self.draw()
            pg.display.flip()
            clock.tick(60)  # Limita o loop a 60 frames por segundo

        pg.quit()

if __name__ == '__main__':
    objetos = [
        Objeto3d(((1,0),(-1, 1), (1, 1), (1, 0))), 
        Objeto3d(((1,0),(-2, 2), (-1, -1), (1, 0))),
        Objeto3d(((-2,0),(-3, 1), (-2, 1), (-2, 0)))  # Novo objeto adicionado
    ]
    CenaWireframe(objetos).run()
