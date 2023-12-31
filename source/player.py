import pygame
import numpy
import random
import utils, globals as G
import bullet, cell


class player(pygame.sprite.Sprite):
    def __init__(self, id, battlefield):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.battlefield = battlefield
        
        # 一些玩的时候的标识状态的变量
        # 三种子弹类型
        self.shotgun = False
        self.bigbullet = False
        self.laser = False
        # 开火状态，self.fire被设置为true会让坦克进入开火状态图
        self.fire = False
        # 开火时间，用于决定是否退出开火状态图
        self.fire_timer = 0
        # 用于决定能否开火
        self.fire_cool_down_timer = 0
        self.can_fire = True
        # 用于判断坦克是否能动
        self.is_stucked = False
        self.when_stucked = 0
        self.moving = False
        self.dead = False
        self.random = 0
        self.x = 0
        self.y = 0
        # 以水平向右为0，顺时针方向为正，顺时针为正的原因是因为像素点坐标的y是向下变大的
        self.theta = 0
        self.bullet_num = 0
        self.boom = False
        self.bullets = pygame.sprite.Group()

        self.init_collision_v_s()
        self.load_material()

    def init_collision_v_s(self):
        self.collision_v_s = pygame.sprite.Group()
        self.all_collision_detect_pos = []
        # 以坦克中心为坐标原点，构建极坐标系
        # 下面的(x,y)表示坦克右下角,坦克大小是41*27
        x = G.player_scale_x * G.play_zoom_rate / 2
        y = -G.player_scale_y * G.play_zoom_rate / 2
        # d仅仅作为一个步长
        d = G.player_scale_x * G.play_zoom_rate / 12
        # 构建碰撞方块的宽
        for i in range(8):
            r = numpy.sqrt(x**2+y**2)
            alpha = numpy.arccos(x/r)
            if y < 0: # 顺时针为负
                alpha = -alpha
            self.all_collision_detect_pos.append((r, alpha))
            # 加个Π表示关于坐标原点对称的点
            self.all_collision_detect_pos.append((r, G.PI + alpha))
            y += d
        x = G.player_scale_x*G.play_zoom_rate/2
        y = G.player_scale_y*G.play_zoom_rate/2
        # 构建碰撞体积的长
        for i in range(11):
            r = numpy.sqrt(x**2+y**2)
            alpha = numpy.arccos(x/r)
            self.all_collision_detect_pos.append((r, alpha))
            self.all_collision_detect_pos.append((r, G.PI + alpha))
            x += -d

    def load_material(self):
        if self.id == 1:
            self.image = utils.create_image(
                utils.pics['red'], 0, 0, G.player_scale_y, G.player_scale_x, G.play_zoom_rate)
            self.fire_image = utils.create_image(
                utils.pics['red_s'], 0, 0, G.player_scale_y, G.player_scale_x, G.play_zoom_rate)
        elif self.id == 2:
            self.image = utils.create_image(
                utils.pics['green'], 0, 0, G.player_scale_y, G.player_scale_x, G.play_zoom_rate)
            self.fire_image = utils.create_image(
                utils.pics['green_s'], 0, 0, G.player_scale_y, G.player_scale_x, G.play_zoom_rate)
        elif self.id == 3:
            self.image = utils.create_image(
                utils.pics['blue'], 0, 0, G.player_scale_y, G.player_scale_x, G.play_zoom_rate)
            self.fire_image = utils.create_image(
                utils.pics['blue_s'], 0, 0, G.player_scale_y, G.player_scale_x, G.play_zoom_rate)
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

    def prevent_tank_stuck_out_wall(self):
        # 以下代码主要是防止一些意外导致坦克被卡出外墙，以下情况很少发生
        if self.x / G.real_to_virtual < G.left_space:
            # print("##############")
            # print(self.x)
            # print(G.left_space)
            # print("##############")
            self.x = (G.cell_size/2+G.left_space)*G.real_to_virtual
        if self.y/G.real_to_virtual < G.top_space:
            # print("##############")
            # print(self.y)
            # print(G.top_space)
            # print("##############")
            self.y = (G.cell_size/2+G.top_space)*G.real_to_virtual
        if self.x/G.real_to_virtual > G.left_space+G.cell_column_num*G.cell_size:
            # print("##############")
            # print(self.x)
            # print(G.left_space+G.cell_column_num*G.cell_size)
            # print("##############")
            self.x = (G.left_space+(G.cell_column_num-0.5) *
                      G.cell_size)*G.real_to_virtual
        if self.y/G.real_to_virtual > G.top_space+G.cell_row_num*G.cell_size:
            # print("##############")
            # print(self.y)
            # print(G.top_space+G.cell_row_num*G.cell_size)
            # print("##############")
            self.y = (G.top_space+(G.cell_row_num-0.5) *
                      G.cell_size)*G.real_to_virtual

    # 对按键输入作出反应，使坦克运动
    def update_position(self, keys):
        self.prevent_tank_stuck_out_wall()

        self.moving = False

        key_mapping_1 = {
            pygame.K_w: (G.tank_base_v, 0),  # (移动速度, 角度调整)
            pygame.K_s: (-G.tank_back_v, 0),
            pygame.K_a: (0, -G.tank_turn_base_w),
            pygame.K_d: (0, G.tank_turn_base_w)
        }
        key_mapping_2 = {
            pygame.K_i: (G.tank_base_v, 0),
            pygame.K_k: (-G.tank_back_v, 0),
            pygame.K_j: (0, -G.tank_turn_base_w),
            pygame.K_l: (0, G.tank_turn_base_w),
        }
        key_mapping_3 = {
            pygame.K_UP: (G.tank_base_v, 0),
            pygame.K_DOWN: (-G.tank_back_v, 0),
            pygame.K_LEFT: (0, -G.tank_turn_base_w),
            pygame.K_RIGHT: (0, G.tank_turn_base_w),
        }
        if self.id == 1:
           for key in key_mapping_1:
                if keys[key]:
                    move_speed, angle_adjustment = key_mapping_1[key]
                    self.moving = True
                    self.x += move_speed * (not self.is_stucked) * numpy.cos(self.theta)
                    self.y += move_speed * (not self.is_stucked) * numpy.sin(self.theta)
                    self.theta += (not self.is_stucked) * angle_adjustment
        elif self.id == 2:
            for key in key_mapping_2:
                if keys[key]:
                    move_speed, angle_adjustment = key_mapping_2[key]
                    self.moving = True
                    self.x += move_speed * (not self.is_stucked) * numpy.cos(self.theta)
                    self.y += move_speed * (not self.is_stucked) * numpy.sin(self.theta)
                    self.theta += (not self.is_stucked) * angle_adjustment
        elif self.id == 3:
            for key in key_mapping_3:
                if keys[key]:
                    move_speed, angle_adjustment = key_mapping_3[key]
                    self.moving = True
                    self.x += move_speed * numpy.cos(self.theta) * (not self.is_stucked)
                    self.y += move_speed * numpy.sin(self.theta) * (not self.is_stucked)
                    self.theta += angle_adjustment * (not self.is_stucked)
        # 确保 self.theta 的值在 0 到 2π 之间
        self.theta = self.theta % (2 * G.PI)

    def update_fire(self, keys):
        # 每间隔0.2s可以发射子弹一次
        if not self.can_fire and self.battlefield.clock - self.fire_cool_down_timer >= G.fire_interval:
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
            if self.bullet_num < G.bullet_exist_num or self.shotgun or self.bigbullet:
                self.fire = True # 在这里self.fire被设置为true会让坦克进入开枪状态图
                self.fire_timer = self.battlefield.clock # 不要忘了更新开火时间

        if self.fire:
            self.can_fire = False
            self.fire_cool_down_timer = self.battlefield.clock
            if self.battlefield.clock - self.fire_timer >= G.fire_state_sustain_time:
                utils.audios['fire'].play()

                if self.shotgun:
                    bullet.Shot_Gun(self.x+0.32*G.v_player_scale_x*numpy.cos(self.theta), self.y + 0.32*G.v_player_scale_y*numpy.sin(
                        self.theta), theta=self.theta, s=0.7, v=1.4, time_rate=0.08, battlefield=self.battlefield, player=self)
                    self.shotgun = False

                elif self.bigbullet:
                    self.bullets.add(bullet.Big_Bullet(x=self.x+0.32*G.v_player_scale_x*numpy.cos(self.theta), y=self.y+0.32*G.v_player_scale_y * numpy.sin(self.theta),
                                                    theta=self.theta, s=3.5, v=1.4, time_rate=1, battlefield=self.battlefield, player=self))
                    self.bigbullet = False

                elif self.laser:
                    self.bullets.add(bullet.Laser(x=self.x+0.32*G.v_player_scale_x*numpy.cos(self.theta),
                                    y=self.y+0.32*G.v_player_scale_y*numpy.sin(self.theta),
                                    theta=self.theta, s=3.5, v=2.5, time_rate=1,
                                    battlefield=self.battlefield, player=self))
                    self.laser = False

                else:
                    self.bullets.add(bullet.Bullet(x=self.x+0.32*G.v_player_scale_x*numpy.cos(self.theta),
                                    y=self.y+0.32*G.v_player_scale_y*numpy.sin(self.theta),
                                    theta=self.theta, s=1, v=1, time_rate=1,
                                    battlefield=self.battlefield, player=self))
                    self.bullet_num += 1

                self.fire = False # 在这里被设置为false，使坦克退出开枪状态

    def update_image(self):
        # 1.5PI的原因是材料图是竖直向上的，所以是1.5PI
        cur_angle = (1.5 * G.PI - self.theta) / G.PI * 180
        if self.fire:
            self.tank_state_img = pygame.transform.rotate(self.fire_image, cur_angle)
        else:
            self.tank_state_img = pygame.transform.rotate(self.image, cur_angle)

    def calculate_collision_v_s(self):
        self.collision_v_s.empty()
        for pos in self.all_collision_detect_pos:
            collision_v = pygame.sprite.Sprite()
            collision_v.image = pygame.Surface((G.player_scale_x / 12, G.player_scale_x / 12)).convert()
            collision_v.rect = collision_v.image.get_rect()
            # 不要忘记加上self.theta
            collision_v.rect.center = (pos[0] * numpy.cos(pos[1] + self.theta) + self.x / G.real_to_virtual, pos[0] * numpy.sin(pos[1] + self.theta) + self.y / G.real_to_virtual)
            self.collision_v_s.add(collision_v)

    def detect_collision(self):
        # 获取坦克现在所在位置的cell下标
        cell_index = cell.which_cells_by_tankpos(self.x / G.real_to_virtual, self.y / G.real_to_virtual)
        self.is_stucked = False
        # 处理坦克与墙之间的碰撞
        for i in cell_index:
            # 遍历这个cell的所有墙
            for wall in self.battlefield.cells[i].walls:
                # 如果碰撞到墙，则让is_stucked为True，这样坦克就无法移动
                # which_collision_v表示围绕坦克一圈的哪个小矩形碰到了
                which_collision_v = pygame.sprite.spritecollideany(wall, self.collision_v_s)
                if which_collision_v:
                    #print(which_collision_v.rect)
                    self.is_stucked = True
                    # 调节位置后坦克便可移动
                    self.adjust_position(which_collision_v)
                    return
        
        self.when_stucked = self.battlefield.clock

    def adjust_position(self, collision_v):
        x = collision_v.rect.center[0] - self.x / G.real_to_virtual
        y = collision_v.rect.center[1] - self.y / G.real_to_virtual
        alpha = numpy.arccos(x / numpy.sqrt(x**2 + y**2))
        # y < 0表示向上撞得
        if y < 0:
            alpha = -alpha

        self.x -= numpy.cos(alpha-self.theta)*min((self.battlefield.clock-self.when_stucked), 10)*0.1 * \
            G.real_to_virtual * \
            numpy.cos(self.theta) + (self.random-0.5) * \
            (self.battlefield.clock-self.when_stucked)
        self.y -= numpy.cos(alpha-self.theta)*min(0.1*(self.battlefield.clock-self.when_stucked), 10)*0.1 * \
            G.real_to_virtual * \
            numpy.sin(self.theta) + (random.random()-0.5) * \
            (self.battlefield.clock-self.when_stucked)
        self.x -= numpy.sin(alpha-self.theta) * min((self.battlefield.clock-self.when_stucked), 100)*0.1 * \
            G.real_to_virtual*-numpy.sin(self.theta)
        self.y -= numpy.sin(alpha-self.theta) * min((self.battlefield.clock-self.when_stucked), 100)*0.1 * \
            G.real_to_virtual*numpy.cos(self.theta)

    def go_die(self):
        utils.audios['explosion'].play()
        self.collision_v_s.empty()

        self.dead = True
        self.battlefield.rest_player_num -= 1
        self.battlefield.end_time = self.battlefield.clock

        self.boom = True

    def draw(self, surface):
        if self.boom:
            death_img = utils.create_image(utils.pics['dead'], 0, 0, 233, 190, 0.2)
            surface.blit(death_img, (self.x / G.real_to_virtual - 20, self.y / G.real_to_virtual - 20))
        if not self.dead:
            surface.blit(self.tank_state_img, self.tank_state_img.get_rect(center=(self.x/G.real_to_virtual, self.y/G.real_to_virtual)))
        self.bullets.draw(surface)