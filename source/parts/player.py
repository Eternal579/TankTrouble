import pygame
import numpy
import random
from .. import tools, setup, constants as C
from . import bullet, cell, particles


class player(pygame.sprite.Sprite):
    def __init__(self, id, battlefield):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.battlefield = battlefield
        
        # 一些玩的时候的标识状态的变量
        self.fire = False
        self.fire_timer = 0
        self.fire_cool_down_timer = 0
        self.is_stucked = False
        self.moving = False
        self.when_stucked = 0
        self.dead = False
        self.can_fire = True
        self.shotgun = False
        self.biground = False
        self.random = 0
        self.x = 0
        self.y = 0
        # 以水平向右为0，顺时针方向为正
        self.theta = 0
        self.bullet_num = 0
        self.exploding = False
        self.bullets = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        self.init_collision_v_s()
        self.load_material()

    def init_collision_v_s(self):
        self.collision_v_s = pygame.sprite.Group()
        self.all_collision_detect_pos = []
        # 以坦克中心为坐标原点，构建极坐标系
        # 下面的(x,y)表示坦克右下角,坦克大小是41*27
        x = C.player_scale_x * C.play_zoom_rate / 2
        y = -C.player_scale_y * C.play_zoom_rate / 2
        # d仅仅作为一个步长
        d = C.player_scale_x * C.play_zoom_rate / 12
        # 构建碰撞方块的宽
        for i in range(8):
            r = numpy.sqrt(x**2+y**2)
            alpha = numpy.arccos(x/r)
            if y < 0: # 顺时针为负
                alpha = -alpha
            self.all_collision_detect_pos.append((r, alpha))
            # 加个Π表示关于坐标原点对称的点
            self.all_collision_detect_pos.append((r, C.PI + alpha))
            y += d
        x = C.player_scale_x*C.play_zoom_rate/2
        y = C.player_scale_y*C.play_zoom_rate/2
        # 构建碰撞体积的长
        for i in range(11):
            r = numpy.sqrt(x**2+y**2)
            alpha = numpy.arccos(x/r)
            self.all_collision_detect_pos.append((r, alpha))
            self.all_collision_detect_pos.append((r, C.PI + alpha))
            x += -d

    def load_material(self):
        if self.id == 1:
            self.image = tools.create_image(
                setup.GRAPHICS['red'], 0, 0, C.player_scale_y, C.player_scale_x, C.play_zoom_rate)
            self.fire_image = tools.create_image(
                setup.GRAPHICS['red_s'], 0, 0, C.player_scale_y, C.player_scale_x, C.play_zoom_rate)
        elif self.id == 2:
            self.image = tools.create_image(
                setup.GRAPHICS['green'], 0, 0, C.player_scale_y, C.player_scale_x, C.play_zoom_rate)
            self.fire_image = tools.create_image(
                setup.GRAPHICS['green_s'], 0, 0, C.player_scale_y, C.player_scale_x, C.play_zoom_rate)
        elif self.id == 3:
            self.image = tools.create_image(
                setup.GRAPHICS['blue'], 0, 0, C.player_scale_y, C.player_scale_x, C.play_zoom_rate)
            self.fire_image = tools.create_image(
                setup.GRAPHICS['blue_s'], 0, 0, C.player_scale_y, C.player_scale_x, C.play_zoom_rate)
        self.tank_state_img = self.image

    def update(self, keys):
        self.random = self.battlefield.random
        self.bullets.update()
        if not self.dead:
            # 更新坦克位置
            self.update_position(keys)
            # 更新完位置后千万不要忘了更新碰撞组
            self.calculate_collision_v_s()
            # 更新开火状态
            self.update_fire(keys)
            # 更新坦克状态图
            self.update_image()
            if self.moving:
                # 检测是否发生碰撞
                self.detect_collision()
                self.update_moving_particles()

    def prevent_tank_stuck_out_wall(self):
        # 以下代码主要是防止一些意外导致坦克被卡出外墙，以下情况很少发生
        if self.x / C.real_to_virtual < C.left_space:
            # print("##############")
            # print(self.x)
            # print(C.left_space)
            # print("##############")
            self.x = (C.cell_size/2+C.left_space)*C.real_to_virtual
        if self.y/C.real_to_virtual < C.top_space:
            # print("##############")
            # print(self.y)
            # print(C.top_space)
            # print("##############")
            self.y = (C.cell_size/2+C.top_space)*C.real_to_virtual
        if self.x/C.real_to_virtual > C.left_space+C.cell_column_num*C.cell_size:
            # print("##############")
            # print(self.x)
            # print(C.left_space+C.cell_column_num*C.cell_size)
            # print("##############")
            self.x = (C.left_space+(C.cell_column_num-0.5) *
                      C.cell_size)*C.real_to_virtual
        if self.y/C.real_to_virtual > C.top_space+C.cell_row_num*C.cell_size:
            # print("##############")
            # print(self.y)
            # print(C.top_space+C.cell_row_num*C.cell_size)
            # print("##############")
            self.y = (C.top_space+(C.cell_row_num-0.5) *
                      C.cell_size)*C.real_to_virtual

    # 对按键输入作出反应，使坦克运动
    def update_position(self, keys):
        self.prevent_tank_stuck_out_wall()

        self.moving = False

        key_mapping_1 = {
            pygame.K_w: (C.tank_base_v, 0),  # (移动速度, 角度调整)
            pygame.K_s: (-C.tank_back_v, 0),
            pygame.K_a: (0, -C.tank_turn_base_w),
            pygame.K_d: (0, C.tank_turn_base_w)
        }
        key_mapping_2 = {
            pygame.K_i: (C.tank_base_v, 0),
            pygame.K_k: (-C.tank_back_v, 0),
            pygame.K_j: (0, -C.tank_turn_base_w),
            pygame.K_l: (0, C.tank_turn_base_w),
        }
        key_mapping_3 = {
            pygame.K_UP: (C.tank_base_v, 0),
            pygame.K_DOWN: (-C.tank_back_v, 0),
            pygame.K_LEFT: (0, -C.tank_turn_base_w),
            pygame.K_RIGHT: (0, C.tank_turn_base_w),
        }
        if self.id == 1:
           for key in key_mapping_1:
                if keys[key]:
                    self.moving = True
                    move_speed, angle_adjustment = key_mapping_1[key]
                    self.x += move_speed * (not self.is_stucked) * numpy.cos(self.theta)
                    self.y += move_speed * (not self.is_stucked) * numpy.sin(self.theta)
                    self.theta += (not self.is_stucked) * angle_adjustment
        elif self.id == 2:
            for key in key_mapping_2:
                if keys[key]:
                    self.moving = True
                    move_speed, angle_adjustment = key_mapping_2[key]
                    self.x += move_speed * (not self.is_stucked) * numpy.cos(self.theta)
                    self.y += move_speed * (not self.is_stucked) * numpy.sin(self.theta)
                    self.theta += (not self.is_stucked) * angle_adjustment
        elif self.id == 3:
            for key in key_mapping_3:
                if keys[key]:
                    self.moving = True
                    move_speed, angle_adjustment = key_mapping_3[key]
                    self.x += move_speed * numpy.cos(self.theta) * (not self.is_stucked)
                    self.y += move_speed * numpy.sin(self.theta) * (not self.is_stucked)
                    self.theta += angle_adjustment * (not self.is_stucked)

        # 确保 self.theta 的值在 0 到 2π 之间
        self.theta = self.theta % (2 * C.PI)

    def update_fire(self, keys):
        # 每间隔0.2s可以发射子弹一次
        if not self.can_fire and self.battlefield.clock - self.fire_cool_down_timer >= C.fire_interval:
            self.can_fire = True

        flag = False
        if self.id == 1 and keys[pygame.K_q]:
            flag = True
        if self.id == 2 and keys[pygame.K_u]:
            flag = True
        if self.id == 3 and keys[pygame.K_DELETE]:
            flag = True
        if flag and self.can_fire and not self.fire: 
            # 霰弹枪和大子弹是不算在每次最多5颗子弹之内的
            if self.bullet_num < C.bullet_exist_num or self.shotgun or self.biground:
                self.fire = True # 在这里self.fire被设置为true会让坦克进入开枪状态图
                self.fire_timer = self.battlefield.clock # 不要忘了更新开火时间

        if self.fire:
            self.can_fire = False
            self.fire_cool_down_timer = self.battlefield.clock
            if self.battlefield.clock - self.fire_timer >= C.fire_state_sustain_time:
                setup.SOUNDS['fire'].play()

                if self.shotgun:
                    bullet.Shot_Gun(self.x+0.32*C.v_player_scale_x*numpy.cos(self.theta), self.y + 0.32*C.v_player_scale_y*numpy.sin(
                        self.theta), theta=self.theta, s=0.7, v=1.4, t=0.08, battlefield=self.battlefield, player=self)
                    self.shotgun = False

                elif self.biground:
                    self.bullets.add(bullet.Big_Bullet(x=self.x+0.32*C.v_player_scale_x*numpy.cos(self.theta), y=self.y+0.32*C.v_player_scale_y * numpy.sin(self.theta),
                                                    theta=self.theta, s=1.5, v=1.4, t=0.11, battlefield=self.battlefield, player=self))
                    self.biground = False

                else:
                    self.bullets.add(bullet.Bullet(x=self.x+0.32*C.v_player_scale_x*numpy.cos(self.theta),
                                    y=self.y+0.32*C.v_player_scale_y*numpy.sin(self.theta),
                                    theta=self.theta, s=1, v=1, t=1,
                                    battlefield=self.battlefield, player=self))
                    self.bullet_num += 1

                self.fire = False # 在这里被设置为false，使坦克退出开枪状态

    def update_image(self):
        # 1.5PI的原因是材料图是竖直向上的，所以是1.5PI
        cur_angle = (1.5 * C.PI - self.theta) / C.PI * 180
        if self.fire:
            self.tank_state_img = pygame.transform.rotate(self.fire_image, cur_angle)
        else:
            self.tank_state_img = pygame.transform.rotate(self.image, cur_angle)

    def calculate_collision_v_s(self):
        self.collision_v_s.empty()
        for pos in self.all_collision_detect_pos:
            collision_v = pygame.sprite.Sprite()
            collision_v.image = pygame.Surface((C.player_scale_x / 12, C.player_scale_x / 12)).convert()
            collision_v.rect = collision_v.image.get_rect()
            # 不要忘记加上self.theta
            collision_v.rect.center = (pos[0] * numpy.cos(pos[1] + self.theta) + self.x / C.real_to_virtual, pos[0] * numpy.sin(pos[1] + self.theta) + self.y / C.real_to_virtual)
            self.collision_v_s.add(collision_v)

    def detect_collision(self):
        # 获取坦克现在所在位置的cell下标
        cell_index = cell.calculate_cell_num(self.x / C.real_to_virtual, self.y / C.real_to_virtual)
        self.is_stucked = False
        # 处理坦克与墙之间的碰撞
        for i in cell_index:
            # 遍历这个cell的所有墙
            for wall in self.battlefield.cells[i].walls:
                # 如果碰撞到墙，则让is_stucked为True，这样坦克就无法移动
                # which_collision_v表示哪个小矩形碰到了
                which_collision_v = pygame.sprite.spritecollideany(wall, self.collision_v_s)
                if which_collision_v:
                    #print(which_collision_v.rect)
                    self.is_stucked = True
                    # 调节位置后坦克便可移动
                    self.adjust_position(which_collision_v, 0.1, True)
                    return
        
        self.when_stucked = self.battlefield.clock

        # # 处理坦克与坦克之间的碰撞
        # for player in self.battlefield.players:
        #     if player is self:
        #         continue
        #     if abs(player.x-self.x)/C.real_to_virtual > C.player_scale_x or abs(player.y-self.y)/C.real_to_virtual > C.player_scale_x:
        #         continue
        #     for self_hitbox in self.collision_v_s:
        #         collision_v = pygame.sprite.spritecollideany(
        #             self_hitbox, player.collision_v_s)
        #         if collision_v:
        #             self.is_stucked = True
        #             self.adjust_position(collision_v, 1, False)
        #             return

    def adjust_position(self, collision_v, k, time_matters):
        x = collision_v.rect.center[0] - self.x / C.real_to_virtual
        y = collision_v.rect.center[1] - self.y / C.real_to_virtual
        alpha = numpy.arccos(x / numpy.sqrt(x**2 + y**2))
        # y < 0表示向上撞得
        if y < 0:
            alpha = -alpha

        if (time_matters):
            self.x -= numpy.cos(alpha-self.theta)*min((self.battlefield.clock-self.when_stucked), 10)*k * \
                C.real_to_virtual * \
                numpy.cos(self.theta) + (self.random-0.5) * \
                (self.battlefield.clock-self.when_stucked)
            self.y -= numpy.cos(alpha-self.theta)*min(0.1*(self.battlefield.clock-self.when_stucked), 10)*k * \
                C.real_to_virtual * \
                numpy.sin(self.theta) + (random.random()-0.5) * \
                (self.battlefield.clock-self.when_stucked)
            self.x -= numpy.sin(alpha-self.theta) * min((self.battlefield.clock-self.when_stucked), 100)*k * \
                C.real_to_virtual*-numpy.sin(self.theta)
            self.y -= numpy.sin(alpha-self.theta) * min((self.battlefield.clock-self.when_stucked), 100)*k * \
                C.real_to_virtual*numpy.cos(self.theta)
        else:
            self.x -= numpy.cos(alpha-self.theta)*k * \
                C.real_to_virtual * \
                numpy.cos(self.theta) + (self.random-0.5) * \
                (self.battlefield.clock-self.when_stucked)
            self.y -= numpy.cos(alpha-self.theta)*k * \
                C.real_to_virtual * \
                numpy.sin(self.theta) + (random.random()-0.5) * \
                (self.battlefield.clock-self.when_stucked)
            self.x -= numpy.sin(alpha-self.theta) * k * \
                C.real_to_virtual*-numpy.sin(self.theta)
            self.y -= numpy.sin(alpha-self.theta) * k * \
                C.real_to_virtual*numpy.cos(self.theta)

    def go_die(self):
        setup.SOUNDS['explosion'].play()
        self.collision_v_s.empty()

        self.dead = True
        self.battlefield.rest_player_num -= 1
        self.battlefield.end_time = self.battlefield.clock

        if self.id == 1:
            color = C.red
        elif self.id == 2:
            color = C.green
        elif self.id == 3:
            color = C.blue

        self.particles.add(particles.Particles(
            20, (C.gray, C.dark_gray, color), 9, self.x, self.y, 0, 0, 6, 6))
        self.exploding = True

    def update_moving_particles(self):
        if self.is_stucked and random.randint(1, 2) == 1:
            sign = int(self.random+0.5)*2-1
            self.particles.add(particles.Particles(
                1, (C.gray, C.dark_gray, C.black), 6, (self.x+sign*0.4*C.player_scale_y*C.real_to_virtual*numpy.sin(self.theta))-0.4*C.player_scale_x*C.real_to_virtual*numpy.cos(
                    self.theta), (self.y-sign*0.4*C.player_scale_y*C.real_to_virtual*numpy.cos(self.theta))-0.4*C.player_scale_x*C.real_to_virtual*numpy.sin(self.theta),
                -numpy.cos(self.theta), -numpy.sin(self.theta), 0.8, 0.8))
            return
        if self.moving and random.randint(1, 64) == 1:
            sign = int(self.random+0.5)*2-1
            self.particles.add(particles.Particles(
                1, (C.gray, C.dark_gray), 4, (self.x+sign*0.4*C.player_scale_y*C.real_to_virtual*numpy.sin(self.theta))-0.4*C.player_scale_x*C.real_to_virtual*numpy.cos(
                    self.theta), (self.y-sign*0.4*C.player_scale_y*C.real_to_virtual*numpy.cos(self.theta))-0.4*C.player_scale_x*C.real_to_virtual*numpy.sin(self.theta),
                -numpy.cos(self.theta), -numpy.sin(self.theta), 0.8, 0.8))

    def celebrate(self):
        setup.SOUNDS['fire'].play()
        self.particles.add(particles.Particles(
            20, (C.purple, C.red, C.yellow), 6, self.x+0.32*C.player_scale_x*C.real_to_virtual*numpy.cos(
                self.theta), self.y+0.32*C.player_scale_x*C.real_to_virtual*numpy.sin(self.theta),
            numpy.cos(self.theta), numpy.sin(self.theta), 12, 2))

    def draw(self, surface):
        if not self.dead:
            surface.blit(self.tank_state_img, self.tank_state_img.get_rect(
                center=(self.x/C.real_to_virtual, self.y/C.real_to_virtual)))
        self.bullets.draw(surface)
        self.particles.update(surface)