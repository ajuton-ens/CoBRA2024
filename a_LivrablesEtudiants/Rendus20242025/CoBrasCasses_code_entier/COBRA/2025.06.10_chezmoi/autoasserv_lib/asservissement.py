import time
import numpy as np
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import config
import sensors_lib.mergemeas as mergemeas
import userinput_lib.cinematique_vol as cine_vol

consigne_position = [0 for i in range(0,6)]
autorise_asservissement = False
erreurs_x   = [0 for i in range (0,40)]
erreurs_y   = [0 for i in range (0,40)]
erreurs_z   = [0 for i in range (0,40)]
commandes_x = [0 for i in range (0,40)]
commandes_y = [0 for i in range (0,40)]
commandes_z = [0 for i in range (0,40)]

def asservir_x():
    global erreurs_x
    global commandes_x
    kp=30
    Ti=1000000#10
    Kd=0#2

    erreurs_x[:-1] = erreurs_x[1:]
    erreurs_x[-1] = consigne_position[mergemeas.X_INDEX]-mergemeas.current_measures[mergemeas.X_INDEX][1]
    commandes_x[:-1] = commandes_x[1:]

    d_erreur_dt = erreurs_x[-1]-erreurs_x[-4]
    d_erreur_dt2 = erreurs_x[-4]-erreurs_x[-7]
    acceleration = d_erreur_dt - d_erreur_dt2

    commandes_x[-1] = erreurs_x[-1]*kp*(-Kd*d_erreur_dt+1+sum(erreurs_x[:-2])/Ti)
    commandes_x[-1] = max(min(commandes_x[-1],80),-80)

    heading = mergemeas.current_measures[mergemeas.HEADING_INDEX]*np.pi/180
    cine_vol.liste_forces_couples[cine_vol.FX_INDEX] += np.cos(-heading)*commandes_x[-1]
    cine_vol.liste_forces_couples[cine_vol.FY_INDEX] += np.sin(-heading)*commandes_x[-1]

def asservir_y():
    global erreurs_y
    global commandes_y
    kp=30
    Ti=1000000#10
    Kd=0#2

    erreurs_y[:-1] = erreurs_y[1:]
    erreurs_y[-1] = consigne_position[mergemeas.Y_INDEX]-mergemeas.current_measures[mergemeas.Y_INDEX][1]
    commandes_y[:-1] = commandes_y[1:]

    d_erreur_dt = erreurs_y[-1]-erreurs_y[-4]
    d_erreur_dt2 = erreurs_y[-4]-erreurs_y[-7]
    acceleration = d_erreur_dt - d_erreur_dt2

    commandes_y[-1] = erreurs_y[-1]*kp*(-Kd*d_erreur_dt+1+sum(erreurs_y[:-2])/Ti)
    commandes_y[-1] = max(min(commandes_y[-1],80),-80)

    heading = mergemeas.current_measures[mergemeas.HEADING_INDEX]*np.pi/180
    cine_vol.liste_forces_couples[cine_vol.FX_INDEX] += -np.sin(-heading)*commandes_y[-1]
    cine_vol.liste_forces_couples[cine_vol.FY_INDEX] +=  np.cos(-heading)*commandes_y[-1]


def asservir_z():
    global erreurs_z
    global commandes_z
    kp=30
    Ti=1000000#10
    Kd=0#2
    acc_min = 0.05
    valeur_repos = 0
    change_valeur_repos = True

    erreurs_z[:-1] = erreurs_z[1:]
    erreurs_z[-1] = consigne_position[mergemeas.Z_INDEX]-mergemeas.current_measures[mergemeas.Z_INDEX][1]
    commandes_z[:-1] = commandes_z[1:]

    d_erreur_dt = erreurs_z[-1]-erreurs_z[-4]
    d_erreur_dt2 = erreurs_z[-4]-erreurs_z[-7]
    acceleration = d_erreur_dt - d_erreur_dt2
    if abs(acceleration) > acc_min:
        if change_valeur_repos == True and commandes_z[-1]>0:
            valeur_repos -= 4*acceleration
        change_valeur_repos = False
    else:
        change_valeur_repos = True

    commandes_z[-1] = valeur_repos+erreurs_z[-1]*kp*(-Kd*d_erreur_dt+1+sum(erreurs_z[:-2])/Ti)
    commandes_z[-1] = max(min(commandes_z[-1],80),-80)
    cine_vol.liste_forces_couples[cine_vol.FZ_INDEX] += commandes_z[-1]

def asservir_tout():
    global autorise_asservissement

    while True:
        if autorise_asservissement == True:
            cine_vol.liste_forces_couples[cine_vol.FX_INDEX] = 0
            cine_vol.liste_forces_couples[cine_vol.FY_INDEX] = 0
            cine_vol.liste_forces_couples[cine_vol.FZ_INDEX] = 0
            asservir_z()
            asservir_x()
            asservir_y()
            cine_vol.cmd_force(cine_vol.FX_INDEX, cine_vol.liste_forces_couples[cine_vol.FX_INDEX])
            cine_vol.cmd_force(cine_vol.FY_INDEX, cine_vol.liste_forces_couples[cine_vol.FY_INDEX])
            cine_vol.cmd_force(cine_vol.FZ_INDEX, cine_vol.liste_forces_couples[cine_vol.FZ_INDEX])
        time.sleep(0.1)

if __name__ == "__main__":
    consigne_position[mergemeas.Z_INDEX] = 2
    autorise_asservissement = True
    asservir_tout()
