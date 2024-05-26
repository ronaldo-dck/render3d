import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Objeto3d import Objeto3d


class CenaWireframe:
    def __init__(self, polylines=[((1, 0), (-1, 1), (1, 1), (1, 0))]):
        self.objetos = [Objeto3d(p) for p in polylines]
        self.camera_pos = [1, 0, 0]  # Posição inicial da câmera
        for obj in self.objetos:
            obj.rotacaoX(3)
        self.edges = [obj.get_edges() for obj in self.objetos]
        self.faces = [obj.get_faces() for obj in self.objetos]
        self.vertices = [obj.get_vertices() for obj in self.objetos]

    def draw_axes(self):
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(-100, 0, 0)
        glVertex3f(1000, 0, 0)
        glEnd()

        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 1000, 0)
        glEnd()

        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0, 0, -1000)
        glVertex3f(0, 0, 1000)
        glEnd()

    def draw_wireframe(self):
        cx, cy, cz = self.camera_pos
        glBegin(GL_LINES)
        glColor3f(1.0, 0.5, 0.0)
        for i, faces in enumerate(self.faces):
            for face in faces:
                # if face.is_visible((cx, cy, cz)):
                    print(len(faces))
                    for vertex in face.vertices:
                        glVertex3fv(self.vertices[i][vertex][:3])
        glEnd()

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_axes()
        self.draw_wireframe()
        pg.display.flip()

    def resize(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (width / height), 0.1, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        cx, cy, cz = self.camera_pos
        gluLookAt(cx, cy, cz,  # posição da camera
                  0, 0, 0,  # para onde a camera olha
                  0, 0, 1)  # viewUP

    def handle_camera_movement(self, keys, camera_speed):
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.camera_pos[0] -= camera_speed
            glTranslatef(-camera_speed, 0, 0)
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.camera_pos[0] += camera_speed
            glTranslatef(camera_speed, 0, 0)
        if keys[pg.K_UP] or keys[pg.K_q]:
            self.camera_pos[1] += camera_speed
            glTranslatef(0, camera_speed, 0)
        if keys[pg.K_DOWN] or keys[pg.K_e]:
            self.camera_pos[1] -= camera_speed
            glTranslatef(0, -camera_speed, 0)
        if keys[pg.K_w]:
            self.camera_pos[2] += camera_speed
            glTranslatef(0, 0, camera_speed)
        if keys[pg.K_s]:
            self.camera_pos[2] -= camera_speed
            glTranslatef(0, 0, -camera_speed)

    def get_camera_position(self):
        return self.camera_pos

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

            keys = pg.key.get_pressed()
            self.handle_camera_movement(keys, camera_speed)

            screen.fill(pg.Color('darkslategray'))
            self.draw()
            pg.display.flip()
            clock.tick(24)  # Limita o loop a 60 frames por segundo

        pg.quit()


if __name__ == '__main__':
    objetos = [
        # ((1,0),(-1, 1), (1, 1), (1, 0)),
        # ((1,0),(-2, 2), (-1, -1), (1, 0)),
        # ((-2,0),(-3, 1), (-2, 1), (-2, 0)) ,
        ((1, 0), (2, 3))  # Novo objeto adicionado
    ]
    CenaWireframe(objetos).run()