import pygame
import numpy
import random
import utils, cell, globals as G


class Bullet(pygame.sprite.Sprite):
    # theta表示子弹初始角度，s表示子弹大小，v：速度，time_rate：表示存活时间的rate
    # battlefiled用于拿到上个状态的一些变量，player表示发射子弹的玩家
    def __init__(self, x, y, theta, s, v, time_rate, battlefield, player):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.theta = theta
        # x轴方向速度分量
        self.vx = v*G.bullet_base_v*numpy.cos(self.theta)
        self.vy = v*G.bullet_base_v*numpy.sin(self.theta)
        # 子弹最大存活时间
        self.max_exist_time = time_rate*G.bullet_max_exist_time
        # 发射时间
        self.launch_time = 0
        # 防止子弹刚发射的一帧后就被判定为与坦克碰撞，导致产生“炸膛”的效果
        self.protection = True
        # 子弹上次碰到的墙体，同样是由于多帧问题被认为重复碰撞，
        self.last_wall = None
        # 子弹大小
        self.size = s
        self.battlefield = battlefield
        self.player = player
        self.load_image()

    def load_image(self):
        self.image = utils.create_image(utils.pics['bullet'], 0, 0, G.bullet_pic_size_x, G.bullet_pic_size_y, self.size)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x / G.real_to_virtual, self.y / G.real_to_virtual)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x / G.real_to_virtual, self.y / G.real_to_virtual)
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
                    if abs(wall.rect.top - self.rect.bottom) <= G.is_collided and self.vy > 0 or \
                       abs(wall.rect.bottom-self.rect.top) <= G.is_collided and self.vy < 0:
                        self.vy *= -1
                        return
                    # 撞到左或右了
                    if abs(wall.rect.right-self.rect.left) <= G.is_collided and self.vx < 0 or \
                       abs(wall.rect.left-self.rect.right) <= G.is_collided and self.vx > 0:
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
        player.bullets.add(Bullet(x=x, y=y, theta=theta+(random.random()-0.5)*G.PI/6,
            s=s, v=v, time_rate=time_rate, battlefield=battlefield, player=player))
        
class Laser(Bullet):
    def __init__(self, x, y, theta, s, v, time_rate, battlefield, player):
        Bullet.__init__(self, x, y, theta, s, v, time_rate, battlefield, player)

    def load_image(self):
        cur_angle = (1.5 * G.PI - self.player.theta) / G.PI * 180
        if self.player.id == 1:
            color = 'red_laser'
        elif self.player.id == 2:
            color = 'green_laser'
        elif self.player.id == 3:
            color = 'blue_laser'
        self.image = utils.create_image(utils.pics[color], 0, 0, G.laser_pic_size_x, G.laser_pic_size_y, self.size)
        self.image = pygame.transform.rotate(self.image, cur_angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x / G.real_to_virtual, self.y / G.real_to_virtual)

    def detect_collisions(self):
        if self.launch_time == 0:
            self.launch_time = self.player.battlefield.clock
