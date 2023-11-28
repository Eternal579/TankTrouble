import pygame
import random
from .. import constants as C


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        if type == C.TOP or type == C.BOTTOM:
            self.rect = pygame.Rect(
                x-C.wall_size/2, y-C.wall_size/2, C.cell_size+C.wall_size, C.wall_size)
        elif type == C.LEFT or type == C.RIGHT:
            self.rect = pygame.Rect(
                x-C.wall_size/2, y-C.wall_size/2, C.wall_size, C.cell_size+C.wall_size)

    def update(self, surface):
        pygame.draw.rect(surface, C.black, self.rect)


class Cell:
    # x和y表示此cell的位置，walls_mark表示这个cell的上下左右有没有墙
    def __init__(self, x, y, walls_mark):
        self.walls_mark = walls_mark
        self.image = pygame.Surface((C.cell_size, C.cell_size)).convert()
        self.image.fill(C.white)
        self.rect = self.image.get_rect()
        self.rect.move_ip(x, y)
        
        self.record_wall_pos()

    def record_wall_pos(self):
        self.walls = pygame.sprite.Group()
        if self.walls_mark & C.TOP:
            self.walls.add(Wall(self.rect.x, self.rect.y, C.TOP))
        # 墙位于一个cell的底部，需要在纵坐标上加一个C.cell_size
        if self.walls_mark & C.BOTTOM:
            self.walls.add(Wall(self.rect.x, self.rect.y + C.cell_size, C.BOTTOM))
        if self.walls_mark & C.LEFT:
            self.walls.add(Wall(self.rect.x, self.rect.y, C.LEFT))
        # 墙位于一个cell的右侧，需要在横坐标上加一个C.cell_size
        if self.walls_mark & C.RIGHT:
            self.walls.add(Wall(self.rect.x + C.cell_size, self.rect.y, C.RIGHT))

    def draw_cell(self, surface):
        surface.blit(self.image, self.rect)

    def draw_walls(self, surface):
        self.walls.update(surface)


def which_cells_by_tankpos(x, y):
    # 当前这个坦克位于的cell是第几行第几列
    float_cell_x = (x - C.left_space) / C.cell_size
    float_cell_y = (y - C.top_space) / C.cell_size
    int_cell_x = int(float_cell_x)
    int_cell_y = int(float_cell_y)

    # 这个坦克所在的cell
    possible_cell1 = int_cell_x + int_cell_y * C.cell_column_num

    # 由于一个坦克最多可以占四个cell，所以要考虑种种情况
    # 如果坦克中心位置在一个cell的偏右侧
    if float_cell_x - int_cell_x >= 0.5:
        possible_cell2 = int_cell_x + 1 + int_cell_y * C.cell_column_num
        # 如果坦克中心位置在一个cell的偏下侧
        if float_cell_y - int_cell_y >= 0.5:
            possible_cell3 = int_cell_x + (int_cell_y + 1) * C.cell_column_num
            possible_cell4 = int_cell_x + 1 + (int_cell_y + 1) * C.cell_column_num
        else:
            possible_cell3 = int_cell_x + (int_cell_y - 1) * C.cell_column_num
            possible_cell4 = int_cell_x + 1 + (int_cell_y - 1) * C.cell_column_num
    
    # 如果坦克中心位置在一个cell的偏左侧
    else:
        possible_cell2 = (int_cell_x-1) + int_cell_y * C.cell_column_num
        # 如果坦克中心位置在一个cell的偏下侧
        if float_cell_y - int_cell_y >= 0.5:
            possible_cell3 = int_cell_x + (int_cell_y + 1) * C.cell_column_num
            possible_cell4 = (int_cell_x - 1) + (int_cell_y + 1) * C.cell_column_num
        else:
            possible_cell3 = int_cell_x + (int_cell_y - 1) * C.cell_column_num
            possible_cell4 = (int_cell_x - 1) + (int_cell_y - 1) * C.cell_column_num
    # possible_cell可能会小于0，同时在屏幕下方是，possible_cell容易超出C.cell_column_num*C.cell_row_num-1，所以需要取max
    return (min(max(possible_cell1, 0), C.cell_column_num * C.cell_row_num - 1), min(max(possible_cell2, 0), C.cell_column_num * C.cell_row_num - 1),
            min(max(possible_cell3, 0), C.cell_column_num * C.cell_row_num - 1), min(max(possible_cell4, 0), C.cell_column_num * C.cell_row_num - 1))