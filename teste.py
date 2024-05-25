import pygame
import sys
import math

# Inicializa o Pygame
pygame.init()

# Define as dimensões da janela
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Alternar entre Cenas")

# Define cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Classe para uma cena genérica
class Cena:
    def __init__(self, color):
        self.color = color

    def update(self):
        pass  # Lógica de atualização da cena vai aqui

    def draw(self, surface):
        pass

# Cena com triângulo
class CenaTriangulo(Cena):
    def __init__(self, color):
        super().__init__(color)
        self.triangle_points = [(400, 200), (300, 400), (500, 400)]

    def draw(self, surface):
        super().draw(surface)
        pygame.draw.polygon(surface, GREEN, self.triangle_points)

# Cena com cubo rotacionando
class CenaCubo(Cena):
    def __init__(self, color):
        super().__init__(color)
        self.cube_image = pygame.Surface((100, 100))
        self.cube_image.fill(WHITE)
        pygame.draw.rect(self.cube_image, BLACK, self.cube_image.get_rect(), 2)
        self.angle = 0

    def update(self):
        self.angle += 1
        if self.angle >= 360:
            self.angle = 0

    def draw(self, surface):
        super().draw(surface)
        rotated_image = pygame.transform.rotate(self.cube_image, self.angle)
        new_rect = rotated_image.get_rect(center=(400, 300))
        surface.blit(rotated_image, new_rect.topleft)

# Classe para um botão
class Botao:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BLACK
        self.text = text
        self.action = action
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


from Objeto3d import Objeto3d
class Cena2D(Cena):
    def __init__(self):
        super().__init__('RED')
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
        self.run()


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

            self.screen.fill((255, 255, 255))
            self.draw_button(self.screen, button_start_rect, "Iniciar Desenho", (0, 255, 0))
            self.draw_button(self.screen, button_end_rect, "Terminar Desenho", (255, 0, 0))
            self.draw_button(self.screen, button_calc, 'Gera obj', (0, 0, 255))
            self.draw_button(self.screen, button_3d, '3D', (200, 200, 200))
            self.draw_button(self.screen, button_2d, '2D', (200, 200, 200))
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




# Classe para a cena principal
class CenaPrincipal:
    def __init__(self):
        self.cena1 = Cena2D()
        self.cena2 = CenaCubo(BLUE)
        self.current_cena = self.cena1
        self.botao = Botao(350, 500, 100, 50, "Trocar", self.trocar_cena)

    def trocar_cena(self):
        if self.current_cena == self.cena1:
            self.current_cena = self.cena2
        else:
            self.current_cena = self.cena1

    def update(self):
        self.current_cena.update()

    def draw(self, surface):
        self.current_cena.draw(surface)
        self.botao.draw(surface)

# Instancia a cena principal
cena_principal = CenaPrincipal()

# Loop principal do jogo
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if cena_principal.botao.is_clicked(event.pos):
                cena_principal.botao.action()

    # Atualiza a cena principal
    cena_principal.update()

    # Desenha a cena principal
    cena_principal.draw(screen)

    # Atualiza a tela
    pygame.display.flip()

    # Controla a taxa de frames por segundo
    clock.tick(60)
