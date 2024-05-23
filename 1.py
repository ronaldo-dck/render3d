import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from Objeto3d import Objeto3d
import random


obj = Objeto3d([(0,0),(2, 2), (4, 2)])
obj.rotacaoX(4)

edges = obj.get_edges()
faces = obj.get_faces()
vertices = obj.get_vertices()


cores_faces = []  # Lista para armazenar as cores de cada face

# Gera cores aleatórias para cada face e as armazena na lista cores_faces
for face in faces:
    cor_r = random.uniform(0, 1)
    cor_g = random.uniform(0, 1)
    cor_b = random.uniform(0, 1)
    cores_faces.append((cor_r, cor_g, cor_b))


def draw_axes():
    # Eixo X (vermelho)
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(1000, 0, 0)
    glEnd()

    # Eixo Y (verde)
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 1000, 0)
    glEnd()

    # Eixo Z (azul)
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 1000)
    glEnd()


print(len(edges))
print(edges)




def draw_wireframe():
    
    # Desenha as arestas do cubo
    glBegin(GL_LINES)
    glColor3f(1.0, 0.5, 0.0)
    for e in edges:
        glVertex3fv(vertices[e[0]])
        glVertex3fv(vertices[e[1]])
    glEnd()
    





def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    gluLookAt(2, 0, 0,  # Posição da câmera (acima do eixo X)
              0, 0, 0,   # Ponto para onde a câmera está olhando (origem)
              0, 0, 1)   # Vetor de orientação da câmera (para cima)

    camera_speed = 0.05
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

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

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Desenhar os eixos coordenados
        draw_axes()

        # Desenhar o objeto como wireframe
        draw_wireframe()

        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == "__main__":
    main()
