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
# test modélisation- Maurice
import datetime


consigne_position = [3,5,1,0,0,0]
consignes_position = np.zeros((6,4))
consignes_position[mergemeas.X_INDEX,:] = 2
consignes_position[mergemeas.Y_INDEX,0:1] = 2
consignes_position[mergemeas.Z_INDEX,0] = 1
consignes_position[mergemeas.Z_INDEX,1:2] = 2
consignes_position[mergemeas.Y_INDEX,2:3] = 5
consignes_position[mergemeas.Z_INDEX,3] = 1
autorise_asservissement = False
erreurs_heading   = [0 for i in range (0,40)]

def chgt_base_atr_dir(lacet,roulis,tangage):
    '''angles en radians'''
    M=[[0,0,0],[0,0,0],[0,0,0]]
    M[0][0]=np.cos(tangage)*np.cos(lacet)
    M[0][1]=np.cos(tangage)*np.sin(lacet)
    M[0][2]=np.sin(tangage)
    M[1][0]=np.sin(roulis)*np.sin(tangage)*np.cos(lacet)-np.cos(roulis)*np.sin(lacet)
    M[1][1]=np.cos(roulis)*np.cos(lacet)+np.sin(lacet)*np.sin(tangage)*np.sin(roulis)
    M[1][2]=-np.sin(roulis)*np.cos(tangage)
    M[2][0]=-np.sin(roulis)*np.sin(lacet)-np.cos(roulis)*np.cos(lacet)*np.sin(tangage)
    M[2][1]=np.sin(roulis)*np.cos(lacet)-np.cos(roulis)*np.sin(tangage)*np.sin(lacet)
    M[2][2]=np.cos(roulis)*np.cos(tangage)
    return M




"""
class asservissement_position():
    def __init__(self, POS_INDEX):
        # DÉFINITION des registres (valeurs initiales)
        self.erreurs   = [0 for i in range (0,40)]
        self.commandes = [0 for i in range (0,40)]
        self.lambda_fx  = lambda_fx
    
    def PID(self, consigne, mesure):
        kp=30
        Ti=1000000#10
        Kd=0#2

        self.erreurs[:-1] = self.erreurs[1:]
        self.erreurs[-1] = consigne-mesure
        self.commandes[:-1] = self.commandes[1:]

        d_erreur_dt = self.erreurs[-1]-self.erreurs[-4]
        d_erreur_dt2 = self.erreurs[-4]-self.erreurs[-7]
        acceleration = d_erreur_dt - d_erreur_dt2

        self.commandes[-1] = self.erreurs[-1]*kp*(-Kd*d_erreur_dt+1+sum(self.erreurs[:-2])/Ti)
        self.commandes[-1] = max(min(self.commandes[-1],80),-80)

        heading = mergemeas.current_measures[mergemeas.HEADING_INDEX][1]*np.pi/180
        cine_vol.liste_forces_couples[cine_vol.FX_INDEX] += np.cos(-heading)*self.commandes[-1]
        cine_vol.liste_forces_couples[cine_vol.FY_INDEX] += np.sin(-heading)*self.commandes[-1]

def asservir_heading():
    global erreurs_heading
    global commandes_heading
    kp=30
    Ti=1000000#10
    Kd=0#2

    erreurs_heading[:-1] = erreurs_heading[1:]
    erreurs_heading[-1] = consigne_position[mergemeas.HEADING_INDEX]-mergemeas.current_measures[mergemeas.HEADING_INDEX][1]
    commandes_heading[:-1] = commandes_heading[1:]

    d_erreur_dt = erreurs_heading[-1]-erreurs_heading[-4]
    d_erreur_dt2 = erreurs_heading[-4]-erreurs_heading[-7]
    acceleration = d_erreur_dt - d_erreur_dt2

    commandes_heading[-1] = erreurs_heading[-1]*kp*(-Kd*d_erreur_dt+1+sum(erreurs_heading[:-2])/Ti)
    commandes_heading[-1] = max(min(commandes_heading[-1],80),-80)

    cine_vol.liste_forces_couples[cine_vol.CZ_INDEX] += commandes_heading[-1]

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

    heading = mergemeas.current_measures[mergemeas.HEADING_INDEX][1]*np.pi/180
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

    heading = mergemeas.current_measures[mergemeas.HEADING_INDEX][1]*np.pi/180
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
"""
epsilon_err = [1,1,1,1,1,1]
epsilon_vit = [1,1,1,1,1,1]
erreurs_R_dir = np.zeros((6,40))
commandes     = np.zeros((6,40))
Kp = [1,1,1,1,1,1]
Td = [1,1,1,1,1,1]
Ti = [1000,1000,1000,1000,1000,1000]
asservissement_is_finished = False

def asservir_commande():
    global erreurs_R_dir
    global commandes
    global Kp
    global Td
    global Ti
    global asservissement_is_finished

    d_erreur_dt = erreurs_R_dir[:,-1]-erreurs_R_dir[:,-4]
    d_erreur_dt2 = erreurs_R_dir[:,-4]-erreurs_R_dir[:,-7]
    acceleration = d_erreur_dt - d_erreur_dt2

    return erreurs_R_dir[:,-1]*Kp*(1+erreurs_R_dir[:,:-2].sum(axis=1)/Ti-Td*d_erreur_dt)
    

saturation_efforts=[(-40,40),(-40,40),(-40,40),(-40,40),(-40,40),(-40,40)]
truc=0
def asservir_tout():
    global autorise_asservissement
    global truc
    K=10
    #écriture fichier pour modlisation modèle- Maurice
    #f = open("/home/cobra5/COBRA/2025.06.12/autoasserv_lib/asserv.txt", "w")
    while True:
        
        if autorise_asservissement == True:

            truc+=1
            mes = [item[1] for item in mergemeas.current_measures] #mes xyz, theta xyz 
            mes[3]  = -mes[3]+270
            mes[3:] = [mes[i]*np.pi/180 for i in range(3,6)]
            cons=consigne_position #consigne en xyz, theta xyz
            erreur_R_atr = [cons[i]-mes[i] for i in range(6)]
            M=chgt_base_atr_dir(*mes[3:])
            erreur_R_dir = [ sum([M[i][j]*erreur_R_atr[j] for j in range(3)]) for i in range(3)]+erreur_R_atr[3:]
            erreurs_R_dir[:,:-1] = erreurs_R_dir[:,1:]
            erreurs_R_dir[:,-1] = erreur_R_dir
            commandes[:,:-1] = commandes[:,1:]
            #efforts = asservir_commande()
            efforts=[K*erreur for erreur in erreur_R_dir]
            efforts_sat = [min(max(efforts[i],saturation_efforts[i][0]),saturation_efforts[i][1]) for i in range(6)]
            commandes[:,-1] = efforts_sat
            cine_vol.liste_forces_couples = efforts_sat
            cine_vol.cmd_forces(efforts_sat)
            #if([[erreurs_R_dir[i,j]<epsilon_err[i] for j in range(40)] for i in range(6)] == [[True for j in range(40)] for i in range(6)]) and ([[erreurs_R_dir[i,j]<epsilon_vit[j] for j in range(40)] for i in range(6)] == [[True for j in range(40)] for i in range(6)]):
                #asservissement_is_finished = True
            #else:
                #asservissement_is_finished = False
            #now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            #f.write(f"{now} {mes} {cons} \n")
            #f.flush()
        time.sleep(0.1)

if __name__ == "__main__":
    consigne_position[mergemeas.Z_INDEX] = 2
    autorise_asservissement = True
    asservir_tout()
