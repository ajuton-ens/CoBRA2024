from pyPS4Controller.controller import Controller


class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)
        
    def on_R2_press(self,value):
        print("La valeur de R2 est: ",value)
        
        
    def on_R2_release(self):
         print("Arrêt complet")
         
        
    
    def on_R1_press(self):
        pwm_prop.change_duty_cycle(5)
        
    def on_R1_release(self):
        pwm_prop.change_duty_cycle(max_prop)
        
    
    
    
    def on_L3_right(self,value):
        print("La valeur de L3 est: ",value)
        
    def on_L3_left(self,value):
        pass
        
    def on_x_press(self):
        print("PWM activées")
        
    def on_circle_press(self):
        print("PWM arrêtées")



controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
controller.listen()
