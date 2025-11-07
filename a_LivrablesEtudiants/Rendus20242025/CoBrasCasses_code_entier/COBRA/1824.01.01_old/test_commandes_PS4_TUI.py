from pyPS4Controller.controller import Controller
import smbus2
import cobra_pca9685_v11temp as pca9685
import curses

myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C
myPCA9685 = pca9685.PCA9685(myi2cbus) # Initialisation du générateur de PWM

brushless_config = { "propulsion":   {"valeur_repos_us": 1.5*10**3, "seuil_vitesse_neg_pourcent": -4.5, "seuil_vitesse_pos_pourcent": 4.5}
            }

MCC2_config = { "lent":   {"seuil_vitesse_neg_pourcent": -4.5, "seuil_vitesse_pos_pourcent": 4.5}
            }

#FUTABA S3107 : 2.37ms correspond a 0deg du systeme.
#FUTABA S3107 : 1.92ms correspond a 90deg du systeme.
#FUTABA S3107 : 1.38ms correspond a 180deg du systeme.

servo_config = { "cerceau":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286},
                 "axe":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286}
            }


PAGE_BRUSHLESS = 0
PAGE_SERVO = 1
PAGE_MCC = 2
PAGE_WIDTH = 20

height = 0
width = 0
key=0
page_current = 0
cursor_y=0
input_nb=""


def get_motor_value(motor, page_current):
    match page_current:
        case page if page==PAGE_BRUSHLESS:
            return motor.vitesse_pourcent
        case page if page==PAGE_SERVO:
            return motor.angle_deg
        case page if page==PAGE_MCC:
            return motor.vitesse_pourcent

def set_motor_value(motor, page_current, val):
    match page_current:
        case page if page==PAGE_BRUSHLESS:
            motor.cmd_vit_pourcent(val)
        case page if page==PAGE_SERVO:
            motor.cmd_angle_deg(val)
        case page if page==PAGE_MCC:
            motor.cmd_vit_pourcent(val)


def on_any_keypress(stdscr):
    stdscr.clear()
    for page_i in range(0,len(pages)):
        for motor_i in range(0, len(pages[page_i])):
            motor_dict = pages[page_i][motor_i]
            stdscr.addstr(motor_i, PAGE_WIDTH*page_i+1, str(motor_dict[0]))
            stdscr.addstr(motor_i, PAGE_WIDTH*page_i+10, str(round(get_motor_value(motor_dict[1],page_i),5)))
    stdscr.addstr(height-2, 10, str(input_nb))
    stdscr.move(cursor_y,PAGE_WIDTH*page_current)
    stdscr.refresh()

def main(stdscr):
    key=0
    global cursor_y
    global page_current
    global input_nb
    global height
    global width
    height, width = stdscr.getmaxyx()
    CURSOR_Y_MAX=len(pages[page_current])

    controller = MyController(stdscr, interface="/dev/input/js0", connecting_using_ds4drv=False)
    #controller.listen_in_thread()
    controller.listen()
    
    # Boucle_continue/principale
    while key != ord('q'):
        match key:
            case curses.KEY_DOWN:
                if (cursor_y >= CURSOR_Y_MAX-1):
                    page_current = (page_current+1)%len(pages)
                    CURSOR_Y_MAX=len(pages[page_current])
                    cursor_y = 0
                else:
                    cursor_y = cursor_y+1
            case curses.KEY_UP:
                if (cursor_y <= 0):
                    page_current = (page_current-1)%len(pages)
                    CURSOR_Y_MAX=len(pages[page_current])
                    cursor_y = CURSOR_Y_MAX-1
                else:
                    cursor_y = cursor_y-1
            case curses.KEY_LEFT:
                motor = pages[page_current][cursor_y][1]
                motor_value = get_motor_value(motor,page_current)
                set_motor_value(motor,page_current,motor_value-1)
            case curses.KEY_RIGHT:
                motor = pages[page_current][cursor_y][1]
                motor_value = get_motor_value(motor,page_current)
                set_motor_value(motor,page_current,motor_value+1)
            case num if chr(key).isdigit():
                input_nb+=chr(key)
            case minus if minus == ord('-'):
                if (input_nb == ""):
                    input_nb += chr(key)
            case curses.KEY_ENTER | 10 | 13:
                set_motor_value(motor,page_current,int(input_nb))
                input_nb=""
        
        on_any_keypress(stdscr)
        key = stdscr.getch()

    for page_i in range(0,len(pages)):
        for motor_i in range(0, len(pages[page_i])):
            motor_dict = pages[page_i][motor_i]
            set_motor_value(motor_dict[1],page_i,0)

    myPCA9685.reset()



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
        on_any_keypress(self.stdscr)
        
    def on_R1_release(self):
        on_any_keypress(self.stdscr)


    def on_L2_press(self, value):
        value = value*50/32767
        mcc_2pwm["treuil"].cmd_vit_pourcent(value)
        on_any_keypress(self.stdscr)
        
    def on_L2_release(self):
        value = value*50/32767
        mcc_2pwm["treuil"].cmd_vit_pourcent(value)
        on_any_keypress(self.stdscr)


    def on_R2_press(self,value):
        if (value>0) :
            value = value*servo["axe"].angle_max/32767
        else:
            value = -value*servo["axe"].angle_min/32767
        #print("La valeur de R2 est: ",value) # pour tester les touches (on voit le print quand on appuie sur la touche (appelle la fonction))
        servo["axe"].cmd_angle_deg(value)
        on_any_keypress(self.stdscr)

    def on_R2_release(self):
        on_any_keypress(self.stdscr)


    def on_L3_x_at_rest(self):
        on_any_keypress(self.stdscr)
    
    def on_L3_left(self,value):
        value = -value*50/32767
        on_any_keypress(self.stdscr)

    def on_L3_right(self,value):
        value = -value*50/32767
        on_any_keypress(self.stdscr)

    def on_L3_up(self,value):
        value = -value*50/32767
        brushless["gauche"].cmd_vit_pourcent(value)
        on_any_keypress(self.stdscr)

    def on_L3_down(self,value):
        value = -value*50/32767
        brushless["gauche"].cmd_vit_pourcent(value)
        on_any_keypress(self.stdscr)


    def on_R3_x_at_rest(self):
        on_any_keypress(self.stdscr)

    def on_R3_left(self,value):
        value = -value*50/32767
        on_any_keypress(self.stdscr)

    def on_R3_right(self,value):
        value = -value*50/32767
        on_any_keypress(self.stdscr)

    def on_R3_up(self,value):
        value = -value*50/32767
        brushless["droite"].cmd_vit_pourcent(value)
        on_any_keypress(self.stdscr)

    def on_R3_down(self,value):
        value = -value*50/32767
        brushless["droite"].cmd_vit_pourcent(value)
        on_any_keypress(self.stdscr)

        
    def on_x_press(self):
        myPCA9685.reset()
        on_any_keypress(self.stdscr)
        
    def on_circle_press(self):
        on_any_keypress(self.stdscr)



brushless = {}
servo = {}
mcc_2pwm = {}

servo["cerceau"]= pca9685.servo(myPCA9685,4, servo_config["cerceau"])
servo["axe"]= pca9685.servo(myPCA9685,5, servo_config["axe"])
brushless["gauche"] = pca9685.brushless(myPCA9685,6,brushless_config["propulsion"])
brushless["droite"] = pca9685.brushless(myPCA9685,7,brushless_config["propulsion"])
mcc_2pwm["treuil"] = pca9685.MCC_2PWM(myPCA9685,0,1,MCC2_config["lent"])

print("Prêt - Initialisation réalisée")

brushless_list = [list(tup) for tup in list(brushless.items())]
servo_list     = [list(tup) for tup in list(servo.items())]
mcc_list     = [list(tup) for tup in list(mcc_2pwm.items())]
pages = [brushless_list, servo_list, mcc_list]




curses.wrapper(main)




