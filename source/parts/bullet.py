import pygame
import numpy
import random
from .. import setup, tools, constants as C
from . import cell, bullet


class Bullet(pygame.sprite.Sprite):
    # theta表示子弹初始角度，s表示子弹大小，v：速度，time_rate：表示存活时间的rate，battlefiled用于拿到上个状态的一些变量，player表示发射子弹的玩家
    def __init__(self, x, y, theta, s, v, time_rate, battlefield, player):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.theta = theta
        # x轴方向速度分量
        self.vx = v*C.bullet_base_v*numpy.cos(self.theta)
        self.vy = v*C.bullet_base_v*numpy.sin(self.theta)
        self.max_exist_time = time_rate*C.bullet_max_exist_time
        self.launch_time = 0
        # 防止炸膛
        self.protection = True
        self.last_wall = None
        self.size = s
        self.battlefield = battlefield
        self.player = player
        self.load_image()

    def load_image(self):
        self.image = tools.create_image(setup.GRAPHICS['bullet'], 0, 0, C.bullet_pic_size_x, C.bullet_pic_size_y, self.size)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x / C.real_to_virtual, self.y / C.real_to_virtual)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x / C.real_to_virtual, self.y / C.real_to_virtual)
        self.detect_collisions()
        self.update_hit()

    def detect_collisions(self):
        if self.launch_time == 0:
            self.launch_time = self.player.battlefield.clock

        cell_index = cell.which_cells_by_tankpos(self.rect.center[0], self.rect.center[1])
        # 处理坦克与墙之间的碰撞
        for i in cell_index:
            # 遍历这个cell的所有墙
            for wall in self.battlefield.cells[i].walls:
                # 如果子弹撞墙了
                if pygame.sprite.collide_rect(self, wall):
                    if self.player.battlefield.clock - self.launch_time >= self.max_exist_time:
                        self.go_die()
                        return

                    # 由于连续帧中又重复碰撞，需要加上下面这段话防止多次处理相同时间
                    if self.last_wall != None and self.last_wall is wall:
                        return

                    self.last_wall = wall
                    self.protection = False
                    # 撞到上或下了
                    if abs(wall.rect.top - self.rect.bottom) <= C.is_collided and self.vy > 0 or \
                       abs(wall.rect.bottom-self.rect.top) <= C.is_collided and self.vy < 0:
                        self.vy *= -1
                        return
                    # 撞到左或右了
                    if abs(wall.rect.right-self.rect.left) <= C.is_collided and self.vx < 0 or \
                       abs(wall.rect.left-self.rect.right) <= C.is_collided and self.vx > 0:
                        self.vx *= -1
                        return

    def update_hit(self):
        # 遍历战场上的所有玩家
        for single_player in self.battlefield.players:
            # 下面这段是用来防止刚开出去的子弹把自己炸死了
            if self.protection and single_player is self.player:
                continue
            if pygame.sprite.spritecollideany(self, single_player.collision_v_s):
                single_player.go_die()
                self.go_die()
                return

    def go_die(self):
        self.player.bullet_num -= 1
        self.kill()

class Big_Bullet(Bullet):
    def __init__(self, x, y, theta, s, v, time_rate, battlefield, player):
        Bullet.__init__(self, x, y, theta, s, v, time_rate, battlefield, player)

def Shot_Gun(x, y, theta, s, v, time_rate, battlefield, player):
    for i in range(20):
        player.bullets.add(Bullet(x=x, y=y, theta=theta+(random.random()-0.5)*C.PI/6,
            s=s, v=v, time_rate=time_rate, battlefield=battlefield, player=player))
