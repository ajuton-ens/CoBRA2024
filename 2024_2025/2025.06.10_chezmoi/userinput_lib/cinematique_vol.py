import numpy as np
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import config

FX_INDEX = 0
FY_INDEX = 1
FZ_INDEX = 2
CX_INDEX = 3
CY_INDEX = 4
CZ_INDEX = 5

DROITE_INDEX  = 0
GAUCHE_INDEX  = 1
AXE_INDEX     = 2
CERCEAU_INDEX = 3

liste_forces_couples = [0 for i in range(6)]

def cmd_force(force_index, value ):
    global liste_forces_couples

    liste_forces_couples[force_index] = value
    consignes_moteurs = cinematique_vol(liste_forces_couples)
    config.brushless["droite"].cmd_vit_pourcent(consignes_moteurs[DROITE_INDEX])
    config.brushless["gauche"].cmd_vit_pourcent(consignes_moteurs[GAUCHE_INDEX])
    config.servo["axe"].cmd_angle_deg(consignes_moteurs[AXE_INDEX]*180/np.pi)
    config.servo["cerceau"].cmd_angle_deg(consignes_moteurs[CERCEAU_INDEX]*180/np.pi)

L=0.01 #en m
a=1.5 #N/pourcent de commande moteur
h=0.01 #en m
def cinematique_vol(liste_forces_couples):
    fx,fy,fz,Cx,Cy,Cz = liste_forces_couples
    '''renvoie Ud,Ug,Theta3,Theta2 en radians'''
    if fx==0:
        fx=1e-20
    N_F=(fx**2+fy**2+fz**2)**(1/2)
    return(N_F*(1+Cz/(fx*L*a))/(2*a),N_F*(1-Cz/(fx*L*a))/(2*a),-np.arctan(fz/fx),np.arcsin(fy/N_F))



if __name__ == "__main__":
    liste_forces_couples = [0,0,0,0,0,0]
    print(cinematique_vol(liste_forces_couples))
