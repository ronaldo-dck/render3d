import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Objeto3d import Objeto3d, Face
import random


class Cena3D:
    def __init__(self, polyline=[(0, 0), (1, 1)]):
        self.obj = Objeto3d([(-1, 1), (1, 1), (1,0)])
        self.obj.rotacaoX(4)
        self.edges = self.obj.get_edges()
        self.faces = self.obj.get_faces()
        self.vertices = self.obj.get_vertices()

        self.cores_faces = []
        for face in self.faces:
            cor_r = random.uniform(0, 1)
            cor_g = random.uniform(0, 1)
            cor_b = random.uniform(0, 1)
            self.cores_faces.append((cor_r, cor_g, cor_b))

        pygame.font.init()
        self.font = pygame.font.SysFont(None, 36)
        self.button_2d_rect = pygame.Rect(10, 10, 150, 50)

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
        for e in self.edges:
            glVertex3fv(self.vertices[e[0]])
            glVertex3fv(self.vertices[e[1]])
        glEnd()

    def draw_triangles(self):
        glBegin(GL_TRIANGLES)
        for i, face in enumerate(self.faces):

            f = Face(self.vertices, face)
            if f.is_visible((1, 10, 0)):
                glColor3f(*self.cores_faces[i])
                for vertex in face:
                    glVertex3fv(self.vertices[vertex])
        glEnd()
    
    def draw_button(self, screen, rect, text, color):
        pygame.draw.rect(screen, color, rect)
        text_surf = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)



    def display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.draw_axes()
        self.draw_wireframe()
        self.draw_triangles()
        pygame.display.flip()

    def run(self):
        pygame.init()
        display = (800, 600)
        screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
        gluPerspective(45, (display[0] / display[1]), 0.1, 1000.0)
        gluLookAt(1, 2, 0,
                    0, 0, 0,
                  0, 0, 1)

        button_2d = pygame.Rect(170, 10, 150, 50)

        camera_speed = 0.1
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.button_2d_rect.collidepoint(mouse_pos):
                        return "2D"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "2D"
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                glTranslatef(-camera_speed, 0, 0)
            if keys[pygame.K_RIGHT]:
                glTranslatef(camera_speed, 0, 0)
            if keys[pygame.K_UP]:
                glTranslatef(0, camera_speed, 0)
            if keys[pygame.K_DOWN]:
                glTranslatef(0, -camera_speed, 0)
            if keys[pygame.K_w]:
                glTranslatef(0, 0, camera_speed)
            if keys[pygame.K_s]:
                glTranslatef(0, 0, -camera_speed)
            if keys[pygame.K_a]:
                glTranslatef(-camera_speed, 0, 0)
            if keys[pygame.K_d]:
                glTranslatef(camera_speed, 0, 0)
            if keys[pygame.K_q]:
                glTranslatef(0, camera_speed, 0)
            if keys[pygame.K_e]:
                glTranslatef(0, -camera_speed, 0)

            self.display()
            self.draw_button(screen, button_2d, '2D', (200, 200, 200))

            screen.fill(pygame.Color('darkslategray'))
            pygame.display.flip()
            pygame.time.wait(10)
