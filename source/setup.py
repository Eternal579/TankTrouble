import pygame
from . import constants as C
from . import tools

pygame.init()
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.display.set_caption('TANK TROUBLE PYTHON EDITION')
pygame.display.set_mode((C.screen_width, C.screen_height))
GRAPHICS = tools.load_graphics('resources/graphics')
pygame.display.set_icon(tools.create_image(
    GRAPHICS['icon'], 7, 0, 27, 41, C.tank_zoom_rate))
SOUNDS = tools.load_sounds('resources/sounds')