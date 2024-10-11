from pyPS4Controller.controller import Controller
import time

###################################################
#Programme de test de la manette PS4
##################################################


class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        
    def on_R2_press(self,value):
        print("La valeur de R2 est: ",value)
        
    def on_R2_release(self):
        print("Arrêt R2")
 
    def on_L3_x_at_rest(self):
        print("L3 au milieu")
        
    def on_R1_press(self):
        print("R1 enfoncé")
        
    def on_R1_release(self):
        print("R1 relaché")
    
    def on_L3_right(self,value):
        print("La valeur de L3 est: ",value)

    def on_L3_left(self,value):
        print("La valeur de L3 est: ",value)
        
    def on_L2_press(self, value):
        print("La valeur de L2 est: ",value)
        
    def on_L2_release(self):
        print("L2 relaché")
        
    def on_x_press(self):
        print("X enfoncé")
        
    def on_circle_press(self):
        print("O enfoncé")


controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()


