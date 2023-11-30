import pygame
import globals as G


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        if type == G.TOP or type == G.BOTTOM:
            self.rect = pygame.Rect(x - G.wall_size / 2, y - G.wall_size / 2, G.cell_size + G.wall_size, G.wall_size)
        elif type == G.LEFT or type == G.RIGHT:
            self.rect = pygame.Rect(x - G.wall_size / 2, y - G.wall_size / 2, G.wall_size, G.cell_size + G.wall_size)

    def update(self, surface):
        pygame.draw.rect(surface, G.black, self.rect)


class Cell:
    # x和y表示此cell的位置，walls_mark表示这个cell的上下左右有没有墙
    def __init__(self, x, y, walls_mark):
        self.walls_mark = walls_mark
        self.image = pygame.Surface((G.cell_size, G.cell_size)).convert()
        self.image.fill(G.white)
        self.rect = self.image.get_rect()
        self.rect.move_ip(x, y)
        
        self.record_wall_pos()

    def record_wall_pos(self):
        self.walls = pygame.sprite.Group()
        if self.walls_mark & G.TOP:
            self.walls.add(Wall(self.rect.x, self.rect.y, G.TOP))
        # 墙位于一个cell的底部，需要在纵坐标上加一个C.cell_size
        if self.walls_mark & G.BOTTOM:
            self.walls.add(Wall(self.rect.x, self.rect.y + G.cell_size, G.BOTTOM))
        if self.walls_mark & G.LEFT:
            self.walls.add(Wall(self.rect.x, self.rect.y, G.LEFT))
        # 墙位于一个cell的右侧，需要在横坐标上加一个C.cell_size
        if self.walls_mark & G.RIGHT:
            self.walls.add(Wall(self.rect.x + G.cell_size, self.rect.y, G.RIGHT))

    def draw_cell(self, surface):
        surface.blit(self.image, self.rect)

    def draw_walls(self, surface):
        self.walls.update(surface)


def which_cells_by_tankpos(x, y):
    # 当前这个坦克位于的cell是第几行第几列
    float_cell_x = (x - G.left_space) / G.cell_size
    float_cell_y = (y - G.top_space) / G.cell_size
    int_cell_x = int(float_cell_x)
    int_cell_y = int(float_cell_y)

    # 这个坦克所在的cell
    possible_cell1 = int_cell_x + int_cell_y * G.cell_column_num

    # 由于一个坦克最多可以占四个cell，所以要考虑种种情况
    # 如果坦克中心位置在一个cell的偏右侧
    if float_cell_x - int_cell_x >= 0.5:
        possible_cell2 = int_cell_x + 1 + int_cell_y * G.cell_column_num
        # 如果坦克中心位置在一个cell的偏下侧
        if float_cell_y - int_cell_y >= 0.5:
            possible_cell3 = int_cell_x + (int_cell_y + 1) * G.cell_column_num
            possible_cell4 = int_cell_x + 1 + (int_cell_y + 1) * G.cell_column_num
        else:
            possible_cell3 = int_cell_x + (int_cell_y - 1) * G.cell_column_num
            possible_cell4 = int_cell_x + 1 + (int_cell_y - 1) * G.cell_column_num
    
    # 如果坦克中心位置在一个cell的偏左侧
    else:
        possible_cell2 = (int_cell_x-1) + int_cell_y * G.cell_column_num
        # 如果坦克中心位置在一个cell的偏下侧
        if float_cell_y - int_cell_y >= 0.5:
            possible_cell3 = int_cell_x + (int_cell_y + 1) * G.cell_column_num
            possible_cell4 = (int_cell_x - 1) + (int_cell_y + 1) * G.cell_column_num
        else:
            possible_cell3 = int_cell_x + (int_cell_y - 1) * G.cell_column_num
            possible_cell4 = (int_cell_x - 1) + (int_cell_y - 1) * G.cell_column_num
    # possible_cell可能会小于0，同时在屏幕下方是，possible_cell容易超出C.cell_column_num*G.cell_row_num-1，所以需要取max
    return (min(max(possible_cell1, 0), G.cell_column_num * G.cell_row_num - 1), min(max(possible_cell2, 0), G.cell_column_num * G.cell_row_num - 1),
            min(max(possible_cell3, 0), G.cell_column_num * G.cell_row_num - 1), min(max(possible_cell4, 0), G.cell_column_num * G.cell_row_num - 1))