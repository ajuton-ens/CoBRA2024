import numpy as np
import time
import curses
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import config
import autoasserv_lib.asservissement as asserv
import userinput_lib.cinematique_vol as cine_vol


PAGE_BRUSHLESS = 0
PAGE_SERVO = 1
PAGE_MCC = 2
PAGE_SENSORS = 3
PAGE_FORCES = 4
PAGE_WIDTH = 20



class TUI:
    def __init__(self, stdscr, matrice_etats, autorise_asservissement):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()

        self.matrice_etats = matrice_etats

        self.autorise_asservissement = autorise_asservissement
        
        self.page_current = 0
        self.cursor_y=0
        self.input_nb=""
        self.TUI_is_exited = False
        
        self.brushless_list = np.array([list(tup) for tup in list(config.brushless.items())])
        self.servo_list     = np.array([list(tup) for tup in list(config.servo.items())])
        self.mcc_list       = np.array([list(tup) for tup in list(config.mcc_2pwm.items())])
        
        self.sensor_data_list   = np.array([["aa",0] for i in range(config.NB_AXES)])
        self.sensor_data_list[config.X_INDEX,       :] = np.array(["X",       self.matrice_etats[config.MESURES_INDEX*config.NB_AXES+config.X_INDEX,       -1]]) 
        self.sensor_data_list[config.Y_INDEX,       :] = np.array(["Y",       self.matrice_etats[config.MESURES_INDEX*config.NB_AXES+config.Y_INDEX,       -1]])
        self.sensor_data_list[config.Z_INDEX,       :] = np.array(["Z",       self.matrice_etats[config.MESURES_INDEX*config.NB_AXES+config.Z_INDEX,       -1]])
        self.sensor_data_list[config.PITCH_INDEX,   :] = np.array(["Roulis",  self.matrice_etats[config.MESURES_INDEX*config.NB_AXES+config.ROLL_INDEX,    -1]])
        self.sensor_data_list[config.ROLL_INDEX,    :] = np.array(["Tangage", self.matrice_etats[config.MESURES_INDEX*config.NB_AXES+config.PITCH_INDEX,   -1]])
        self.sensor_data_list[config.HEADING_INDEX, :] = np.array(["Lacet",   self.matrice_etats[config.MESURES_INDEX*config.NB_AXES+config.HEADING_INDEX, -1]])

        self.forces_list = np.array([["aa",0] for i in range(config.NB_AXES)])
        self.forces_list[config.X_INDEX,       :] = np.array(["fx",      self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES+config.X_INDEX,       -1]])
        self.forces_list[config.Y_INDEX,       :] = np.array(["fy",      self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES+config.Y_INDEX,       -1]])
        self.forces_list[config.Z_INDEX,       :] = np.array(["fz",      self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES+config.Z_INDEX,       -1]])
        self.forces_list[config.ROLL_INDEX,    :] = np.array(["Roulis",  self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES+config.ROLL_INDEX,    -1]])
        self.forces_list[config.PITCH_INDEX,   :] = np.array(["Tangage", self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES+config.PITCH_INDEX,   -1]])
        self.forces_list[config.HEADING_INDEX, :] = np.array(["Lacet",   self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES+config.HEADING_INDEX, -1]])

        self.pages = [self.brushless_list, self.servo_list, self.mcc_list, self.sensor_data_list, self.forces_list]


    def get_motor_value(self, page_i, motor_i):
        motor = self.pages[page_i][motor_i][1]
        
        match page_i:
            case page if page==PAGE_BRUSHLESS:
                return motor.vitesse_pourcent
            case page if page==PAGE_SERVO:
                return motor.angle_deg
            case page if page==PAGE_MCC:
                return motor.vitesse_pourcent
            case page if page==PAGE_SENSORS:
                return motor
                #return asserv.truc
            case page if page==PAGE_FORCES:
                #file = open("qwewqeeqw.txt", "w")
                #file.write(str("aaa"))
                #file.close()
                return self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES+motor_i, -1]


    def set_motor_value(self, page_i, motor_i, val):
        motor = self.pages[page_i][motor_i][1]

        match page_i:
            case page if page==PAGE_BRUSHLESS:
                self.autorise_asservissement = False
                motor.cmd_vit_pourcent(val)
            case page if page==PAGE_SERVO:
                self.autorise_asservissement = False
                motor.cmd_angle_deg(val)
            case page if page==PAGE_MCC:
                self.autorise_asservissement = False
                motor.cmd_vit_pourcent(val)
            case page if page==PAGE_SENSORS:
                self.autorise_asservissement = True
                config.Consignes_Positions[motor_i, :] = val
            case page if page==PAGE_FORCES:
                self.autorise_asservissement = False
                
                measures_array = self.matrice_etats[config.MESURES_INDEX*config.NB_AXES:(config.MESURES_INDEX+1)*config.NB_AXES,-1].copy()
                asservissements_dict = asserv.create_null_asserv_dict()
                

                asservissements_dict["COMMANDES_FORCES"] = self.matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES:(config.COMMANDES_FORCES_INDEX+1)*config.NB_AXES,-1].copy()
                


                asserv.update_matrice_etats(self.matrice_etats, time.time(), measures_array, asservissements_dict)
                
                cine_vol.cmd_force(asservissements_dict["COMMANDES_FORCES"], motor_i, val)



    def refresh_TUI(self):
        global cursor_y
        global page_current
        global input_nb
        global height
        global width

        self.stdscr.clear()
        for page_i in range(0,len(self.pages)):
            for motor_i in range(0, len(self.pages[page_i])):
                self.stdscr.addstr(motor_i, PAGE_WIDTH*page_i+1, str(self.pages[page_i][motor_i][0]))
                self.stdscr.addstr(motor_i, PAGE_WIDTH*page_i+10, str(round(float(self.get_motor_value(page_i,motor_i)),5)))
        self.stdscr.addstr(self.height-2, 10, str(self.input_nb))
        self.stdscr.move(self.cursor_y,PAGE_WIDTH*self.page_current)
        self.stdscr.refresh()



    def TUI_main_loop(self):
        key=0
        CURSOR_Y_MAX=len(self.pages[self.page_current])


        # Boucle_continue/principale
        while key != ord('q'):
            match key:
                case curses.KEY_DOWN:
                    if (self.cursor_y >= CURSOR_Y_MAX-1):
                        self.page_current = (self.page_current+1)%len(self.pages)
                        CURSOR_Y_MAX=len(self.pages[self.page_current])
                        self.cursor_y = 0
                    else:
                        self.cursor_y = self.cursor_y+1
                case curses.KEY_UP:
                    if (self.cursor_y <= 0):
                        self.page_current = (self.page_current-1)%len(self.pages)
                        CURSOR_Y_MAX=len(self.pages[self.page_current])
                        self.cursor_y = CURSOR_Y_MAX-1
                    else:
                        self.cursor_y = self.cursor_y-1
                case curses.KEY_LEFT:
                    motor_value = self.get_motor_value(self.page_current, self.cursor_y)
                    self.set_motor_value(self.page_current,self.cursor_y, motor_value-1)
                case curses.KEY_RIGHT:
                    motor_value = self.get_motor_value(self.page_current, self.cursor_y)
                    self.set_motor_value(self.page_current, self.cursor_y, motor_value+1)
                case num if chr(key).isdigit():
                    self.input_nb+=chr(key)
                case minus if minus == ord('-'):
                    if (self.input_nb == ""):
                        self.input_nb += chr(key)
                case dot if dot == ord('.'):
                    self.input_nb+=chr(key)
                case curses.KEY_BACKSPACE:
                    self.input_nb=input_nb[:-1]
                case curses.KEY_ENTER | 10 | 13:
                    self.set_motor_value(self.page_current,self.cursor_y,float(self.input_nb))
                    self.input_nb=""
            
            self.refresh_TUI()
            key = self.stdscr.getch()
        
        self.TUI_is_exited=True

        for page_i in range(0,len(self.pages)):
            for motor_i in range(0, len(self.pages[page_i])):
                if motor_i not in [PAGE_SENSORS, PAGE_FORCES]:
                    self.set_motor_value(page_i,motor_i,0)



