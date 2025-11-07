from pyPS4Controller.controller import Controller
import v12_cobra_pca9685 as pca9685
import v12_cobra_config as config
import v12_test_commandes_TUI as TUI

###################################################
#Programme de test de la manette PS4
##################################################


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
        value = value*50/32767
        config.mcc_2pwm["treuil"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)
        
    def on_L2_release(self):
        TUI.refresh_TUI(self.stdscr)


    def on_R2_press(self,value):
        if (value>0) :
            value = value*config.servo["axe"].angle_max/32767
        else:
            value = -value*config.servo["axe"].angle_min/32767
        #print("La valeur de R2 est: ",value) # pour tester les touches (on voit le print quand on appuie sur la touche (appelle la fonction))
        config.servo["axe"].cmd_angle_deg(value)
        TUI.refresh_TUI(self.stdscr)

    def on_R2_release(self):
        TUI.refresh_TUI(self.stdscr)


    def on_L3_x_at_rest(self):
        TUI.refresh_TUI(self.stdscr)
    
    def on_L3_left(self,value):
        value = +value*50/32767
        TUI.refresh_TUI(self.stdscr)

    def on_L3_right(self,value):
        value = +value*50/32767
        TUI.refresh_TUI(self.stdscr)

    def on_L3_up(self,value):
        value = +value*50/32767
        config.brushless["gauche"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)

    def on_L3_down(self,value):
        value = +value*50/32767
        config.brushless["gauche"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)


    def on_R3_x_at_rest(self):
        TUI.refresh_TUI(self.stdscr)

    def on_R3_left(self,value):
        value = -value*50/32767
        TUI.refresh_TUI(self.stdscr)

    def on_R3_right(self,value):
        value = -value*50/32767
        TUI.refresh_TUI(self.stdscr)

    def on_R3_up(self,value):
        value = -value*50/32767
        config.brushless["droite"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)

    def on_R3_down(self,value):
        value = -value*50/32767
        config.brushless["droite"].cmd_vit_pourcent(value)
        TUI.refresh_TUI(self.stdscr)

        
    def on_x_press(self):
        config.myPCA9685.reset()
        TUI.refresh_TUI(self.stdscr)
        
    def on_circle_press(self):
        TUI.refresh_TUI(self.stdscr)






