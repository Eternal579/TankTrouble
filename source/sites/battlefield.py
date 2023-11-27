import pygame
import random
from ..parts import player, cell, generate_maze, prop
from .. import tools, setup, constants as C


class Battlefield:
    # 加载战场
    def load(self, player_num, score):
        self.finished = False
        self.player_num = player_num
        self.score = score
        self.next = 'battlefield'
        self.random = random.random()
        self.prop_num = 0
        # 上一个道具生成的时间
        self.last_prop_gen_time = 0
        # 上一个道具的id
        self.last_prop_id = -1
        self.props = pygame.sprite.Group()
        self.ending = False
        # 游戏结束时间
        self.end_time = 0
        self.can_pause = True
        self.pause = False
        self.clock = 0
        self.winning = False
        self.winning_time = 0

        self.load_map()
        self.distribute_players_pos()

    def load_map(self):
        self.cells = []  
        self.map = pygame.Surface((C.screen_width, C.screen_height)).convert()  
        self.map.fill(C.screen_color)  

        # 地图由多个cells组成，先生成需要的cells
        generate_maze.build_cells(self)  
        # 调用 generate_maze 模块的 Generage_Maze 函数生成迷宫
        generate_maze.create_maze(self, 0, 0, C.cell_column_num-1, C.cell_row_num-1)  
        # 遍历地图中的每个单元格，调用其 draw_walls 方法在地图表面上绘制墙壁
        for i in range(0, C.cell_column_num*C.cell_row_num):
            self.cells[i].draw_walls(self.map)  

    def distribute_players_pos(self):
        self.players = pygame.sprite.Group()
        # 剩余玩家数量
        self.rest_player_num = self.player_num
        # 用于分配玩家的初始位置
        cell_is_used = {}
        for i in range(3):
            if self.score[i] != -1:
                single_player = player.player(i+1, self)
                x = random.randint(0, C.cell_column_num - 1)
                y = random.randint(0, C.cell_row_num - 1)
                # 如果随机到的位置已经被其他玩家占用
                while cell_is_used.get(generate_maze.get_idx(x, y), False):
                    x = random.randint(0, C.cell_column_num - 1)
                    y = random.randint(0, C.cell_row_num - 1)
                cell_is_used[generate_maze.get_idx(x, y)] = True
                single_player.theta = 2*C.PI*random.random()
                # 游戏中的位置是以地图为参照系的，所以要乘上C.real_to_virtual
                single_player.x = self.cells[generate_maze.get_idx(x, y)].rect.centerx * C.real_to_virtual
                single_player.y = self.cells[generate_maze.get_idx(x, y)].rect.centery * C.real_to_virtual
                self.players.add(single_player)

    def update(self, surface, keys):
        self.clock = pygame.time.get_ticks()
        self.random = random.random()
        self.draw_map(surface)

        if not self.pause and not self.winning:
            for single_player in self.players:
                single_player.update(keys)
            # 刷新一下道具
            self.update_prop()

        if not self.pause:
            # 刷新结局
            self.update_ending()

        if not self.winning:
            # 更新游戏状态
            self.update_game_state(keys)

        for single_player in self.players:
            single_player.draw(surface)

    def draw_map(self, surface):
        surface.blit(self.map, (0, 0))
        self.draw_info(surface)
        self.props.draw(surface)

    def draw_info(self, surface):
        surface.blit(tools.create_textImg('ESC  /  P', 28),
                     (C.screen_width*0.11, C.screen_height*0.9))
        if self.pause:
            surface.blit(tools.create_textImg('pause...', 28),
                         (C.screen_width*0.215, C.screen_height*0.9))
        
        self.draw_player_score(surface)

    def draw_player_score(self, surface):
        if self.score[0] != -1:
            surface.blit(tools.create_textImg('PLAYER1', 32, C.red),
                         (C.screen_width*0.33, C.screen_height*0.9))
            surface.blit(tools.create_textImg(str(self.score[0]), 32, C.red),
                         (C.screen_width*0.46, C.screen_height*0.9))
        if self.score[1] != -1:
            surface.blit(tools.create_textImg('PLAYER2', 32, C.green),
                         (C.screen_width*0.53, C.screen_height*0.9))
            surface.blit(tools.create_textImg(str(self.score[1]), 32, C.green),
                         (C.screen_width*0.66, C.screen_height*0.9))
        if self.score[2] != -1:
            surface.blit(tools.create_textImg('PLAYER3', 32, C.blue),
                         (C.screen_width*0.73, C.screen_height*0.9))
            surface.blit(tools.create_textImg(str(self.score[2]), 32, C.blue),
                         (C.screen_width*0.86, C.screen_height*0.9))

    def update_prop(self):
        # 先初始化一下last_prop_gen_time
        if self.last_prop_gen_time == 0:
            self.last_prop_gen_time = self.clock
        # 如果大于时间间隔并且场上的道具数小于2
        elif self.clock-self.last_prop_gen_time > C.prop_gener_interval and self.prop_num < 2:
            new_id = random.randint(0, C.cell_column_num * C.cell_row_num - 1)
            while new_id == self.last_prop_id:
                new_id = int(random.random()*C.cell_column_num*C.cell_row_num)
            self.last_prop_id = new_id
            self.props.add(prop.Prop(self.cells[new_id].rect.center))
            self.last_prop_gen_time = self.clock
            self.prop_num += 1
        # 检测道具是否被捡到
        for single_prop in self.props:
            for player in self.players:
                is_obtain = pygame.sprite.spritecollide(single_prop, player.collision_v_s, False)
                if is_obtain:
                    self.prop_num -= 1
                    self.last_prop_gen_time = self.clock
                    setup.SOUNDS['pick'].play()
                    single_prop.kill()
                    if single_prop.type: # 为0表示霰弹
                        player.shotgun = True
                        player.biground = False
                    else: # 为1表示大子弹
                        player.biground = True
                        player.shotgun = False
                    return

    def update_ending(self):
        if not self.ending and self.rest_player_num <= 1:
            self.ending = True
            self.end_time = self.clock
        # 过了C.judge_interval（三秒）后，若还有坦克存活则庆祝
        if self.ending and self.clock - self.end_time >= C.judge_interval:
            self.ending = False
            self.winning = True
            self.winning_time = self.clock
            for single_player in self.players:
                if not single_player.dead:
                    single_player.celebrate()
        # 过了C.celebrating_time（两秒）后，开始更新得分
        if self.winning and self.clock - self.winning_time >= C.celebrating_time:
            for single_player in self.players:
                if not single_player.dead:
                    self.score = tuple(score + (single_player.id-1 == idx) for idx, score in enumerate(self.score))
            self.finished = True

    def update_game_state(self, keys):
        if keys[pygame.K_ESCAPE]:
            self.next = 'main_menu'
            self.finished = True

        if self.can_pause and keys[pygame.K_p]:
            self.pause = not self.pause

        if keys[pygame.K_p]:
            self.can_pause = False
        else:
            self.can_pause = True


