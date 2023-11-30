import pygame
import random
import utils


class Prop(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        res = random.randint(0, 2)
        if res == 0:
            self.type = 0
            self.image = utils.create_image(
                utils.pics['shotgun'], 0, 0, 17, 17, 1)
            self.rect = self.image.get_rect()
            self.rect.center = center
        elif res == 1:
            self.type = 1
            self.image = utils.create_image(
                utils.pics['biground'], 0, 0, 17, 17, 1)
            self.rect = self.image.get_rect()
            self.rect.center = center
        elif res == 2:
            self.type = 2
            self.image = utils.create_image(
                utils.pics['red_laser'], 0, 0, 19, 45, 1)
            self.rect = self.image.get_rect()
            self.rect.center = center
