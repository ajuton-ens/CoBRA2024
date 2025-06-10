import curses
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import motor_lib.cobra_pca9685 as pca9685
import config
import sensors_lib.mergemeas as mergemeas
import autoasserv_lib.asservissement as asserv
import userinput_lib.cinematique_vol as cine_vol


PAGE_BRUSHLESS = 0
PAGE_SERVO = 1
PAGE_MCC = 2
PAGE_SENSORS = 3
PAGE_FORCES = 4
PAGE_WIDTH = 20

height = 0
width = 0
key=0
page_current = 0
cursor_y=0
input_nb=""
TUI_is_exited = False



forces_list    = [[],[],[],[],[],[]]
forces_list[cine_vol.FX_INDEX] = ["fx","useless_column"]
forces_list[cine_vol.FY_INDEX] = ["fy","useless_column"]
forces_list[cine_vol.FZ_INDEX] = ["fz","useless_column"]
forces_list[cine_vol.CX_INDEX] = ["Cx","useless_column"]
forces_list[cine_vol.CY_INDEX] = ["Cy","useless_column"]
forces_list[cine_vol.CZ_INDEX] = ["Cz","useless_column"]
brushless_list = [list(tup) for tup in list(config.brushless.items())]
servo_list     = [list(tup) for tup in list(config.servo.items())]
mcc_list       = [list(tup) for tup in list(config.mcc_2pwm.items())]
sensors_list   = mergemeas.current_measures
pages = [brushless_list, servo_list, mcc_list, sensors_list, forces_list]
aa = [2]

def get_motor_value(motor, page_current, motor_i):
    match page_current:
        case page if page==PAGE_BRUSHLESS:
            return motor.vitesse_pourcent
        case page if page==PAGE_SERVO:
            return motor.angle_deg
        case page if page==PAGE_MCC:
            return motor.vitesse_pourcent
        case page if page==PAGE_SENSORS:
            return motor
        case page if page==PAGE_FORCES:
            #file = open("qwewqeeqw.txt", "w")
            #file.write(str("aaa"))
            #file.close()
            return cine_vol.liste_forces_couples[motor_i]
        

def set_motor_value(motor, page_current, val, motor_index):
    match page_current:
        case page if page==PAGE_BRUSHLESS:
            asserv.autorise_asservissement = False
            motor.cmd_vit_pourcent(val)
        case page if page==PAGE_SERVO:
            asserv.autorise_asservissement = False
            motor.cmd_angle_deg(val)
        case page if page==PAGE_MCC:
            asserv.autorise_asservissement = False
            motor.cmd_vit_pourcent(val)
        case page if page==PAGE_SENSORS:
            if motor_index == -1:
                return
            asserv.autorise_asservissement = True
            asserv.consigne_position[motor_index] = val
        case page if page==PAGE_FORCES:
            asserv.autorise_asservissement = False
            cine_vol.liste_forces_couples[motor_index] = val
            cine_vol.cmd_mot_avec_forces(cine_vol.liste_forces_couples)



def refresh_TUI(stdscr):
    global cursor_y
    global page_current
    global input_nb
    global height
    global width

    stdscr.clear()
    for page_i in range(0,len(pages)):
        for motor_i in range(0, len(pages[page_i])):
            motor_dict = pages[page_i][motor_i]
            stdscr.addstr(motor_i, PAGE_WIDTH*page_i+1, str(motor_dict[0]))
            stdscr.addstr(motor_i, PAGE_WIDTH*page_i+10, str(round(get_motor_value(motor_dict[1],page_i,motor_i),5)))
    stdscr.addstr(height-2, 10, str(input_nb))
    stdscr.move(cursor_y,PAGE_WIDTH*page_current)
    stdscr.refresh()



def TUI_main_loop(stdscr):
    key=0
    global cursor_y
    global page_current
    global input_nb
    global height
    global width
    global TUI_is_exited
    CURSOR_Y_MAX=len(pages[page_current])


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
                motor_value = get_motor_value(motor, page_current, cursor_y)
                set_motor_value(motor,page_current,motor_value-1,cursor_y)
            case curses.KEY_RIGHT:
                motor = pages[page_current][cursor_y][1]
                motor_value = get_motor_value(motor, page_current, cursor_y)
                set_motor_value(motor,page_current,motor_value+1,cursor_y)
            case num if chr(key).isdigit():
                input_nb+=chr(key)
            case minus if minus == ord('-'):
                if (input_nb == ""):
                    input_nb += chr(key)
            case curses.KEY_BACKSPACE:
                input_nb=input_nb[:-1]
            case curses.KEY_ENTER | 10 | 13:
                motor = pages[page_current][cursor_y][1]
                set_motor_value(motor,page_current,int(input_nb),cursor_y)
                input_nb=""
        
        refresh_TUI(stdscr)
        key = stdscr.getch()
    
    TUI_is_exited=True

    for page_i in range(0,len(pages)):
        for motor_i in range(0, len(pages[page_i])):
            motor_dict = pages[page_i][motor_i]
            set_motor_value(motor_dict[1],page_i,0,-1)



def TUI_init(stdscr):
    global height
    global width
    height, width = stdscr.getmaxyx()
