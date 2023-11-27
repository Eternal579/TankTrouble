import numpy

# 游戏界面大小
screen_width, screen_height = 1280, 720
# 游戏界面颜色
screen_color = (230, 230, 230)

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
blue = (0, 0, 255)
purple = (255, 0, 255)
yellow = (255, 255, 0)
green = (0, 255, 0)
gray = (130, 130, 130)
dark_gray = (100, 100, 100)

# 在主界面展示tank的缩放比例
tank_zoom_rate = 1.5
# 在游玩的时候展示tank的缩放比例
play_zoom_rate = 1.0
# 坦克图片大小
player_scale_x = 41
player_scale_y = 27
# 一列有多少个cell
cell_column_num = 12
# 一行有多少个cell
cell_row_num = 6
# 一共有多少个cell
cell_num = 72
# 一个cell的大小
cell_size = 94
# 标识cell处于上下左右
TOP, BOTTOM, LEFT, RIGHT = 1, 2, 4, 8
# 子弹图片大小
bullet_pic_size_x = 9
bullet_pic_size_y = 9
# 由于每一次按下按键，并不只是执行一次，所以需要除以一个数字，在这里把一个像素看成100个单位
real_to_virtual = 100
v_player_scale_x = real_to_virtual*player_scale_x
v_player_scale_y = real_to_virtual*player_scale_y
# 用来判断是否与墙体碰撞
is_collided = 6
# 墙的宽度
wall_size = 8
# 上方空白高度
top_space = 42
# 左边空白宽度
left_space = 74
PI = numpy.arccos(-1)
# 字体
font = 'Fixedsys.ttf'
# 子弹的基础速度
bullet_base_v = 105
# 前进的基础速度
tank_base_v = 60
# 坦克旋转的角速度
tank_turn_base_w = 0.05/PI
# 坦克倒退的速度
tank_back_v = 0.83*tank_base_v
# 碎片向下的垂直速度
g_val = 4
# 判断是否有玩家获胜的间隔时间，单位毫秒
judge_interval = 3000
# 庆祝时间
celebrating_time = 2000
# 道具生成的间隔时间
prop_gener_interval = 10000
# 子弹存在的最大时间
bullet_max_exist_time = 8000
# 每个坦克子弹最大存在个数
bullet_exist_num = 5
fire_state_sustain_time = 110
# 开火间隔时间
fire_interval = 200