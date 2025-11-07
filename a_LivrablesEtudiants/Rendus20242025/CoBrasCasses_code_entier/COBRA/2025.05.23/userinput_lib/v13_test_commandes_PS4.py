from pyPS4Controller.controller import Controller
import motor_lib.v13_cobra_pca9685 as pca9685
import v13_cobra_config as config
import userinput_lib.v13_test_commandes_TUI as TUI
import time

###################################################
#Programme de test de la manette PS4
##################################################

PS4_cmd_values = {"axe": 0}
PS4_brushless_max_speed = 50

def timeloop(stdscr):
    while True:
        config.servo["axe"].cmd_angle_deg(config.servo["axe"].angle_deg+PS4_cmd_values["axe"]/2)
        #config.servo["axe"].cmd_angle_deg(config.servo["axe"].angle_deg+0.01)
        TUI.refresh_TUI(stdscr)
        time.sleep(0.02)

class MyController(Controller):

    def __init__(self, stdscr, **kwargs):
        Controller.__init__(self, **kwargs)
        self.stdscr = stdscr

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


    def on_L2_press(self, value):
        global PS4_cmd_values
        value = -(value + 32767)/32767
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
        value = (value + 32767)/32767
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

        
    def on_x_press(self):
        config.myPCA9685.reset()
        TUI.refresh_TUI(self.stdscr)
        TUI.TUI_is_exited = True
        
    def on_circle_press(self):
        TUI.refresh_TUI(self.stdscr)




