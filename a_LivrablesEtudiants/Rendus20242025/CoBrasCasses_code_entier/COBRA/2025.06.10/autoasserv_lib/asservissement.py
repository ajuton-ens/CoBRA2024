import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import config
import sensors_lib.mergemeas as mergemeas
import time

consigne_position = [0 for i in range(0,6)]
autorise_asservissement = False
erreurs_z   = [0 for i in range (0,40)]
commandes_z = [0 for i in range (0,40)]

def asservir_z():
    global erreur
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
    config.brushless["gauche"].cmd_vit_pourcent(commandes_z[-1])
    config.brushless["droite"].cmd_vit_pourcent(commandes_z[-1])

def asservir_tout():
    global autorise_asservissement

    while True:
        if autorise_asservissement == True:
            asservir_z()
        time.sleep(0.1) 

if __name__ == "__main__":
    consigne_position[mergemeas.Z_INDEX] = 2
    autorise_asservissement = True
    asservir_tout()