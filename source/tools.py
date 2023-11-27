import pygame
import sys
import os
from . import constants as C

class Game:
    def __init__(self, interface_dict, start_interface):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.keys = pygame.key.get_pressed()
        self.interface_dict = interface_dict
        self.state = self.interface_dict[start_interface]

    def update(self):
        if self.state.finished:
            player_num = self.state.player_num
            # 这个score是个数组，指的是玩家的得分
            score = self.state.score
            next_state = self.state.next
            self.state = self.interface_dict[next_state]
            self.state.load(player_num, score)

        self.state.update(self.screen, self.keys)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN: # 按下
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP: # 松开
                    self.keys = pygame.key.get_pressed()
                elif self.state == self.interface_dict['main_menu']:
                    for button in self.state.buttons:
                        button.handle_event(event)

            self.update()
            pygame.display.update() # 将之前绘制的图形更新到屏幕上

def load_graphics(path):
    graphics = {}
    for pic in os.listdir(path):
        name, ext = os.path.splitext(pic)
        img = pygame.image.load(os.path.join(path, pic))
        img = img.convert()
        graphics[name] = img
    return graphics

def load_sounds(path):
    sounds = {}
    for sound in os.listdir(path):
        name, ext = os.path.splitext(sound)
        asound = pygame.mixer.Sound(os.path.join(path, sound))
        sounds[name] = asound
    return sounds

def create_image(sheet, x, y, width, height, scale):
    image = pygame.Surface((width, height))
    # blit三个参数分别为源图像，目标位置，要复制的图像区域
    image.blit(sheet, (0, 0), (x, y, width, height))
    # 把图片旁边的白色设置为透明
    image.set_colorkey(C.white)
    image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
    return image

# 创建文本图像
def create_textImg(text, size=40, color=C.black, width_ratio=1.25, height_ratio=1):
    font = pygame.font.SysFont(C.font, size)
    text_image = font.render(text, 1, color) # 文本转为图像
    rect = text_image.get_rect()
    # 缩放
    text_image = pygame.transform.scale(text_image, (int(rect.width*width_ratio), int(rect.height*height_ratio))) 
    return text_image