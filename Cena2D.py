import pygame
import sys

from Objeto3d import Objeto3d

class Cena2D:
    def __init__(self):
        self.WIDTH, self.HEIGHT = 800, 600
        self.DRAW_AREA_WIDTH, self.DRAW_AREA_HEIGHT = 600, 400
        self.DRAW_AREA_X, self.DRAW_AREA_Y = 100, 100
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Desenho de Polylines")

        self.polylines = []
        self.current_polyline = []
        self.drawing = False

        pygame.font.init()
        self.font = pygame.font.SysFont(None, 36)

    def draw_button(self, screen, rect, text, color):
        pygame.draw.rect(screen, color, rect)
        text_surf = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def draw_mouse_coords(self, screen, x, y):
        coord_text = f"X: {x}, Y: {y}"
        text_surf = self.font.render(coord_text, True, (0, 0, 0))
        screen.blit(text_surf, (10, 70))

    def draw_axes(self, screen):
        pygame.draw.line(screen, (0, 0, 0), (self.DRAW_AREA_X, self.DRAW_AREA_Y), (self.DRAW_AREA_X + self.DRAW_AREA_WIDTH, self.DRAW_AREA_Y), 2)
        pygame.draw.line(screen, (0, 0, 0), (self.DRAW_AREA_X, self.DRAW_AREA_Y), (self.DRAW_AREA_X, self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT), 2)
        pygame.draw.line(screen, (0, 0, 0), (self.DRAW_AREA_X + self.DRAW_AREA_WIDTH, self.DRAW_AREA_Y), (self.DRAW_AREA_X + self.DRAW_AREA_WIDTH, self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT), 2)
        pygame.draw.line(screen, (0, 0, 0), (self.DRAW_AREA_X, self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT), (self.DRAW_AREA_X + self.DRAW_AREA_WIDTH, self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT), 2)

    def create3dobj(self):
        objetos = list()
        for p in self.polylines:
            o = Objeto3d(p)
            o.rotacaoX(4)
            objetos.append(0)

        return objetos

    def run(self):

        pygame.init()
        
        button_start_rect = pygame.Rect(10, 10, 150, 50)
        button_end_rect = pygame.Rect(170, 10, 150, 50)
        button_calc = pygame.Rect(370, 10, 150, 50)
        button_3d = pygame.Rect(530, 10, 150, 50)
        button_2d = pygame.Rect(690, 10, 150, 50)
        button_close_polyline = pygame.Rect(690, 100, 150, 50)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if button_start_rect.collidepoint(mouse_pos):
                        self.drawing = True
                        self.current_polyline.clear()
                    elif button_end_rect.collidepoint(mouse_pos):
                        if self.current_polyline:
                            self.polylines.append(self.current_polyline.copy())
                            self.current_polyline.clear()
                        self.drawing = False
                    elif self.drawing and self.DRAW_AREA_X <= mouse_pos[0] <= self.DRAW_AREA_X + self.DRAW_AREA_WIDTH and self.DRAW_AREA_Y <= mouse_pos[1] <= self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT:
                        self.current_polyline.append(mouse_pos)
                    elif button_3d.collidepoint(mouse_pos):
                        return self.polylines[0]
                    elif button_2d.collidepoint(mouse_pos):
                        return "2D"
                    elif button_close_polyline.collidepoint(mouse_pos):
                        self.current_polyline.append(self.current_polyline[0])
                        self.polylines.append(self.current_polyline.copy())
                        self.current_polyline.clear()

            self.screen.fill((255, 255, 255))
            self.draw_button(self.screen, button_start_rect, "Iniciar Desenho", (0, 255, 0))
            self.draw_button(self.screen, button_end_rect, "Terminar Desenho", (255, 0, 0))
            self.draw_button(self.screen, button_calc, 'Gera obj', (0, 0, 255))
            self.draw_button(self.screen, button_3d, '3D', (200, 200, 200))
            self.draw_button(self.screen, button_2d, '2D', (200, 200, 200))
            self.draw_button(self.screen, button_close_polyline, 'end', (200, 200, 200))
            pygame.draw.rect(self.screen, (200, 200, 200), (self.DRAW_AREA_X, self.DRAW_AREA_Y, self.DRAW_AREA_WIDTH, self.DRAW_AREA_HEIGHT), 0)
            self.draw_axes(self.screen)

            for polyline in self.polylines:
                if len(polyline) > 1:
                    pygame.draw.lines(self.screen, (0, 0, 0), False, polyline, 2)
            if len(self.current_polyline) > 1:
                pygame.draw.lines(self.screen, (0, 0, 255), False, self.current_polyline, 2)
            elif len(self.current_polyline) == 1:
                pygame.draw.circle(self.screen, (0, 0, 255), self.current_polyline[0], 3)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x >= self.DRAW_AREA_X and mouse_x <= self.DRAW_AREA_WIDTH:
                if mouse_y >= self.DRAW_AREA_Y and mouse_y <= self.DRAW_AREA_HEIGHT:
                    self.draw_mouse_coords(self.screen, mouse_x - self.DRAW_AREA_X, mouse_y - self.DRAW_AREA_Y)

            pygame.display.flip()
        pygame.quit()
        sys.exit()
