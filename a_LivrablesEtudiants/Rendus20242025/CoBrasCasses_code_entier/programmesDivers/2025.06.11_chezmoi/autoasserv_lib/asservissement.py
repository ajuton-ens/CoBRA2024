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

consignes_position = np.zeros(1,1)
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

    #return erreurs_R_dir[:,-1]*Kp+(1+erreurs_R_dir[:,:-2].sum(axis=1)/Ti-Td*d_erreur_dt)
    return Kp*( \
              erreurs_R_dir[:,-1]*(1+Te/Ti+N*Td/(1+N*Te)) \
            - erreurs_R_dir[:,-2]*(1+2*N*Td/(1+N*Te))\
            + erreurs_R_dir[:,-3]*N*Td/(1+N*Te) \
            ) \
            - commandes[:,-2]*(1-N*Te)/(1+N*Te) \
            - commandes[:,-2]*0


saturation_efforts=[(-40,40),(-40,40),(-40,40),(-40,40),(-40,40),(-40,40)]
def asservir_tout():
    global autorise_asservissement

    if autorise_asservissement == True:
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
        efforts = asservir_commande()
        #efforts=[K*erreur for erreur in erreur_R_dir]
        efforts_sat = [min(max(efforts[i],saturation_efforts[i][0]),saturation_efforts[i][1]) for i in range(6)]
        commandes[:,-1] = efforts_sat
        cine_vol.liste_forces_couples = efforts_sat
        cine_vol.cmd_forces(efforts_sat)
        if([[erreurs_R_dir[i,j]<epsilon_err[j] for j in range(40)] for i in range(6)] == [[True for j in range(40)] for i in range(6)]) and ([[erreurs_R_dir[i,j]<epsilon_vit[j] for j in range(40)] for i in range(6)] == [[True for j in range(40)] for i in range(6)]):
            asservissement_is_finished = True
        else:
            asservissement_is_finished = False


if __name__ == "__main__":
    consigne_position[mergemeas.Z_INDEX] = 2
    autorise_asservissement = True
    asservir_tout()
