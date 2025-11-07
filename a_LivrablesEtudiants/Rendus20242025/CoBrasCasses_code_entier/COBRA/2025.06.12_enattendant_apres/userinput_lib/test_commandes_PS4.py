import time
from pyPS4Controller.controller import Controller
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import config
import userinput_lib.test_commandes_TUI as TUI
import userinput_lib.cinematique_vol as cine_vol

###################################################
#Programme de test de la manette PS4
##################################################

class MyController(Controller):

    def __init__(self, MyTUI, matrice_etats, **kwargs):
        Controller.__init__(self, **kwargs)
        self.MyTUI = MyTUI
        self.matrice_etats = matrice_etats
        self.pointeur_forces_couples=self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES:(config.COMMANDES_FORCES_INDEX+1)*config.NB_AXES,-1]
        self._left_down = False
        self._right_down = False
        self._up_down = False
        self._down_down = False
        self.fy_increment = 0
        self.treuil_commande = 0

    """
    def __getattr__(self, name):
        if name.startswith("on_"):
            def handler(*args, **kwargs):
                on_any_keypress()
            return handler
        #else:
            #raise AttributeError(f"'{name}' attribute not found")
    """

    def timeloop(self):
        while True:
            fy = self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES+config.Y_INDEX,-1]
            if fy>=0:
                cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.Y_INDEX, min( 40,fy+self.fy_increment/40))
            else:
                cine_vol.cmd_force(self.pointeur_forces_couples.copy(), config.Y_INDEX, max(-40,fy+self.fy_increment/40))
            self.MyTUI.refresh_TUI()
            time.sleep(0.02)

    def on_R1_press(self):
        self.MyTUI.refresh_TUI()
        
        
    def on_R1_release(self):
        self.MyTUI.refresh_TUI()

    def on_L1_press(self):
        self.MyTUI.refresh_TUI()
        
        
    def on_L1_release(self):
        self.MyTUI.refresh_TUI()

    def on_L2_press(self, value):
        value = (value + 32767)/32767
        self.fy_increment = value
        self.MyTUI.refresh_TUI()
    
    def on_L2_release(self):
        self.fy_increment=0
        self.MyTUI.refresh_TUI()


    def on_R2_press(self,value):
        value = -(value + 32767)/32767
        self.fy_increment = value
        self.MyTUI.refresh_TUI()

    def on_R2_release(self):
        self.fy_increment=0
        self.MyTUI.refresh_TUI()


    def on_L3_x_at_rest(self):
        self.MyTUI.refresh_TUI()
    
    def on_L3_left(self,value):
        cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.PITCH_INDEX, value/32767)
        self.MyTUI.refresh_TUI()

    def on_L3_right(self,value):
        cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.PITCH_INDEX, value/32767)
        self.MyTUI.refresh_TUI()

    def on_L3_up(self,value):
        value = +value/32767
        cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.Z_INDEX, value)
        self.MyTUI.refresh_TUI()

    def on_L3_down(self,value):
        value = +value/32767
        cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.Z_INDEX, value)
        self.MyTUI.refresh_TUI()


    def on_R3_x_at_rest(self):
        self.MyTUI.refresh_TUI()

    def on_R3_left(self,value):
        cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.HEADING_INDEX, value/32767)
        self.MyTUI.refresh_TUI()

    def on_R3_right(self,value):
        cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.HEADING_INDEX, value/32767)
        self.MyTUI.refresh_TUI()

    def on_R3_up(self,value):
        cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.X_INDEX, value/32767)
        self.MyTUI.refresh_TUI()

    def on_R3_down(self,value):
        cine_vol.cmd_force(self.pointeur_forces_couples.copy(),config.X_INDEX, value/32767)
        self.MyTUI.refresh_TUI()


    def on_up_arrow_press(self):
        self.treuil_commande = max(-100,self.treuil_commande - 100)
        config.mcc_2pwm["treuil"].cmd_vit_pourcent(self.treuil_commande)
        self.MyTUI.refresh_TUI()

    def on_up_arrow_release(self):
        self.treuil_commande = 0
        self.MyTUI.refresh_TUI()

    def on_down_arrow_press(self):
        self.treuil_commande = min(100,self.treuil_commande + 100)
        config.mcc_2pwm["treuil"].cmd_vit_pourcent(self.treuil_commande)
        self.MyTUI.refresh_TUI()

    def on_down_arrow_release(self):
        self.treuil_commande = 0
        self.MyTUI.refresh_TUI()

    def on_x_press(self):
        config.myPCA9685.reset()
        self.MyTUI.refresh_TUI()
        self.MyTUI.TUI_is_exited = True
        
    def on_circle_press(self):
        self.MyTUI.refresh_TUI()
