import pygame
import sys
from .. import setup, tools, constants as C

class Button:
    def __init__(self, rect, color, text):
        self.rect = pygame.Rect(rect)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.clicked = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.clicked = False

class MainMenu:
    def __init__(self):
        self.how_to_play()
        self.how_tank_look()
        self.choose_player_num()
        self.finished = False
        self.next = 'arena'
        # score数组用于表示玩家得分，-1表示没有此玩家
        self.score = [-1,-1,-1]

    def setup(self, *args):
        self.how_to_play()
        self.how_tank_look()
        self.choose_player_num()
        self.finished = False
        self.next = 'load_screen'

    def choose_player_num(self):
        two_players = Button((250, 550, 200, 50), (255, 0, 0), "1 V 1")
        three_players = Button((800, 550, 200, 50), (0, 0, 255), "1 V 1 V 1")
        self.buttons = [two_players, three_players]

    # 玩法
    def how_to_play(self):
        self.player_methods = []
        self.player_methods.append(
            (tools.create_textImg('PLAYER 1', 35, color=C.RED), (C.PLAYER1_X, C.PLAYER1_Y)))
        self.player_methods.append(
            (tools.create_textImg('WASD FIRE: Q', 35, color=C.RED), (0.15*C.SCREEN_W+C.PLAYER1_X, C.PLAYER1_Y)))
        self.player_methods.append(
            (tools.create_textImg('PLAYER 2', 35, color=C.GREEN), (C.PLAYER1_X, 0.1*C.SCREEN_H+C.PLAYER1_Y)))
        self.player_methods.append(
            (tools.create_textImg('IJKL FIRE: U', 35, color=C.GREEN), (0.15*C.SCREEN_W+C.PLAYER1_X, 0.1*C.SCREEN_H+C.PLAYER1_Y)))
        self.player_methods.append(
            (tools.create_textImg('PLAYER 3', 35, color=C.BLUE), (C.PLAYER1_X, 0.2*C.SCREEN_H+C.PLAYER1_Y)))
        self.player_methods.append(
            (tools.create_textImg('DIRECT FIRE: DEL', 35, color=C.BLUE), (0.15*C.SCREEN_W+C.PLAYER1_X, 0.2*C.SCREEN_H+C.PLAYER1_Y)))

    # 坦克的样子
    def how_tank_look(self):
        self.tank_p1 = pygame.sprite.Sprite()
        self.tank_p1.image = tools.create_image(
            setup.GRAPHICS['red'], 0, 0, C.PLAYER_PY, C.PLAYER_PX, C.CURSOR_MULTI)
        rect = self.tank_p1.image.get_rect()
        rect.x, rect.y = (0.57*C.SCREEN_W+C.PLAYER1_X -
                          rect.w/2, C.PLAYER1_Y-rect.h/2)
        self.tank_p1.rect = rect
        
        self.tank_p2 = pygame.sprite.Sprite()
        self.tank_p2.image = tools.create_image(
            setup.GRAPHICS['green'], 0, 0, C.PLAYER_PY, C.PLAYER_PX, C.CURSOR_MULTI)
        rect = self.tank_p2.image.get_rect()
        rect.x, rect.y = (0.57*C.SCREEN_W+C.PLAYER1_X-rect.w/2,
                          0.1*C.SCREEN_H+C.PLAYER1_Y-rect.h/2)
        self.tank_p2.rect = rect

        self.tank_p3 = pygame.sprite.Sprite()
        self.tank_p3.image = tools.create_image(
            setup.GRAPHICS['blue'], 0, 0, C.PLAYER_PY, C.PLAYER_PX, C.CURSOR_MULTI)
        rect = self.tank_p3.image.get_rect()
        rect.x, rect.y = (0.57*C.SCREEN_W+C.PLAYER1_X-rect.w/2,
                          0.2*C.SCREEN_H+C.PLAYER1_Y-rect.h/2)
        self.tank_p3.rect = rect

    def show_tanks(self, surface, keys):
        surface.blit(self.tank_p1.image, self.tank_p1.rect)
        surface.blit(self.tank_p2.image, self.tank_p2.rect)
        surface.blit(self.tank_p3.image, self.tank_p3.rect)

    def show_caption(self, surface):
        caption = pygame.Surface((629, 71))
        caption.blit(setup.GRAPHICS['caption'], (0, 0), (0, 0, 629, 71))
        for y in range(caption.get_height()):
            for x in range(caption.get_width()):
                pixel_color = caption.get_at((x, y))
                if 100 <= pixel_color[1] and 100 <= pixel_color[2]:
                    caption.set_at((x, y), (255, 255, 255, 0))
        caption.set_colorkey(C.WHITE)
        rect = caption.get_rect()
        rect.x, rect.y = 350, 110
        surface.blit(caption, rect)

    def update(self, surface, keys):
        surface.blit(
            pygame.transform.scale(setup.GRAPHICS['background'], (surface.get_width(), surface.get_height())), (0,0))
        # 展示游戏标题
        self.show_caption(surface)
        # 展示玩法
        for method in self.player_methods:
            surface.blit(method[0], method[1])     
        # 展示坦克
        self.show_tanks(surface, keys)
        # 选择玩家人数
        for index, button in enumerate(self.buttons):
            button.draw(surface)
            if button.clicked:
                self.player_num = index + 2
                for i in range(self.player_num):
                    self.score[i] = 0
                self.finished = True