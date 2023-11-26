import pygame
import numpy
import random
from .. import setup, tools, constants as C
from . import cell, bullet


class Bullet(pygame.sprite.Sprite):
    # theta表示子弹初始角度，s表示子弹大小，v：速度，t：存在时间，battlefiled用于拿到上个状态的一些变量,player用于拿到玩家的一些变量
    def __init__(self, x, y, theta, s, v, t, battlefield, player):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.theta = theta
        self.vx = v*C.bullet_base_v*numpy.cos(self.theta)
        self.vy = v*C.bullet_base_v*numpy.sin(self.theta)
        self.time = t*C.bullet_max_exist_time
        self.exist_timer = 0
        self.protection = True
        self.last_hit = None
        self.size = s
        self.battlefield = battlefield
        self.player = player
        self.load_image()

    def load_image(self):
        self.image = tools.create_image(
            setup.GRAPHICS['round'], 0, 0, C.bullet_pic_size_x, C.bullet_pic_size_y, self.size)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x/C.real_to_virtual,
                            self.y/C.real_to_virtual)

    def update_collisions(self):
        if self.exist_timer == 0:
            self.exist_timer = self.player.battlefield.clock

        cells_idx = cell.calculate_cell_num(
            self.rect.center[0], self.rect.center[1])
        for i in range(0, 4):
            for wall in self.battlefield.cells[cells_idx[i]].walls:
                if pygame.sprite.collide_rect(self, wall):
                    if self.player.battlefield.clock-self.exist_timer >= self.time:
                        self.go_die()
                        return

                    if self.last_hit != None and self.last_hit is wall:
                        return
                    self.last_hit = wall
                    self.protection = False
                    if abs(wall.rect.top-self.rect.bottom) <= C.is_collided and self.vy > 0:
                        self.vy *= -1
                        return
                    if abs(wall.rect.bottom-self.rect.top) <= C.is_collided and self.vy < 0:
                        self.vy *= -1
                        return
                    if abs(wall.rect.right-self.rect.left) <= C.is_collided and self.vx < 0:
                        self.vx *= -1
                        return
                    if abs(wall.rect.left-self.rect.right) <= C.is_collided and self.vx > 0:
                        self.vx *= -1
                        return
    
    def update_hit(self):
        for aplayer in self.battlefield.players:
            if self.protection and aplayer is self.player:
                continue
            if abs(self.x-aplayer.x)/C.real_to_virtual > C.player_scale_x or abs(self.y-aplayer.y)/C.real_to_virtual > C.player_scale_x:
                continue
            hitbox = pygame.sprite.spritecollideany(
                self, aplayer.hitboxes)
            if hitbox:
                aplayer.go_die()
                self.go_die()
                return

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x/C.real_to_virtual,
                            self.y/C.real_to_virtual)
        self.update_collisions()
        self.update_hit()

    def go_die(self):
        self.player.round_num -= 1
        self.kill()


class Big_Bullet(Bullet):
    def __init__(self, x, y, theta, s, v, t, battlefield, player):
        Bullet.__init__(self, x, y, theta, s, v, t, battlefield, player)

    def go_die(self):
        setup.SOUNDS['fire'+str(int(random.random()*4+1))].play()
        for i in range(30):
            self.player.rounds.add(Fragment(x=self.x, y=self.y, theta=random.random()*2*C.PI,
                                            s=0.7, v=1.5, t=0.05, battlefield=self.battlefield, player=self.player))
        self.kill()

    def update_collisions(self):
        if self.exist_timer == 0:
            self.exist_timer = self.player.battlefield.clock
        if self.player.battlefield.clock-self.exist_timer >= self.time:
            self.go_die()
            return
        cells_idx = cell.calculate_cell_num(
            self.rect.center[0], self.rect.center[1])
        for i in range(0, 4):
            for wall in self.battlefield.cells[cells_idx[i]].walls:
                if pygame.sprite.collide_rect(self, wall):
                    if self.last_hit != None and self.last_hit is wall:
                        return
                    self.last_hit = wall
                    self.protection = False
                    if abs(wall.rect.top-self.rect.bottom) <= C.is_collided and self.vy > 0:
                        self.vy *= -1
                        return
                    if abs(wall.rect.bottom-self.rect.top) <= C.is_collided and self.vy < 0:
                        self.vy *= -1
                        return
                    if abs(wall.rect.right-self.rect.left) <= C.is_collided and self.vx < 0:
                        self.vx *= -1
                        return
                    if abs(wall.rect.left-self.rect.right) <= C.is_collided and self.vx > 0:
                        self.vx *= -1
                        return


class Fragment(Bullet):
    def __init__(self, x, y, theta, s, v, t, battlefield, player):
        Bullet.__init__(self, x, y, theta, s, v, t, battlefield, player)
        self.protection = False

    def update_collisions(self):
        if self.exist_timer == 0:
            self.exist_timer = self.player.battlefield.clock
        if self.player.battlefield.clock-self.exist_timer >= self.time:
            self.go_die()
            return
        cells_idx = cell.calculate_cell_num(
            self.rect.center[0], self.rect.center[1])
        for i in range(0, 4):
            for wall in self.battlefield.cells[cells_idx[i]].walls:
                if pygame.sprite.collide_rect(self, wall):
                    if self.last_hit != None and self.last_hit is wall:
                        return
                    self.last_hit = wall
                    self.protection = False
                    if abs(wall.rect.top-self.rect.bottom) <= C.is_collided and self.vy > 0:
                        self.vy *= -1
                        return
                    if abs(wall.rect.bottom-self.rect.top) <= C.is_collided and self.vy < 0:
                        self.vy *= -1
                        return
                    if abs(wall.rect.right-self.rect.left) <= C.is_collided and self.vx < 0:
                        self.vx *= -1
                        return
                    if abs(wall.rect.left-self.rect.right) <= C.is_collided and self.vx > 0:
                        self.vx *= -1
                        return

    def go_die(self):
        self.kill()


def Shot_Gun(x, y, theta, s, v, t, battlefield, player):
    for i in range(20):
        player.rounds.add(Shot_Gun_Fragment(
            x=x, y=y, theta=theta+(random.random()-0.5)*C.PI/6,
            s=s, v=v, t=t, battlefield=battlefield, player=player))


class Shot_Gun_Fragment(Bullet):
    def __init__(self, x, y, theta, s, v, t, battlefield, player):
        Bullet.__init__(self, x, y, theta, s, v, t, battlefield, player)

    def go_die(self):
        self.kill()