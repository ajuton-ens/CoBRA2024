import v14_cobra_config as config
import userinput_lib.v14_test_commandes_TUI as TUI
import userinput_lib.v14_test_commandes_PS4 as PS4
import concurrent.futures
#from multiprocessing import Process
import curses

def main(stdscr):
    TUI.TUI_init(stdscr)
    print("Prêt - Initialisation réalisée")
    my_controller = PS4.MyController(stdscr, interface="/dev/input/js0", connecting_using_ds4drv=False)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        timeloop_future = executor.submit(PS4.timeloop,stdscr)
        my_controller_future = executor.submit(my_controller.listen)
        TUI_main_loop_future = executor.submit(TUI.TUI_main_loop,stdscr)
    if TUI.TUI_is_exited == True:
        timeloop_future.cancel()
        my_controller_future.cancel()
        TUI_main_loop_future.cancel()
    
    results1 = timeloop_future.result()
    results2 = my_controller_future.result()
    results3 = TUI_main_loop_future.result()

    config.myPCA9685.reset()

curses.wrapper(main)
