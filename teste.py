import numpy as np
import pygame

class Face:
    def __init__(self, vertices):
        self.vertices = vertices

class Objeto:
    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces

    def get_faces(self):
        return self.faces

    def get_vertices(self):
        return self.vertices

class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.z_buffer = np.full((height, width), -np.inf)
        self.cor_buffer = np.full((height, width, 3), [0, 0, 0])
        self.screen = pygame.Surface((width, height))
        self.objetos = []

    def add_objeto(self, objeto):
        self.objetos.append(objeto)

    def fillpoly(self, face, all_vertices, color):
        i_vertices = face.vertices
        vertices = sorted(all_vertices[i_vertices], key=lambda v: v[1])

        (x1, y1), z1 = map(int, vertices[0][:2]), float(vertices[0][2])
        (x2, y2), z2 = map(int, vertices[1][:2]), float(vertices[1][2])
        (x3, y3), z3 = map(int, vertices[2][:2]), float(vertices[2][2])

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
                            self.cor_buffer[y, x] = color
                    z += dz

    def render(self):
        for obj_idx, o in enumerate(self.objetos):
            faces = o.get_faces()
            vertices = o.get_vertices()

            for face_idx, face in enumerate(faces):
                self.fillpoly(face, vertices, [70, 50, 100])

            for y, linha in enumerate(self.cor_buffer):
                for x, pixel in enumerate(linha):
                    self.screen.set_at((x, y), (pixel[0], pixel[1], pixel[2]))

# Dados sintéticos para teste
vertices = np.array([
    [93, 251, -22.807],
    [198, 241, -20.129],
    [125, 107, -21.815]
])

faces = [Face([0, 1, 2])]

objeto = Objeto(vertices, faces)

renderer = Renderer(300, 300)
renderer.add_objeto(objeto)
renderer.render()

# Mostrar a imagem renderizada (necessita de pygame)
pygame.init()
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption('Renderização')
screen.blit(renderer.screen, (0, 0))
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()
