from source import tools
from source.sites import main_menu, battlefield


def main():
    interface_dict = {
        'main_menu': main_menu.MainMenu(),
        'battlefield': battlefield.Battlefield()
    }
    game = tools.Game(interface_dict, 'main_menu')
    game.run()

if __name__ == '__main__':
    main()