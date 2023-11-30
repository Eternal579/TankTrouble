import pygame
import sys
import os
import globals as G

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
    image.set_colorkey(G.white)
    image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
    return image

# 创建文本图像
def create_textImg(text, size=40, color=G.black, width_ratio=1.25, height_ratio=1):
    font = pygame.font.SysFont(G.font, size)
    text_image = font.render(text, 1, color) # 文本转为图像
    rect = text_image.get_rect()
    # 缩放
    text_image = pygame.transform.scale(text_image, (int(rect.width*width_ratio), int(rect.height*height_ratio))) 
    return text_image

pygame.init()
pygame.display.set_caption('TANK TROUBLE')
pygame.display.set_mode((G.screen_width, G.screen_height))
pics = load_graphics('../resources/pics')
audios = load_sounds('../resources/audios')
pygame.display.set_icon(create_image(pics['red_s'], 0, 0, 27, 41, 1))
