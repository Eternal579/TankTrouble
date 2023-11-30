import utils
import main_menu, battlefield
import utils
import sys
import pygame

class Game:
    def __init__(self, interface_dict, start_interface):
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.keys = pygame.key.get_pressed()
        self.interface_dict = interface_dict
        self.state = self.interface_dict[start_interface]

    def update(self):
        if self.state.finished:
            player_num = self.state.player_num
            # 这个score是个数组，指的是玩家的得分
            score = self.state.score
            next_state = self.state.next
            self.state = self.interface_dict[next_state]
            self.state.load(player_num, score)

        self.state.update(self.screen, self.keys)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN: # 按下
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP: # 松开
                    self.keys = pygame.key.get_pressed()
                elif self.state == self.interface_dict['main_menu']:
                    for button in self.state.buttons:
                        button.handle_event(event)

            self.update()
            pygame.display.update() # 将之前绘制的图形更新到屏幕上


def main():
    interface_dict = {'main_menu': main_menu.MainMenu(),
                      'battlefield': battlefield.Battlefield()}
    game = Game(interface_dict, 'main_menu')
    game.run()

if __name__ == '__main__':
    main()