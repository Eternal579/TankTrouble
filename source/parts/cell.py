import pygame
import random
from .. import constants as C


class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        pygame.sprite.Sprite.__init__(self)
        self.type = type
        if type == C.TOP or type == C.BOTTOM:
            self.rect = pygame.Rect(
                x-C.WALL_SIZE/2, y-C.WALL_SIZE/2, C.BLOCK_SIZE+C.WALL_SIZE, C.WALL_SIZE)
        elif type == C.LEFT or type == C.RIGHT:
            self.rect = pygame.Rect(
                x-C.WALL_SIZE/2, y-C.WALL_SIZE/2, C.WALL_SIZE, C.BLOCK_SIZE+C.WALL_SIZE)

    def update(self, surface):
        pygame.draw.rect(surface, C.WALL_COLOR, self.rect)


class Cell:
    # x和y表示此cell的位置，walls_sign表示这个cell在上下左右的边界否
    def __init__(self, x, y, walls_sign):
        self.walls_sign = walls_sign
        self.setup_color(x, y)
        self.setup_walls()

    def setup_walls(self):
        self.walls = pygame.sprite.Group()

        # 如果单元格的 walls_sign 属性包含 C.TOP 标志
        # 创建一个 Wall 对象并将其添加到 walls 组中，位于单元格的顶部
        if self.walls_sign & C.TOP:
            self.walls.add(Wall(self.rect.x, self.rect.y, C.TOP))

        # 如果单元格的 walls_sign 属性包含 C.BOTTOM 标志
        # 创建一个 Wall 对象并将其添加到 walls 组中，位于单元格的底部
        if self.walls_sign & C.BOTTOM:
            self.walls.add(Wall(self.rect.x, self.rect.y + C.BLOCK_SIZE, C.BOTTOM))

        # 如果单元格的 walls_sign 属性包含 C.LEFT 标志
        # 创建一个 Wall 对象并将其添加到 walls 组中，位于单元格的左侧
        if self.walls_sign & C.LEFT:
            self.walls.add(Wall(self.rect.x, self.rect.y, C.LEFT))

        # 如果单元格的 walls_sign 属性包含 C.RIGHT 标志
        # 创建一个 Wall 对象并将其添加到 walls 组中，位于单元格的右侧
        if self.walls_sign & C.RIGHT:
            self.walls.add(Wall(self.rect.x + C.BLOCK_SIZE, self.rect.y, C.RIGHT))

    def setup_color(self, x, y):
        # 创建一个 Surface 对象作为单元格的图像，尺寸为 C.BLOCK_SIZE × C.BLOCK_SIZE
        self.image = pygame.Surface((C.BLOCK_SIZE, C.BLOCK_SIZE)).convert()
        # 使用白色填充单元格的图像
        self.image.fill(C.CELL_COLOR)
        # 获取单元格图像的矩形边界
        self.rect = self.image.get_rect()
        # 将单元格的矩形边界移动到指定的 x 和 y 坐标位置
        self.rect.move_ip(x, y)

    def draw_cell(self, surface):
        surface.blit(self.image, self.rect)

    def draw_walls(self, surface):
        self.walls.update(surface)


def calculate_cell_num(x, y):
    cell_x = (x-C.LEFT_SPACE)/C.BLOCK_SIZE
    cell_y = (y-C.TOP_SPACE)/C.BLOCK_SIZE
    int_cell_x = int(cell_x)
    int_cell_y = int(cell_y)

    cell1 = int_cell_x+int_cell_y*C.COLUMN_NUM

    if cell_x-int_cell_x >= 0.5:
        cell2 = int_cell_x+1+int_cell_y*C.COLUMN_NUM
        if cell_y-int_cell_y >= 0.5:
            cell3 = int_cell_x+(int_cell_y+1)*C.COLUMN_NUM
            cell4 = int_cell_x+1+(int_cell_y+1)*C.COLUMN_NUM
        else:
            cell3 = int_cell_x+(int_cell_y-1)*C.COLUMN_NUM
            cell4 = int_cell_x+1+(int_cell_y-1)*C.COLUMN_NUM

    else:
        cell2 = (int_cell_x-1)+int_cell_y*C.COLUMN_NUM
        if cell_y-int_cell_y >= 0.5:
            cell3 = int_cell_x+(int_cell_y+1)*C.COLUMN_NUM
            cell4 = (int_cell_x-1)+(int_cell_y+1)*C.COLUMN_NUM
        else:
            cell3 = int_cell_x+(int_cell_y-1)*C.COLUMN_NUM
            cell4 = (int_cell_x-1)+(int_cell_y-1)*C.COLUMN_NUM

    return (min(max(cell1, 0), C.COLUMN_NUM*C.ROW_NUM-1), min(max(cell2, 0), C.COLUMN_NUM*C.ROW_NUM-1),
            min(max(cell3, 0), C.COLUMN_NUM*C.ROW_NUM-1), min(max(cell4, 0), C.COLUMN_NUM*C.ROW_NUM-1))