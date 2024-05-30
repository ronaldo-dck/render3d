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

        self.polylines = [[(0,0)]]
        self.current_polyline = []
        self.drawing = False

        pygame.font.init()
        self.font = pygame.font.SysFont(None, 30)

    def draw_button(self, screen, rect, text, color):
        pygame.draw.rect(screen, color, rect)
        text_surf = self.font.render(text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

    def draw_mouse_coords(self, screen, x, y):
        coord_text = f"X: {x}, Y: {y}"
        text_surf =  pygame.font.SysFont(None, 20).render(coord_text, True, (0, 0, 0))
        screen.blit(text_surf, (100, 85))

    def draw_axes(self, screen):
        pygame.draw.line(screen, (0, 0, 0), (self.DRAW_AREA_X, self.DRAW_AREA_Y), (self.DRAW_AREA_X + self.DRAW_AREA_WIDTH, self.DRAW_AREA_Y), 2)
        pygame.draw.line(screen, (0, 0, 0), (self.DRAW_AREA_X, self.DRAW_AREA_Y), (self.DRAW_AREA_X, self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT), 2)
        pygame.draw.line(screen, (0, 0, 0), (self.DRAW_AREA_X + self.DRAW_AREA_WIDTH, self.DRAW_AREA_Y), (self.DRAW_AREA_X + self.DRAW_AREA_WIDTH, self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT), 2)
        pygame.draw.line(screen, (0, 0, 0), (self.DRAW_AREA_X, self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT), (self.DRAW_AREA_X + self.DRAW_AREA_WIDTH, self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT), 2)

    def run(self):

        pygame.init()
        button_start_rect = pygame.Rect(50, 25, 200, 50)
        button_close_polyline = pygame.Rect(300, 25, 200, 50)
        button_end_rect = pygame.Rect(550, 25, 200, 50)
        button_3d = pygame.Rect(300, 525, 200, 50)

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
                    elif button_close_polyline.collidepoint(mouse_pos):
                        if self.current_polyline:
                            self.current_polyline.append(self.current_polyline[0])
                            self.polylines.append(self.current_polyline.copy())
                            self.current_polyline.clear()
                        self.drawing = False
                    elif button_end_rect.collidepoint(mouse_pos):
                        if self.current_polyline:
                            self.polylines.append(self.current_polyline.copy())
                            self.current_polyline.clear()
                        self.drawing = False
                    elif self.drawing and self.DRAW_AREA_X <= mouse_pos[0] <= self.DRAW_AREA_X + self.DRAW_AREA_WIDTH and self.DRAW_AREA_Y <= mouse_pos[1] <= self.DRAW_AREA_Y + self.DRAW_AREA_HEIGHT:
                        self.current_polyline.append((mouse_pos[0] - self.DRAW_AREA_X, mouse_pos[1] - self.DRAW_AREA_Y))
                    elif button_3d.collidepoint(mouse_pos):
                        # treated_polylines = []
                        # for polyline in self.polylines:
                        #     linha = [list(v) for v in polyline]
                        #     treated_polylines.append([])
                        #     for i in range(len(polyline)):
                        #         # treated_polylines[index].append((polyline[i][0] - self.DRAW_AREA_X, polyline[i][1] - self.DRAW_AREA_Y))
                        #         treated_polylines.append([polyline[i][0] - self.DRAW_AREA_X, polyline[i][1] - self.DRAW_AREA_Y])
                        return "3D", self.polylines

            self.screen.fill((255, 255, 255))
            if not self.drawing:
                self.draw_button(self.screen, button_start_rect, "Iniciar Desenho", (50, 255, 150))
                self.draw_button(self.screen, button_close_polyline, 'Finalizar fechado', (200, 200, 200))
                self.draw_button(self.screen, button_end_rect, "Finalizar aberto", (200, 200, 200))
            else:
                self.draw_button(self.screen, button_start_rect, "Iniciar Desenho", (200, 200, 200))
                self.draw_button(self.screen, button_close_polyline, 'Finalizar fechado', (255, 230, 50))
                self.draw_button(self.screen, button_end_rect, "Finalizar aberto", (255, 70, 70))
            self.draw_button(self.screen, button_3d, '3D', (200, 200, 200))
            pygame.draw.rect(self.screen, (200, 200, 200), (self.DRAW_AREA_X, self.DRAW_AREA_Y, self.DRAW_AREA_WIDTH, self.DRAW_AREA_HEIGHT), 0)
            self.draw_axes(self.screen)

            for polyline in self.polylines:
                if len(polyline) > 1:
                    pygame.draw.lines(self.screen, (0, 0, 0), False, [(x+100, y+100) for x, y in polyline], 2)
            if len(self.current_polyline) > 1:
                pygame.draw.lines(self.screen, (0, 0, 255), False, [(x+100, y+100) for x, y in self.current_polyline], 2)
            elif len(self.current_polyline) == 1:
                pygame.draw.circle(self.screen, (0, 0, 255), (self.current_polyline[0][0]+100, self.current_polyline[0][1]+100), 3)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x >= self.DRAW_AREA_X and mouse_x <= self.DRAW_AREA_WIDTH:
                if mouse_y >= self.DRAW_AREA_Y and mouse_y <= self.DRAW_AREA_HEIGHT:
                    self.draw_mouse_coords(self.screen, mouse_x - self.DRAW_AREA_X, mouse_y - self.DRAW_AREA_Y)

            pygame.display.flip()
        pygame.quit()
        sys.exit()
