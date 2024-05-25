import pygame as pg
from pygame.locals import *

def main():
    pg.init()
    screen = pg.display.set_mode((400, 300))
    clock = pg.time.Clock()

    # Definir as cores
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    # Definir a fonte
    font = pg.font.Font(None, 32)

    # Definir a caixa de texto
    input_box = pg.Rect(100, 100, 140, 32)
    color_inactive = pg.Color('lightskyblue3')
    color_active = pg.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pg.event.get():
            if event.type == QUIT:
                done = True
            if event.type == MOUSEBUTTONDOWN:
                # Se o usuário clicar na caixa de texto
                if input_box.collidepoint(event.pos):
                    # Ativar a caixa de texto
                    active = not active
                else:
                    active = False
                # Mudar a cor da caixa de texto
                color = color_active if active else color_inactive
            if event.type == KEYDOWN:
                # Se a caixa de texto estiver ativa e o usuário pressionar uma tecla
                if active:
                    # Se o usuário pressionar Enter
                    if event.key == K_RETURN:
                        print(text)
                        text = ''
                    # Se o usuário pressionar Backspace
                    elif event.key == K_BACKSPACE:
                        text = text[:-1]
                    # Se o usuário pressionar uma tecla
                    else:
                        text += event.unicode

        # Desenhar a caixa de texto
        screen.fill(WHITE)
        pg.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(text, True, BLACK)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pg.display.flip()
        clock.tick(30)

    pg.quit()

if __name__ == '__main__':
    main()
