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
        self.setup_color(x, y)
        self.setup_walls()

    def setup_walls(self):
        self.walls = pygame.sprite.Group()

        # 如果单元格的 walls_mark 属性包含 C.TOP 标志
        # 创建一个 Wall 对象并将其添加到 walls 组中，位于单元格的顶部
        if self.walls_mark & C.TOP:
            self.walls.add(Wall(self.rect.x, self.rect.y, C.TOP))

        # 如果单元格的 walls_mark 属性包含 C.BOTTOM 标志
        # 创建一个 Wall 对象并将其添加到 walls 组中，位于单元格的底部
        if self.walls_mark & C.BOTTOM:
            self.walls.add(Wall(self.rect.x, self.rect.y + C.cell_size, C.BOTTOM))

        # 如果单元格的 walls_mark 属性包含 C.LEFT 标志
        # 创建一个 Wall 对象并将其添加到 walls 组中，位于单元格的左侧
        if self.walls_mark & C.LEFT:
            self.walls.add(Wall(self.rect.x, self.rect.y, C.LEFT))

        # 如果单元格的 walls_mark 属性包含 C.RIGHT 标志
        # 创建一个 Wall 对象并将其添加到 walls 组中，位于单元格的右侧
        if self.walls_mark & C.RIGHT:
            self.walls.add(Wall(self.rect.x + C.cell_size, self.rect.y, C.RIGHT))

    def setup_color(self, x, y):
        # 创建一个 Surface 对象作为单元格的图像，尺寸为 C.cell_size × C.cell_size
        self.image = pygame.Surface((C.cell_size, C.cell_size)).convert()
        # 使用白色填充单元格的图像
        self.image.fill(C.white)
        # 获取单元格图像的矩形边界
        self.rect = self.image.get_rect()
        # 将单元格的矩形边界移动到指定的 x 和 y 坐标位置
        self.rect.move_ip(x, y)

    def draw_cell(self, surface):
        surface.blit(self.image, self.rect)

    def draw_walls(self, surface):
        self.walls.update(surface)


def calculate_cell_num(x, y):
    cell_x = (x-C.left_space)/C.cell_size
    cell_y = (y-C.top_space)/C.cell_size
    int_cell_x = int(cell_x)
    int_cell_y = int(cell_y)

    cell1 = int_cell_x+int_cell_y*C.cell_column_num

    if cell_x-int_cell_x >= 0.5:
        cell2 = int_cell_x+1+int_cell_y*C.cell_column_num
        if cell_y-int_cell_y >= 0.5:
            cell3 = int_cell_x+(int_cell_y+1)*C.cell_column_num
            cell4 = int_cell_x+1+(int_cell_y+1)*C.cell_column_num
        else:
            cell3 = int_cell_x+(int_cell_y-1)*C.cell_column_num
            cell4 = int_cell_x+1+(int_cell_y-1)*C.cell_column_num

    else:
        cell2 = (int_cell_x-1)+int_cell_y*C.cell_column_num
        if cell_y-int_cell_y >= 0.5:
            cell3 = int_cell_x+(int_cell_y+1)*C.cell_column_num
            cell4 = (int_cell_x-1)+(int_cell_y+1)*C.cell_column_num
        else:
            cell3 = int_cell_x+(int_cell_y-1)*C.cell_column_num
            cell4 = (int_cell_x-1)+(int_cell_y-1)*C.cell_column_num

    return (min(max(cell1, 0), C.cell_column_num*C.cell_row_num-1), min(max(cell2, 0), C.cell_column_num*C.cell_row_num-1),
            min(max(cell3, 0), C.cell_column_num*C.cell_row_num-1), min(max(cell4, 0), C.cell_column_num*C.cell_row_num-1))