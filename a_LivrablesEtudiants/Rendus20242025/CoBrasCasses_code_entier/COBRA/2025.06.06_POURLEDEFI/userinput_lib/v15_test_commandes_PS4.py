from pyPS4Controller.controller import Controller
import motor_lib.v15_cobra_pca9685 as pca9685
import v15_cobra_config as config
import userinput_lib.v15_test_commandes_TUI as TUI
import time

###################################################
#Programme de test de la manette PS4
##################################################

PS4_cmd_values = {"axe": 0, "cerceau": 0, "treuil": 0, "pince": 0}
PS4_brushless_max_speed =  55

def timeloop(stdscr):
    while True:
        config.servo["axe"].cmd_angle_deg(config.servo["axe"].angle_deg+PS4_cmd_values["axe"]/2)
        config.servo["cerceau"].cmd_angle_deg(config.servo["cerceau"].angle_deg+PS4_cmd_values["cerceau"]/2)
        #config.servo["axe"].cmd_angle_deg(config.servo["axe"].angle_deg+0.01)
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
        PS4_cmd_values["cerceau"] = -1
        TUI.refresh_TUI(self.stdscr)
        
        
    def on_R1_release(self):
        PS4_cmd_values["cerceau"] = 0
        TUI.refresh_TUI(self.stdscr)

    def on_L1_press(self):
        PS4_cmd_values["cerceau"] = 1
        TUI.refresh_TUI(self.stdscr)
        
        
    def on_L1_release(self):
        PS4_cmd_values["cerceau"] = 0
        TUI.refresh_TUI(self.stdscr)

    def on_L2_press(self, value):
        global PS4_cmd_values
        value = (value + 32767)/32767
        PS4_cmd_values["axe"] = value
        #value = value*50/32767
        #PS4_cmd_values["treuil"] = value
        #config.mcc_2pwm["treuil"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)
    
    def on_L2_release(self):
        global PS4_cmd_values
        PS4_cmd_values["axe"]=0
        TUI.refresh_TUI(self.stdscr)


    def on_R2_press(self,value):
        global PS4_cmd_values
        value = -(value + 32767)/32767
        PS4_cmd_values["axe"] = value
        TUI.refresh_TUI(self.stdscr)

    def on_R2_release(self):
        global PS4_cmd_values
        PS4_cmd_values["axe"]=0
        TUI.refresh_TUI(self.stdscr)


    def on_L3_x_at_rest(self):
        TUI.refresh_TUI(self.stdscr)
    
    def on_L3_left(self,value):
        TUI.refresh_TUI(self.stdscr)

    def on_L3_right(self,value):
        TUI.refresh_TUI(self.stdscr)

    def on_L3_up(self,value):
        value = +value*PS4_brushless_max_speed/32767
        PS4_cmd_values["gauche"] = value
        config.brushless["gauche"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)

    def on_L3_down(self,value):
        value = +value*PS4_brushless_max_speed/32767
        PS4_cmd_values["gauche"] = value
        config.brushless["gauche"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)


    def on_R3_x_at_rest(self):
        TUI.refresh_TUI(self.stdscr)

    def on_R3_left(self,value):
        TUI.refresh_TUI(self.stdscr)

    def on_R3_right(self,value):
        TUI.refresh_TUI(self.stdscr)

    def on_R3_up(self,value):
        value = -value*PS4_brushless_max_speed/32767
        PS4_cmd_values["droite"] = value
        config.brushless["droite"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)

    def on_R3_down(self,value):
        value = -value*PS4_brushless_max_speed/32767
        PS4_cmd_values["droite"] = value
        config.brushless["droite"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)


    def on_up_arrow_press(self):
        PS4_cmd_values["treuil"] = min(100,PS4_cmd_values["treuil"] + 100)
        config.mcc_2pwm["treuil"].cmd_vit_pourcent(PS4_cmd_values["treuil"])

    def on_up_arrow_release(self):
        PS4_cmd_values["treuil"] = 0

    def on_down_arrow_press(self):
        PS4_cmd_values["treuil"] = max(-100,PS4_cmd_values["treuil"] - 100)
        config.mcc_2pwm["treuil"].cmd_vit_pourcent(PS4_cmd_values["treuil"])

    def on_down_arrow_release(self):
        PS4_cmd_values["treuil"] = 0


    def on_left_arrow_press(self):
        PS4_cmd_values["pince"] = min(100,PS4_cmd_values["pince"] + 100)
        config.mcc_2pwm["pince"].cmd_vit_pourcent(PS4_cmd_values["pince"])

    def on_left_arrow_release(self):
        PS4_cmd_values["pince"] = 0

    def on_right_arrow_press(self):
        PS4_cmd_values["pince"] = max(-100,PS4_cmd_values["pince"] - 100)
        config.mcc_2pwm["pince"].cmd_vit_pourcent(PS4_cmd_values["pince"])

    def on_right_arrow_release(self):
        PS4_cmd_values["pince"] = 0
    

    def on_x_press(self):
        config.myPCA9685.reset()
        TUI.refresh_TUI(self.stdscr)
        TUI.TUI_is_exited = True
        
    def on_circle_press(self):
        TUI.refresh_TUI(self.stdscr)

    



