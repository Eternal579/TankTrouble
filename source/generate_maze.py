import random
import globals as G
import cell

# 根据x,y获得在cells数组中的下表
def get_idx(x, y):
    return x + y * G.cell_column_num

# 地图由多个cells组成，先生成需要的cells
def build_cells(battlefield):
    # 先把所有的cell的右和下弄个墙
    for i in range(0, G.cell_column_num * G.cell_row_num):
        cell_x = G.left_space + i % G.cell_column_num * G.cell_size
        cell_y = G.top_space + int(i / G.cell_column_num) * G.cell_size
        battlefield.cells.append(cell.Cell(cell_x, cell_y, G.BOTTOM | G.RIGHT))
        battlefield.cells[i].draw_cell(battlefield.map)
    # 然后最上面一行的cell给他加一个上方的墙
    for x in range(0, G.cell_column_num):
        i = get_idx(x, 0)
        cell_x = G.left_space + i % G.cell_column_num * G.cell_size
        cell_y = G.top_space + int(i / G.cell_column_num) * G.cell_size
        battlefield.cells[i] = cell.Cell(cell_x, cell_y, G.TOP | G.BOTTOM | G.RIGHT)
        battlefield.cells[i].draw_cell(battlefield.map)
    # 给最左边的一列的cell加上一个左边的墙
    for y in range(0, G.cell_row_num):
        i = get_idx(0, y)
        cell_x = G.left_space + i % G.cell_column_num * G.cell_size
        cell_y = G.top_space + int(i / G.cell_column_num) * G.cell_size
        battlefield.cells[i] = cell.Cell(cell_x, cell_y, G.BOTTOM | G.LEFT | G.RIGHT)
        battlefield.cells[i].draw_cell(battlefield.map)
    # 第一个cell的上下左右都要有墙
    battlefield.cells[0] = cell.Cell(G.left_space, G.top_space, G.TOP | G.BOTTOM | G.LEFT | G.RIGHT)
    battlefield.cells[0].draw_cell(battlefield.map)

# 使用块状分割算法处理cells来生成地图
def create_maze(battlefield, x1, y1, x2, y2):
    # 经实验发现每次递归到最后会让一列或一行无法通过，于是加上以下代码
    if x2-x1 == 0:
        for u in range(y1, y2):
            for wall in battlefield.cells[get_idx(x1, u)].walls:
                if wall.type == G.BOTTOM:
                    wall.kill()
        for u in range(y2, y1, -1):
            for wall in battlefield.cells[get_idx(x1, u)].walls:
                if wall.type == G.TOP:
                    wall.kill()
        return
    if y2-y1 == 0:
        for v in range(x1, x2):
            for wall in battlefield.cells[get_idx(v, y1)].walls:
                if wall.type == G.RIGHT:
                    wall.kill()
        for v in range(x2, x1, -1):
            for wall in battlefield.cells[get_idx(v, y1)].walls:
                if wall.type == G.LEFT:
                    wall.kill()
        return

    # 随机要处理的行与列
    u = random.randint(x1, x2-1)
    v = random.randint(y1, y2-1)
    # 随机抹掉墙
    erase_wall(u, v, battlefield, x1, y1, x2, y2)
    
    # 四分迷宫迭代
    create_maze(battlefield, x1, y1, u, v)
    create_maze(battlefield, u+1, y1, x2, v)
    create_maze(battlefield, x1, v+1, u, y2)
    create_maze(battlefield, u+1, v+1, x2, y2)

def erase_wall(u, v, battlefield, x1, y1, x2, y2):
    choose = [1, 1, 1, 1]
    choose[random.randint(0, 3)] = 0
    randfix = random.uniform(0.8, 1)

    if choose[0] or random.random() < randfix:
        p = random.randint(x1, u)
        for wall in battlefield.cells[get_idx(p, v)].walls:
            if wall.type == G.BOTTOM:
                wall.kill()
    if choose[1] or random.random() < randfix:
        p = random.randint(y1, v)
        for wall in battlefield.cells[get_idx(u, p)].walls:
            if wall.type == G.RIGHT:
                wall.kill()
    if choose[2] or random.random() < randfix:
        p = random.randint(u+1, x2)
        for wall in battlefield.cells[get_idx(p, v)].walls:
            if wall.type == G.BOTTOM:
                wall.kill()
    if choose[3] or random.random() < randfix:
        p = random.randint(v+1, y2)
        for wall in battlefield.cells[get_idx(u, p)].walls:
            if wall.type == G.RIGHT:
                wall.kill()