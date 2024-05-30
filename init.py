import pygame
import sys
from Cena2D import Cena2D
from Cena3D import Cena3D
from CenaWireframe import CenaWireframe



# Inicializa o Pygame
pygame.init()

# Define as dimensões da janela
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Alternar entre Cenas")

# Classe para a cena principal
class CenaPrincipal:
    def __init__(self, screen):
        self.screen = screen
        self.cena1 = Cena2D()
        self.current_cena = self.cena1

    def trocar_cena(self):
        if self.current_cena == self.cena1:
            self.current_cena = self.cena2
        else:
            self.current_cena = self.cena1

    def update(self):
        # self.cena2 = Cena3D(self.current_cena.run())
        retorno, poli = self.current_cena.run()
        self.cena2 = Cena3D(poli)
        self.trocar_cena()

    def draw(self, surface):
        self.current_cena.run()

# Instancia a cena principal
cena_principal = CenaPrincipal(screen)

# Loop principal do jogo
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()



    # Atualiza a cena principal
    cena_principal.update()

    # Desenha a cena principal
    # cena_principal.draw(screen)

    # Atualiza a tela
    # pygame.display.flip()

    # Controla a taxa de frames por segundo
    clock.tick(30)
