import pygame
from .. import tools, setup, constants as C


class LoadScreen:
    def setup(self, player_num, score):
        self.finished = False
        self.next = 'arena'
        self.timer = 0
        self.player_num = player_num
        self.score = score

    def update(self, surface, keys):
        surface.fill(C.SCREEN_COLOR)

        surface.blit(
            tools.create_textImg('PLAYERS'),(C.SCREEN_W*0.43, C.SCREEN_H*0.42))
        surface.blit(tools.create_image(
            setup.GRAPHICS['red'], 0, 0, C.PLAYER_PY, C.PLAYER_PX,C.CURSOR_MULTI), (C.SCREEN_W*0.27, C.SCREEN_H*0.48))
        surface.blit(tools.create_image(
            setup.GRAPHICS['green'], 0, 0, C.PLAYER_PY, C.PLAYER_PX,C.CURSOR_MULTI), (C.SCREEN_W*0.47, C.SCREEN_H*0.48))
        if self.player_num == 3:
            surface.blit(tools.create_image(setup.GRAPHICS['blue'], 0, 0, C.PLAYER_PY, C.PLAYER_PX,
                                         C.CURSOR_MULTI), (C.SCREEN_W*0.67, C.SCREEN_H*0.48))

        if self.timer == 0:
            self.timer = pygame.time.get_ticks()
        elif pygame.time.get_ticks()-self.timer >= C.LOAD_TIME:
            self.finished = True
            self.timer = 0