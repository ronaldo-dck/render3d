import pygame
import numpy as np

# Configurações iniciais
width, height = 800, 600
background_color = (0, 0, 0)
screen = pygame.display.set_mode((width, height))

# Inicialização do Z-buffer
z_buffer = np.full((width, height), np.inf)

# Função para interpolar valores
def interpolate(y, v0, v1):
    dy = v1[1] - v0[1]
    if dy == 0:
        return v0[0], v0[2], v0[3]
    dx = v1[0] - v0[0]
    dz = v1[2] - v0[2]
    dr = v1[3][0] - v0[3][0]
    dg = v1[3][1] - v0[3][1]
    db = v1[3][2] - v0[3][2]
    x = v0[0] + dx * (y - v0[1]) / dy
    z = v0[2] + dz * (y - v0[1]) / dy
    r = v0[3][0] + dr * (y - v0[1]) / dy
    g = v0[3][1] + dg * (y - v0[1]) / dy
    b = v0[3][2] + db * (y - v0[1]) / dy
    return x, z, (r, g, b)

# Função para rasterizar um polígono com sombreamento Gouraud
def draw_polygon(screen, z_buffer, vertices):
    # Triangulação simples para um polígono convexo
    # Supondo que o polígono é definido como uma lista de vértices [(x1, y1, z1, (r1, g1, b1)), (x2, y2, z2, (r2, g2, b2)), ...]
    triangles = []
    for i in range(1, len(vertices) - 1):
        triangles.append((vertices[0], vertices[i], vertices[i + 1]))
    
    for triangle in triangles:
        draw_triangle(screen, z_buffer, triangle)

def draw_triangle(screen, z_buffer, triangle):
    v1, v2, v3 = triangle
    # Ordenando os vértices pelo eixo y (scanline order)
    if v1[1] > v2[1]: v1, v2 = v2, v1
    if v2[1] > v3[1]: v2, v3 = v3, v2
    if v1[1] > v3[1]: v1, v3 = v3, v1

    def fill_scanline(y, x_start, z_start, color_start, x_end, z_end, color_end):
        if x_start > x_end:
            x_start, x_end = x_end, x_start
            z_start, z_end = z_end, z_start
            color_start, color_end = color_end, color_start
        
        dx = x_end - x_start
        if dx == 0:
            z = (z_start + z_end) / 2
            color = [(color_start[i] + color_end[i]) / 2 for i in range(3)]
            if 0 <= int(x_start) < width and z < z_buffer[int(x_start), y]:
                z_buffer[int(x_start), y] = z
                screen.set_at((int(x_start), y), color)
            return
        
        for x in range(int(x_start), int(x_end) + 1):
            z = z_start + (z_end - z_start) * (x - x_start) / dx
            color = [
                color_start[i] + (color_end[i] - color_start[i]) * (x - x_start) / dx
                for i in range(3)
            ]
            if 0 <= x < width and 0 <= y < height and z < z_buffer[x, y]:
                z_buffer[x, y] = z
                screen.set_at((x, y), color)
    
    for y in range(int(v1[1]), int(v2[1]) + 1):
        x_start, z_start, color_start = interpolate(y, v1, v2)
        x_end, z_end, color_end = interpolate(y, v1, v3)
        fill_scanline(y, x_start, z_start, color_start, x_end, z_end, color_end)
    
    for y in range(int(v2[1]), int(v3[1]) + 1):
        x_start, z_start, color_start = interpolate(y, v2, v3)
        x_end, z_end, color_end = interpolate(y, v1, v3)
        fill_scanline(y, x_start, z_start, color_start, x_end, z_end, color_end)

# Vertices do polígono (exemplo)
vertices = [
    (300, 200, 1, (255, 0, 0)),  # Vermelho
    (500, 200, 1, (0, 255, 0)),  # Verde
    (400, 400, 0.5, (0, 0, 255))  # Azul
]

# Função principal
def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill(background_color)
        
        # Reinicialize o Z-buffer a cada quadro
        z_buffer = np.full((width, height), np.inf)
        
        draw_polygon(screen, z_buffer, vertices)
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
