import time
import numpy as np
if __name__ == "__main__":
     import os
     import sys
     current_dir = os.path.dirname(os.path.abspath(__file__))
     parent_dir = os.path.dirname(current_dir)
     sys.path.append(parent_dir)
import sensors_lib.merge_meas as merge_meas
import userinput_lib.cinematique_vol as cine_vol
import autoasserv_lib.PID as PID
import config
# test modélisation- Maurice

def chgt_base_atr_dir(lacet,roulis,tangage):
    X_INDEX       = config.X_INDEX
    Y_INDEX       = config.Y_INDEX
    Z_INDEX       = config.Z_INDEX
    HEADING_INDEX = config.HEADING_INDEX
    PITCH_INDEX   = config.PITCH_INDEX
    ROLL_INDEX    = config.ROLL_INDEX

    '''angles en radians'''
    M=np.zeros((config.NB_AXES,config.NB_AXES))
    M[X_INDEX][X_INDEX]=np.cos(tangage)*np.cos(lacet)
    M[X_INDEX][Y_INDEX]=np.cos(tangage)*np.sin(lacet)
    M[X_INDEX][Z_INDEX]=np.sin(tangage)
    M[Y_INDEX][X_INDEX]=np.sin(roulis)*np.sin(tangage)*np.cos(lacet)-np.cos(roulis)*np.sin(lacet)
    M[Y_INDEX][Y_INDEX]=np.cos(roulis)*np.cos(lacet)+np.sin(lacet)*np.sin(tangage)*np.sin(roulis)
    M[Y_INDEX][Z_INDEX]=-np.sin(roulis)*np.cos(tangage)
    M[Z_INDEX][X_INDEX]=-np.sin(roulis)*np.sin(lacet)-np.cos(roulis)*np.cos(lacet)*np.sin(tangage)
    M[Z_INDEX][Y_INDEX]=np.sin(roulis)*np.cos(lacet)-np.cos(roulis)*np.sin(tangage)*np.sin(lacet)
    M[Z_INDEX][Z_INDEX]=np.cos(roulis)*np.cos(tangage)
    M[HEADING_INDEX][HEADING_INDEX] = 1
    M[PITCH_INDEX][PITCH_INDEX]     = 1
    M[ROLL_INDEX][ROLL_INDEX]       = 1
    return M

def asservir_commande(erreur_R_dir,matrice_etats):
    d_erreur_dt = matrice_etats[config.ERREURS_INDEX*config.NB_AXES:(config.ERREURS_INDEX+1)*config.NB_AXES,-1]-matrice_etats[config.ERREURS_INDEX*config.NB_AXES:(config.ERREURS_INDEX+1)*config.NB_AXES,-3]
    d_erreur_dt2 = matrice_etats[config.ERREURS_INDEX*config.NB_AXES:(config.ERREURS_INDEX+1)*config.NB_AXES,-3]-matrice_etats[config.ERREURS_INDEX*config.NB_AXES:(config.ERREURS_INDEX+1)*config.NB_AXES,-6]
    acceleration = d_erreur_dt - d_erreur_dt2

    return erreur_R_dir*config.Kp*(1+matrice_etats[config.ERREURS_INDEX*config.NB_AXES:(config.ERREURS_INDEX+1)*config.NB_AXES,:].sum(axis=1)/config.Ti-config.Td*d_erreur_dt)





def asservir_tout(MyPID, last_measures,consigne_position,matrice_etats):
    asservissements_dict = {}
    asservissements_dict["CONSIGNES_POSITIONS"] = np.zeros((config.NB_AXES))
    asservissements_dict["ERREURS"] = np.zeros((config.NB_AXES))
    asservissements_dict["COMMANDES_FORCES"] = np.zeros((config.NB_AXES))

    mes = last_measures.copy() #mes xyz, theta xyz 
    mes[config.HEADING_INDEX]  = -mes[config.HEADING_INDEX]+270
    mes[config.HEADING_INDEX] *= np.pi/180
    mes[config.PITCH_INDEX]   *= np.pi/180
    mes[config.ROLL_INDEX]    *= np.pi/180
    cons=consigne_position.copy() #consigne en xyz, theta xyz
    erreur_R_atr = cons-mes
    M=chgt_base_atr_dir(lacet=mes[config.HEADING_INDEX],roulis=mes[config.ROLL_INDEX],tangage=mes[config.PITCH_INDEX])
    erreur_R_dir = M.dot(erreur_R_atr)
    #efforts = asservir_commande(erreur_R_dir,matrice_etats)
    #efforts=config.Kp*erreur_R_dir
    
    efforts = np.array([0 for i in range(config.NB_AXES)])
    efforts[config.Z_INDEX] = MyPID.compute(erreur_R_atr[config.Z_INDEX])
    efforts_sat = np.array([min(max(efforts[i],config.Saturation_Efforts[i]["min"]),config.Saturation_Efforts[i]["max"]) for i in range(config.NB_AXES)])
    file = open("efforts.txt","w")
    file.write("consignes z : "+str(cons[config.Z_INDEX])+" mesures z : "+str(mes[config.Z_INDEX])+" efforts z : "+str(efforts_sat))
    cine_vol.cmd_forces(efforts_sat)

    asservissements_dict["CONSIGNES_POSITIONS"] = cons
    asservissements_dict["ERREURS"] = erreur_R_dir
    asservissements_dict["COMMANDES_FORCES"] = efforts_sat

    return asservissements_dict

# todo : add mutex for this function so that it cannot be called at the same time from update_etat_loop and from TUI_main_loop
def update_matrice_etats(matrice_etats, current_time, measures_array, asservissements_dict):
    # Mise à jour du tableau 2D
    matrice_etats[:,:-1]  = matrice_etats[:,1:]
    
    matrice_etats[config.TIME_INDEX*config.NB_AXES,-1]                                                                    = current_time
    matrice_etats[config.MESURES_INDEX*config.NB_AXES:(config.MESURES_INDEX+1)*config.NB_AXES,-1]                         = measures_array.copy()
    matrice_etats[config.CONSIGNES_POSITIONS_INDEX*config.NB_AXES:(config.CONSIGNES_POSITIONS_INDEX+1)*config.NB_AXES,-1] = asservissements_dict["CONSIGNES_POSITIONS"].copy()
    matrice_etats[config.ERREURS_INDEX*config.NB_AXES:(config.ERREURS_INDEX+1)*config.NB_AXES,-1]                         = asservissements_dict["ERREURS"].copy()
    matrice_etats[config.COMMANDES_FORCES_INDEX*config.NB_AXES:(config.COMMANDES_FORCES_INDEX+1)*config.NB_AXES,-1]       = asservissements_dict["COMMANDES_FORCES"].copy()

def create_null_asserv_dict():
    none_array = np.array([None for i in range(config.NB_AXES)])
    asservissements_dict = {"CONSIGNES": none_array, "ERREURS": none_array, "COMMANDES": none_array}    
    return asservissements_dict

def update_etat_loop(autorise_asservissement, MyMergeMeas, matrice_etats):
    
    i=0
    MyPID_z = PID.PID(P=60,ITs=0.184,D=120,N=4.07,Ts=0.112)
    while True:
        current_time = time.time()
        measures_array = MyMergeMeas.update_measures(current_time)

        file = open("autorise.txt","w")
        file.write("autorise z : ")
        
        # asservissement de tout
        if autorise_asservissement==True:
            
            asservissements_dict = asservir_tout(MyPID_z,measures_array,config.Consignes_Positions[:,i],matrice_etats)
        else:
            asservissements_dict = create_null_asserv_dict()
        update_matrice_etats(matrice_etats,current_time,measures_array,asservissements_dict)
        i=(i+1)%config.NB_ECHANTILLONS


if __name__ == "__main__":
    autorise_asservissement = True
    MyMergeMeas = merge_meas.MyMergeMeas()
    matrice_etats = np.zeros((config.NB_AXES*config.NB_ELEMENTS_MATRICE_ETAT,config.NB_ECHANTILLONS))
    update_etat_loop(autorise_asservissement,MyMergeMeas,matrice_etats)
