import v12_cobra_config as config
import v12_test_commandes_TUI as TUI
import v12_test_commandes_PS4 as PS4
from multiprocessing import Process
import curses


def main(stdscr):
    TUI.TUI_init(stdscr)
    print("Prêt - Initialisation réalisée")
    my_controller = PS4.MyController(stdscr, interface="/dev/input/js0", connecting_using_ds4drv=False)
    #my_controller.listen_in_thread()
    Process(target=my_controller.listen).start()
    Process(target=TUI.TUI_main_loop, args=(stdscr,)).start()
    config.myPCA9685.reset()



curses.wrapper(main)
