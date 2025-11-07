import config as config
import userinput_lib.test_commandes_TUI as TUI
import userinput_lib.test_commandes_PS4 as PS4
import sensors_lib.merge_meas as merge_meas
import autoasserv_lib.asservissement as asserv
import concurrent.futures
import curses
import numpy as np

def main(stdscr):

    try:
        autorise_asservissement = False
        MyMergeMeas = merge_meas.MyMergeMeas()
        matrice_etats = np.zeros((config.NB_AXES*config.NB_ELEMENTS_MATRICE_ETAT,config.NB_ECHANTILLONS))

        MyTUI = TUI.TUI(stdscr, matrice_etats, autorise_asservissement)
        print("Prêt - Initialisation réalisée")
        my_controller = PS4.MyController(MyTUI, matrice_etats, interface="/dev/input/js0", connecting_using_ds4drv=False)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            my_controller_future = executor.submit(my_controller.listen)
            PS4_timeloop_future = executor.submit(my_controller.timeloop)
            TUI_main_loop_future = executor.submit(MyTUI.TUI_main_loop)
            update_etat_loop_future = executor.submit(asserv.update_etat_loop, autorise_asservissement, MyMergeMeas, matrice_etats)
        if MyTUI.TUI_is_exited == True:
            my_controller_future.cancel()
            PS4_timeloop_future.cancel()
            TUI_main_loop_future.cancel()
            update_etat_loop_future.cancel()
        
        results1 = my_controller_future.result()
        results2 = PS4_timeloop_future.result()
        results3 = TUI_main_loop_future.result()
        results4 = update_etat_loop_future.result()

    finally:
        config.myPCA9685.reset()
        print(results4)

curses.wrapper(main)
