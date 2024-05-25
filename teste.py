import pygame
import numpy as np

# Inicialização do Pygame
pygame.init()

# Configurações da janela
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Desenhando Polígono Preenchido com Z-buffer")

# Cores
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# Função para desenhar linha pixel a pixel
def draw_line(screen, start, end, color):
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))

    x_inc = dx / steps
    y_inc = dy / steps

    x, y = x1, y1
    for _ in range(steps):
        screen.set_at((int(x), int(y)), color)
        x += x_inc
        y += y_inc

# Função para desenhar polígono preenchido usando Z-buffer
def draw_filled_polygon_z_buffer(screen, vertices, color):
    # Função para preencher triângulo usando Z-buffer
    def fill_triangle_z_buffer(v1, v2, v3, color):
        # Ordenar vértices por y
        vertices = sorted([v1, v2, v3], key=lambda v: v[1])
        (x1, y1), (x2, y2), (x3, y3) = vertices

        # Calcular coeficientes de inclinação inversa para as arestas
        inv_slope1 = (x2 - x1) / (y2 - y1) if (y2 - y1) != 0 else 0
        inv_slope2 = (x3 - x1) / (y3 - y1) if (y3 - y1) != 0 else 0
        inv_slope3 = (x3 - x2) / (y3 - y2) if (y3 - y2) != 0 else 0

        # Inicializar Z-buffer
        z_buffer = np.full((width, height), -float('inf'))

        # Função para preencher linha horizontal usando Z-buffer
        def fill_horizontal_line_z_buffer(y, x_start, x_end, z_start, z_end):
            z_inc = (z_end - z_start) / (x_end - x_start) if (x_end - x_start) != 0 else 0
            for x in range(x_start, x_end + 1):
                if z_buffer[x, y] < z_start:
                    screen.set_at((x, y), color)
                    z_buffer[x, y] = z_start
                z_start += z_inc

        # Preencher a parte superior do triângulo (até a linha do meio)
        curx1 = curx2 = x1
        z1 = z2 = z3 = 0  # Profundidade (Z) inicial para os vértices
        z_inc1 = (0 - z1) / (y2 - y1) if (y2 - y1) != 0 else 0
        z_inc2 = (0 - z1) / (y3 - y1) if (y3 - y1) != 0 else 0
        for scanlineY in range(y1, y2 + 1):
            fill_horizontal_line_z_buffer(scanlineY, int(curx1), int(curx2), z1, z2)
            curx1 += inv_slope1
            curx2 += inv_slope2
            z1 += z_inc1
            z2 += z_inc2

        # Preencher a parte inferior do triângulo (da linha do meio para baixo)
        curx1 = x2
        z1 = z2
        z_inc1 = (0 - z1) / (y3 - y2) if (y3 - y2) != 0 else 0
        for scanlineY in range(y2, y3 + 1):
            fill_horizontal_line_z_buffer(scanlineY, int(curx1), int(curx2), z1, z2)
            curx1 += inv_slope3
            curx2 += inv_slope2
            z1 += z_inc1
            z2 += z_inc2

    # Dividir o polígono em triângulos
    for i in range(1, len(vertices) - 1):
        v1, v2, v3 = vertices[0], vertices[i], vertices[i + 1]
        fill_triangle_z_buffer(v1, v2, v3, color)

# Vértices do polígono
vertices = [(400, 100), (300, 400), (500, 400), (600, 200), (500, 100)]

# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(black)
    
    draw_filled_polygon_z_buffer(screen, vertices, white)

    pygame.display.flip()

pygame.quit()
