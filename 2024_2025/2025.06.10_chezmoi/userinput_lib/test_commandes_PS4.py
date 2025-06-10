import time
from pyPS4Controller.controller import Controller
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import config
import motor_lib.cobra_pca9685 as pca9685
import userinput_lib.test_commandes_TUI as TUI
import userinput_lib.cinematique_vol as cine_vol

###################################################
#Programme de test de la manette PS4
##################################################

PS4_cmd_values = {"fy": 0, "treuil": 0}

PS4_brushless_max_speed = 40

def timeloop(stdscr):
    while True:
        fy = cine_vol.liste_forces_couples[cine_vol.FY_INDEX]
        if fy>=0:
            cine_vol.cmd_force(cine_vol.FY_INDEX, min( 1,fy+PS4_cmd_values["fy"]/40))
        else:
            cine_vol.cmd_force(cine_vol.FY_INDEX, max(-1,fy+PS4_cmd_values["fy"]/40))
        TUI.refresh_TUI(stdscr)
        time.sleep(0.02)

class MyController(Controller):

    def __init__(self, stdscr, **kwargs):
        Controller.__init__(self, **kwargs)
        self.stdscr = stdscr
        self._left_down = False
        self._right_down = False
        self._up_down = False
        self._down_down = False

    """
    def __getattr__(self, name):
        if name.startswith("on_"):
            def handler(*args, **kwargs):
                on_any_keypress(self.stdscr)
            return handler
        #else:
            #raise AttributeError(f"'{name}' attribute not found")
    """

    def on_R1_press(self):
        TUI.refresh_TUI(self.stdscr)
        
        
    def on_R1_release(self):
        TUI.refresh_TUI(self.stdscr)

    def on_L1_press(self):
        TUI.refresh_TUI(self.stdscr)
        
        
    def on_L1_release(self):
        TUI.refresh_TUI(self.stdscr)

    def on_L2_press(self, value):
        global PS4_cmd_values
        value = (value + 32767)/32767
        PS4_cmd_values["fy"] = value
        TUI.refresh_TUI(self.stdscr)
    
    def on_L2_release(self):
        global PS4_cmd_values
        PS4_cmd_values["fy"]=0
        TUI.refresh_TUI(self.stdscr)


    def on_R2_press(self,value):
        global PS4_cmd_values
        value = -(value + 32767)/32767
        PS4_cmd_values["fy"] = value
        TUI.refresh_TUI(self.stdscr)

    def on_R2_release(self):
        global PS4_cmd_values
        PS4_cmd_values["fy"]=0
        TUI.refresh_TUI(self.stdscr)


    def on_L3_x_at_rest(self):
        TUI.refresh_TUI(self.stdscr)
    
    def on_L3_left(self,value):
        cine_vol.cmd_force(cine_vol.CY_INDEX, value/32767)
        TUI.refresh_TUI(self.stdscr)

    def on_L3_right(self,value):
        cine_vol.cmd_force(cine_vol.CY_INDEX, value/32767)
        TUI.refresh_TUI(self.stdscr)

    def on_L3_up(self,value):
        value = +value/32767
        cine_vol.cmd_force(cine_vol.FZ_INDEX, value)
        TUI.refresh_TUI(self.stdscr)

    def on_L3_down(self,value):
        value = +value/32767
        cine_vol.cmd_force(cine_vol.FZ_INDEX, value)
        TUI.refresh_TUI(self.stdscr)


    def on_R3_x_at_rest(self):
        TUI.refresh_TUI(self.stdscr)

    def on_R3_left(self,value):
        cine_vol.cmd_force(cine_vol.CZ_INDEX, value/32767)
        TUI.refresh_TUI(self.stdscr)

    def on_R3_right(self,value):
        cine_vol.cmd_force(cine_vol.CZ_INDEX, value/32767)
        TUI.refresh_TUI(self.stdscr)

    def on_R3_up(self,value):
        cine_vol.cmd_force(cine_vol.FX_INDEX, value/32767)
        TUI.refresh_TUI(self.stdscr)

    def on_R3_down(self,value):
        cine_vol.cmd_force(cine_vol.FX_INDEX, value/32767)
        TUI.refresh_TUI(self.stdscr)


    def on_up_arrow_press(self):
        PS4_cmd_values["treuil"] = max(-100,PS4_cmd_values["treuil"] - 100)
        config.mcc_2pwm["treuil"].cmd_vit_pourcent(PS4_cmd_values["treuil"])

    def on_up_arrow_release(self):
        PS4_cmd_values["treuil"] = 0

    def on_down_arrow_press(self):
        PS4_cmd_values["treuil"] = min(100,PS4_cmd_values["treuil"] + 100)
        config.mcc_2pwm["treuil"].cmd_vit_pourcent(PS4_cmd_values["treuil"])

    def on_down_arrow_release(self):
        PS4_cmd_values["treuil"] = 0

    """
    def on_hat(self, hat, value):
        x, y = value

        # LEFT
        if x == -1 and not self._left_down:
            self._left_down = True
            self.on_left_arrow_press()
        elif x != -1 and self._left_down:
            self._left_down = False
            self.on_left_arrow_release()

        # RIGHT
        if x == 1 and not self._right_down:
            self._right_down = True
            self.on_right_arrow_press()
        elif x != 1 and self._right_down:
            self._right_down = False
            self.on_right_arrow_release()

        # UP
        if y == 1 and not self._up_down:
            self._up_down = True
            self.on_up_arrow_press()
        elif y != 1 and self._up_down:
            self._up_down = False
            self.on_up_arrow_release()

        # DOWN
        if y == -1 and not self._down_down:
            self._down_down = True
            self.on_down_arrow_press()
        elif y != -1 and self._down_down:
            self._down_down = False
            self.on_down_arrow_release()
    """

    def on_x_press(self):
        config.myPCA9685.reset()
        TUI.refresh_TUI(self.stdscr)
        TUI.TUI_is_exited = True
        
    def on_circle_press(self):
        TUI.refresh_TUI(self.stdscr)

    



