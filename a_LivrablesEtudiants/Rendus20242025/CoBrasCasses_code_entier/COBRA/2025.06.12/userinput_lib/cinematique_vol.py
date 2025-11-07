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
CX_INDEX = 5
CY_INDEX = 4
CZ_INDEX = 3

DROITE_INDEX  = 0
GAUCHE_INDEX  = 1
AXE_INDEX     = 2
CERCEAU_INDEX = 3

liste_forces_couples = [0 for i in range(6)]

def cmd_forces(liste_forces_couples):
    consignes_moteurs = cinematique_vol_bis(liste_forces_couples)
    print("consigne Cz:",liste_forces_couples[CZ_INDEX])
    config.brushless["droite"].cmd_vit_pourcent(consignes_moteurs[1])#consignes_moteurs[DROITE_INDEX])
    config.brushless["gauche"].cmd_vit_pourcent(consignes_moteurs[2])#consignes_moteurs[GAUCHE_INDEX])
    config.servo["axe"].cmd_angle_deg(consignes_moteurs[0])#consignes_moteurs[AXE_INDEX]*180/np.pi)
    config.servo["cerceau"].cmd_angle_deg(0)#consignes_moteurs[CERCEAU_INDEX]*180/np.pi)

def cmd_force(force_index, value):
    global liste_forces_couples

    liste_forces_couples[force_index] = value
    cmd_forces(liste_forces_couples)

L=0.01 #en m
a=1.6 #N/pourcent de commande moteur
h=0.01 #en m
def cinematique_vol(liste_forces_couples):
    fx,fy,fz,Cx,Cy,Cz = liste_forces_couples
    #Cz /= 10
    #fy /= 1
    #fz*=3
   
    '''renvoie Ud,Ug,Theta1,Theta2 en radians'''
    if fz==0:
        fz=1e-20
    if fx==0:
        fx=1e-20
    #N_F=(fx**2+fy**2+fz**2)**(1/2)
    #return(np.sign(fz)*N_F*(1+Cz/(fx*L*a))/(2*a),np.sign(fz)*N_F*(1-Cz/(fx*L*a))/(2*a),-np.arctan(fx/fz),np.sign(fz)*np.arcsin(fy/N_F))
    return 

def cinematique_vol_bis(liste_forces_couples):
    fx,fy,fz,Cz,Cy,Cx = liste_forces_couples
    if fz==0:
        fz=1e-20
    if fx==0:
        fx=1e-20
    theta=-np.arctan2(fx,fz)
    if theta==0:
        theta=1e-20
    print("theta+Cz: ", theta*180/np.pi+Cz)
    theta=theta
    #return( theta*180/np.pi,((fx**2+fz**2)**(1/2)+Cz/(a*L*np.sin(theta)))/2,((fx**2+fz**2)**(1/2)-Cz/(a*L*np.sin(theta)))/2)
    return(theta*180/np.pi,((fx**2+fz**2)**(1/2)+Cz/(a*L*np.sin(theta)))/2,((fx**2+fz**2)**(1/2)-Cz/(a*L*np.sin(theta)))/2)

def cinematique_vol_ter(liste_forces_couples):
    fx,fy,fz,Cz,Cy,Cx = liste_forces_couples
    N_F=(fx**2+fy**2+fz**2)**(1/2)
    if fz==0:
        fz=1e-10
    if fx==0:
        fx=1e-10
    theta1=np.arctan(fx/fz)
    theta2=np.sign(fz)*np.arcsin(fy/N_F)
    if theta1==0:
        ud=np.sign(fz)*N_F/(2*a)
        ug=ud
    else:
        ud=(np.sign(fz)*N_F+Cz/(L*np.cos(theta2)*np.sin(theta1)))/(2*a)
        ug=(np.sign(fz)*N_F-Cz/(L*np.cos(theta2)*np.sin(theta1)))/(2*a)
    return (ud,ug,theta1,theta2)




if __name__ == "__main__":
    liste_forces_couples = [0,0,0,0,0,0]
    print(cinematique_vol_bis(liste_forces_couples))
