import pygame
import random
from .. import setup, tools, constants as C


class Prop(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        # if random.randint(0, 1):
        #     self.type = 1
        #     self.image = tools.create_image(
        #         setup.GRAPHICS['shotgun'], 0, 0, 17, 17, 1)
        #     self.rect = self.image.get_rect()
        #     self.rect.center = center
        # else:
        self.type = 0
        self.image = tools.create_image(
            setup.GRAPHICS['biground'], 0, 0, 17, 17, 1)
        self.rect = self.image.get_rect()
        self.rect.center = center