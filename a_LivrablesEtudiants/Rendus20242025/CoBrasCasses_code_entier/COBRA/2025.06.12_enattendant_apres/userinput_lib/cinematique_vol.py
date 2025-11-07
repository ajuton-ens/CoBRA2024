import numpy as np
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import config

L=0.01 #en m
a=1.6 #N/pourcent de commande moteur
h=0.01 #en m

def cmd_forces(liste_forces_couples):
    consignes_moteurs = cinematique_vol_bis(liste_forces_couples)
    config.brushless["droite"].cmd_vit_pourcent(consignes_moteurs[config.DROITE_INDEX])
    config.brushless["gauche"].cmd_vit_pourcent(consignes_moteurs[config.GAUCHE_INDEX])
    config.servo["axe"].cmd_angle_deg(consignes_moteurs[config.AXE_INDEX]*180/np.pi)
    config.servo["cerceau"].cmd_angle_deg(consignes_moteurs[config.CERCEAU_INDEX]*180/np.pi)

def cmd_force(liste_forces_couples,force_index, value):
    liste_forces_couples[force_index] = value
    cmd_forces(liste_forces_couples)

def cinematique_vol(liste_forces_couples):
    fx,fy,fz,Cx,Cy,Cz = liste_forces_couples
    #Cz /= 10
    #fy /= 1
    #fz*=3
   
    '''renvoie Ud,Ug,Theta1,Theta2 en degres'''
    if fz==0:
        fz=1e-20
    if fx==0:
        fx=1e-20
    N_F=(fx**2+fy**2+fz**2)**(1/2)
    commandes = [0 for i in range(len(config.NB_ACTIONNEURS))]
    commandes[config.GAUCHE_INDEX]  = np.sign(fz)*N_F*(1-Cz/(fx*L*a))/(2*a)
    commandes[config.DROITE_INDEX]  = np.sign(fz)*N_F*(1+Cz/(fx*L*a))/(2*a)
    commandes[config.AXE_INDEX]     = -np.arctan(fx/fz)*180/np.pi
    commandes[config.CERCEAU_INDEX] = np.sign(fz)*np.arcsin(fy/N_F)*180/np.pi
    return commandes
    
def cinematique_vol_bis(liste_forces_couples):
    fx,fy,fz,Cz,Cy,Cx = liste_forces_couples
    if fz==0:
        fz=1e-20
    if fx==0:
        fx=1e-20
    theta=-np.arctan2(fx,fz)
    if theta==0:
        theta=1e-20
    theta=theta
    commandes = [0 for i in range(config.NB_ACTIONNEURS)]
    commandes[config.GAUCHE_INDEX]  = ((fx**2+fz**2)**(1/2)-Cz/(a*L*np.sin(theta)))/2
    commandes[config.DROITE_INDEX]  = ((fx**2+fz**2)**(1/2)+Cz/(a*L*np.sin(theta)))/2
    commandes[config.AXE_INDEX]     = theta*180/np.pi
    commandes[config.CERCEAU_INDEX] = 0*180/np.pi
    return commandes

if __name__ == "__main__":
    liste_forces_couples = [0,0,0,0,0,0]
    print(cinematique_vol_bis(liste_forces_couples))
