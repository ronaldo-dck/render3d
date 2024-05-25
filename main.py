import pygame
import sys
import math
from Objeto3d import Objeto3d

# Inicializa o Pygame
pygame.init()

# Definições de cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Configurações da tela
WIDTH, HEIGHT = 800, 600
DRAW_AREA_WIDTH, DRAW_AREA_HEIGHT = 600, 400
DRAW_AREA_X, DRAW_AREA_Y = 100, 100
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Desenho de Polylines")

# Lista para armazenar polylines
polylines = []
objetos = []
current_polyline = []
drawing = False

# Fontes
font = pygame.font.SysFont(None, 36)

# Função para desenhar botões
def draw_button(screen, rect, text, color):
    pygame.draw.rect(screen, color, rect)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Função para desenhar as coordenadas do mouse
def draw_mouse_coords(screen, x, y):
    coord_text = f"X: {x}, Y: {y}"
    text_surf = font.render(coord_text, True, BLACK)
    screen.blit(text_surf, (10, 70))

# Função para desenhar os eixos
def draw_axes(screen):
    pygame.draw.line(screen, BLACK, (DRAW_AREA_X, DRAW_AREA_Y), (DRAW_AREA_X + DRAW_AREA_WIDTH, DRAW_AREA_Y), 2)
    pygame.draw.line(screen, BLACK, (DRAW_AREA_X, DRAW_AREA_Y), (DRAW_AREA_X, DRAW_AREA_Y + DRAW_AREA_HEIGHT), 2)
    pygame.draw.line(screen, BLACK, (DRAW_AREA_X + DRAW_AREA_WIDTH, DRAW_AREA_Y), (DRAW_AREA_X + DRAW_AREA_WIDTH, DRAW_AREA_Y + DRAW_AREA_HEIGHT), 2)
    pygame.draw.line(screen, BLACK, (DRAW_AREA_X, DRAW_AREA_Y + DRAW_AREA_HEIGHT), (DRAW_AREA_X + DRAW_AREA_WIDTH, DRAW_AREA_Y + DRAW_AREA_HEIGHT), 2)


def create_3d_object(polyline, divisions=36):
    vertices = []
    geratriz = list()
    for v in polyline:
        geratriz.append(v[0] - DRAW_AREA_X, v[1] - DRAW_AREA_Y)

    obj = Objeto3d(polyline)
    objetos.append(obj)
    return vertices


def main():
    global drawing, current_mode
    polylines.append([(200, 200), (400, 200)])
    button_start_rect = pygame.Rect(10, 10, 150, 50)
    button_end_rect = pygame.Rect(170, 10, 150, 50)
    button_calc = pygame.Rect(370, 10, 150, 50)
    button_3d = pygame.Rect(530, 10, 150, 50)
    button_2d = pygame.Rect(690, 10, 150, 50)

    current_mode = "2D"
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if button_start_rect.collidepoint(mouse_pos):
                    drawing = True
                    current_polyline.clear()
                elif button_end_rect.collidepoint(mouse_pos):
                    if current_polyline:
                        polylines.append(current_polyline.copy())
                        current_polyline.clear()
                    drawing = False
                elif drawing and DRAW_AREA_X <= mouse_pos[0] <= DRAW_AREA_X + DRAW_AREA_WIDTH and DRAW_AREA_Y <= mouse_pos[1] <= DRAW_AREA_Y + DRAW_AREA_HEIGHT:
                    # Adiciona o ponto atual à polyline em construção
                    print(mouse_pos)
                    current_polyline.append(mouse_pos)
                elif button_calc.collidepoint(mouse_pos):
                    current_3d_object = create_3d_object(polyline=polylines[0], divisions=4)
                elif button_3d.collidepoint(mouse_pos):
                    current_mode = "3D"
                elif button_2d.collidepoint(mouse_pos):
                    current_mode = "2D"
            
        
        # Desenha a tela
        screen.fill(WHITE)
        
        # Desenha os botões
        draw_button(screen, button_start_rect, "Iniciar Desenho", GREEN)
        draw_button(screen, button_end_rect, "Terminar Desenho", RED)
        draw_button(screen, button_calc, 'Gera obj', BLUE)
        draw_button(screen, button_3d, '3D', GRAY if current_mode == "3D" else WHITE)
        draw_button(screen, button_2d, '2D', GRAY if current_mode == "2D" else WHITE)
        
        # Desenha a área de desenho
        pygame.draw.rect(screen, GRAY, (DRAW_AREA_X, DRAW_AREA_Y, DRAW_AREA_WIDTH, DRAW_AREA_HEIGHT), 0)
        
        # Desenha os eixos
        draw_axes(screen)
        
        if current_mode == "2D":
            # Desenha todas as polylines já finalizadas
            for polyline in polylines:
                if len(polyline) > 1:
                    pygame.draw.lines(screen, BLACK, False, polyline, 2)
            
            # Desenha a polyline em construção
            if len(current_polyline) > 1:
                pygame.draw.lines(screen, BLUE, False, current_polyline, 2)
            elif len(current_polyline) == 1:
                pygame.draw.circle(screen, BLUE, current_polyline[0], 3)


        # Pega as coordenadas do mouse e desenha na tela
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x >= DRAW_AREA_X and mouse_x <= DRAW_AREA_WIDTH:
            if mouse_y >= DRAW_AREA_Y and mouse_y <= DRAW_AREA_HEIGHT:
                draw_mouse_coords(screen, mouse_x - DRAW_AREA_X, mouse_y - DRAW_AREA_Y)

        pygame.display.flip()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
