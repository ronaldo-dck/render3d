import pygame
from pygame.locals import *
import numpy as np

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

z_buffer = np.full((HEIGHT, WIDTH), -float('inf'))


def oldfillpoly(face, all_vertices, color):
    i_vertices = face
    selected_vertices = all_vertices
    vertices = sorted(selected_vertices, key=lambda v: v[1], reverse=True)

    (x1, y1), z1 = map(int, vertices[0][:2]), float(vertices[0][2])
    (x2, y2), z2 = map(int, vertices[1][:2]), float(vertices[1][2])
    (x3, y3), z3 = map(int, vertices[2][:2]), float(vertices[2][2])

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

    height = HEIGHT
    width = WIDTH

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
            if y >= HEIGHT:
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
                        screen.set_at((x, y), color)
                    z += dz

# Função fillpoly modificada para funcionar com pygame


def fillpoly(screen, face, all_vertices, color):
    selected_vertices = all_vertices
    vertices = sorted(selected_vertices, key=lambda v: v[1])

    # Definindo uma profundidade padrão caso não haja uma coordenada z para algum vértice
    # for vertex in vertices:
    #     if len(vertex) < 3:
    #         vertex.append(0)  # Profundidade padrão é 0 se não for fornecida

    (x0, y0), z0 = map(int, vertices[0][:2]), float(vertices[0][2])
    (x1, y1), z1 = map(int, vertices[1][:2]), float(vertices[1][2])
    (x2, y2), z2 = map(int, vertices[2][:2]), float(vertices[2][2])

    arestas = [
        {
            'ini': (x0, y0, z0),
            'fim': (x1, y1, z1),
            'taxaX': ((x1 - x0) / (y1 - y0)),
            'taxaZ': ((z1 - z0) / (y1 - y0))
        },
        {
            'ini': (x1, y1, z1),
            'fim': (x2, y2, z2),
            'taxaX': ((x2 - x1) / (y2 - y1)),
            'taxaZ': ((z2 - z1) / (y2 - y1))
        },
        {
            'ini': (x2, y2, z2),
            'fim': (x0, y0, z0),
            'taxaX': ((x0 - x2) / (y0 - y2)),
            'taxaZ': ((z0 - z2) / (y0 - y2))
        }
    ]

    arestas.sort(key=lambda x: x['ini'][1])

    # print(arestas)

    lastIniX = arestas[0]['ini'][0]
    lastFimX = arestas[0]['ini'][0]
    lastIniZ = arestas[0]['ini'][2]
    lastFimZ = arestas[0]['ini'][2]

    swapped = False
    if (arestas[0]['ini'][0] > arestas[1]['ini'][0]):
        swapped = True

    for y in range(arestas[0]['ini'][1], arestas[0]['fim'][1]):
        lastIniX += arestas[0]['taxaX']
        lastFimX += arestas[2]['taxaX']
        lastIniZ += arestas[0]['taxaZ']
        lastFimZ += arestas[2]['taxaZ']

        lastIniX = round(lastIniX)
        lastFimX = round(lastFimX)

        varX = (lastFimX - lastIniX) + 1e-16
        deltaZ = (lastFimZ - lastIniZ) / varX
        startZ = lastIniZ

        print(lastIniX, lastFimX)
        if swapped:
            for x in range(lastIniX, lastFimX):
                screen.set_at((x, y), color)
                startZ += deltaZ
        else:
            for x in range(lastFimX, lastIniX):
                screen.set_at((x, y), color)
                startZ += deltaZ

    lastIniZ = arestas[1]['ini'][2]

    for y in range(arestas[1]['ini'][1], arestas[1]['fim'][1]):
        lastIniX += arestas[1]['taxaX']
        lastFimX += arestas[2]['taxaX']
        lastIniZ += arestas[1]['taxaZ']
        lastFimZ += arestas[2]['taxaZ']

        lastIniX = round(lastIniX)
        lastFimX = round(lastFimX)

        varX = (lastFimX - lastIniX) + 1e-16
        deltaZ = (lastFimZ - lastIniZ) / varX
        startZ = lastIniZ

        if swapped:
            for x in range(lastIniX, lastFimX):
                screen.set_at((x, y), color)
                startZ += deltaZ
        else:
            for x in range(lastFimX, lastIniX):
                screen.set_at((x, y), color)
                startZ += deltaZ


# Definições de cor e tamanho da tela

# Inicialização do Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Teste de fillpoly")

# Desenhar um triângulo na tela
triangle_vertices = [(100, 100, 20), (200, 200, 32), (350, 150, 54)]
triangle_vertices_a = [(100, 100), (200, 200), (350, 150)]
pygame.draw.polygon(screen, WHITE, triangle_vertices_a, 1)
fillpoly(screen, [0, 1, 2], triangle_vertices, RED)

triangle_vertices1 = [(100, 100, 20), (200, 200, 32), (50, 150, 54)]
triangle_vertices1_a = [(100, 100), (200, 200), (50, 150)]
pygame.draw.polygon(screen, WHITE, triangle_vertices1_a, 1)
fillpoly(screen, [0, 1, 2], triangle_vertices1, GREEN)

# Preencher o triângulo com a função fillpoly
# oldfillpoly(screen, triangle_vertices, GREEN)

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEMOTION:  # Captura o evento de movimento do mouse
            mouseX, mouseY = pygame.mouse.get_pos()  # Obtém a posição atual do mouse
            # Exibe a posição do mouse na janela do console
            print("Mouse position:", mouseX, mouseY)

    pygame.display.flip()

# Encerramento do Pygame
pygame.quit()
