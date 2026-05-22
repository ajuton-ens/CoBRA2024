import time
import tf_luna   # lidar
from math import *
from PID import *
from centrale_inirtielle import *
from serveur import *
import localisation_2026
import listes_points
import deplacement
from position_cam_fix import PosCamFix


myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C


dep = deplacement.Deplacement(myi2cbus)
lidar = tf_luna.LidarTFLuna(myi2cbus)
loc = localisation_2026.LocalisationRuning(listes_points.liste_atrium, 5)

etat = -1
list_pos_cons = [(1, 1, 1), (5, 1, 2), (1, 5, 3)]

dt_etat = 0

serveur = Serveur(donnee, mes_donnee)
serveur.start()


PID_alt = PID(40, 0, 400, 40, 50, 0.05)
PID_lacet = PID(1, 0, 5, 40, 50, 0.1)

PID_x = PID(15, 0.0, 0, 20, 50, 1)
PID_y = PID(15, 0.0, 0, 20, 50, 1)

PID_alt.etat = False
PID_lacet.etat = False
PID_x.etat = False
PID_y.etat = False


stab_time = 5

lacet_consigne = 0

donnee["amp"] = 30
donnee["alt"] = PID_alt.consigne
donnee["angle"] = lacet_consigne
donnee["x"] = PID_x.consigne
donnee["y"] = PID_y.consigne
donnee["PID_alt"] = PID_alt.sendPIDJson()
donnee["PID_angle"] = PID_lacet.sendPIDJson()
donnee["PID_pos"] = PID_x.sendPIDJson()


loc_cam_fix = PosCamFix()
loc_cam_fix.start()



loc.Start()
i = 0
old_t = time.time()
runing = True
try:
    while runing:
        t = time.time()
        dt = t - old_t
        old_t = t

        if serveur.new_data:
            serveur.new_data = False
            PID_alt.consigne = donnee["alt"]
            lacet_consigne = donnee["angle"]
            
            PID_alt.loadPIDJson(donnee["PID_alt"])
            PID_lacet.loadPIDJson(donnee["PID_angle"])
            PID_x.loadPIDJson(donnee["PID_pos"])
            PID_y.loadPIDJson(donnee["PID_pos"])
            print(serveur.new_data_type)
            

            if donnee["etas_pos"]:
                etat = 0
            else:
                etat = -1
                PID_alt.etat = donnee["etas_alt"]
                PID_lacet.etat = donnee["etas_angle"]
                PID_x.etat = False
                PID_y.etat = False
                

            if "x" in serveur.new_data_type and "y" in serveur.new_data_type:
                list_pos_cons.append((donnee["x"], donnee["y"], donnee["alt"]))

            serveur.new_data_type = []

        
        if loc.new_data or True:
            loc.new_data = False

            tangage, roulis, lacet_ = Centrale.read_euler()

            lacet = (360 - loc.lacet - 90) % 360


            d = lidar.mesure_distance()
            alt = d*cos(tangage*pi/180)*cos(roulis*pi/180)



            relative_lacet = (lacet - (lacet_consigne % 360) + 180) % 360 - 180


            purcent_lacet = PID_lacet.update(relative_lacet, dt)
            purcent_alt = PID_alt.update(alt, dt)

            if len(list_pos_cons) > 0:
                x1, y1 = loc.Rtags_to_Rcobra(list_pos_cons[0][0], list_pos_cons[0][1])
                purcent_x = PID_x.update(x1, dt)
                purcent_y = PID_y.update(y1, dt)


            if donnee["c"] == "0":
                dep.setAltitude(purcent_alt + donnee["offset_alt"] * PID_alt.etat)
                dep.setAngle(-purcent_lacet)
                dep.setX(-purcent_x)
                dep.setY(purcent_y)


            mes_donnee["alt"] = alt
            mes_donnee["angle"] = relative_lacet

            mes_donnee["alt_cons"] = PID_alt.consigne
            mes_donnee["angle_cons"] = lacet_consigne % 360

            mes_donnee["alt_force"] = purcent_alt
            mes_donnee["angle_force"] = purcent_lacet
            
            mes_donnee["x"] = loc.x0
            mes_donnee["y"] = loc.y0
            mes_donnee["x_fix"] = loc_cam_fix.x0
            mes_donnee["y_fix"] = loc_cam_fix.y0
            mes_donnee["angle_fix"] = loc_cam_fix.theta
            serveur.new_donnee = True

            erreur = ((loc.x0 - loc_cam_fix.x0)**2 + (loc.y0 - loc_cam_fix.y0)**2)**0.5

            i += 1
            if (i % 50) == 0 and len(list_pos_cons) > 0:
                print(f"i:{i}\t erreur:{round(erreur, 3)}\t etat: {etat}\tx0: {loc.x0:.2f}\ty0: {loc.y0:.2f}\tlacet: {lacet:.2f} \tlacet_cons: {lacet_consigne:.2f}\trelative_lacet: {relative_lacet:.2f}\tx1: {x1:.2f}\ty1: {y1:.2f}")




        match etat:
            case 0:
                if len(list_pos_cons) > 0:
                    etat = 1

                    PID_x.etat = False
                    PID_y.etat = False


                    PID_alt.consigne = list_pos_cons[0][2]
                    PID_alt.etat = True
                    dt_etat = time.time()

            case 1:
                
                if abs(alt-PID_alt.consigne) < 0.1:             # si la consigne en altutide est respectee
                    if dt_etat + stab_time < time.time():
                        etat = 2

                        Dx = list_pos_cons[0][0] - loc.x0
                        Dy = list_pos_cons[0][1] - loc.y0

                        lacet_consigne = (atan2(Dy, Dx) * 180/pi) % 360

                        del list_pos_cons[0]
                        
                        PID_lacet.etat = True
                        dt_etat = time.time()
                else:
                    dt_etat = time.time()
            case 2:
                
                if abs(relative_lacet) < 20:                # si la consigne en angle est respectee
                    if dt_etat + stab_time < time.time():
                        etat = 3
                        PID_x.etat = True
                        PID_y.etat = True
                        dt_etat = time.time()
                else:
                    dt_etat = time.time()
            
            case 3:
                x1, y1 = loc.Rtags_to_Rcobra(list_pos_cons[0][0], list_pos_cons[0][1])
                if (x1**2 + y1**2)**0.5 < 1:
                    
                    if dt_etat + stab_time < time.time():                    # si les consignes en position sont respectes
                        if len(list_pos_cons) > 0:
                            etat = 0
                        else:
                            etat = 4
        
                else:
                    dt_etat = time.time()
                    
            case 4:
                if len(list_pos_cons) > 0:
                    etat = 0


            case -1:
                pass


        if donnee["c"]:
            amp = donnee["amp"]

            match donnee["c"]:

                case "z":
                    dep.setX(amp)
                
                case "s":
                    dep.setX(-amp)
                
                case "q":
                    dep.setY(-amp)
                
                case "d":
                    dep.setY(amp)
                
                case "a":
                    dep.setAngle(-amp)
                
                case "e":
                    dep.setAngle(amp)
                
                case "Shift_L":
                    dep.setAltitude(amp)

                
                case "Control_L":
                    dep.setAltitude(-amp)
                    
                case "r":
                    dep.zeros()

            
        

except KeyboardInterrupt:
    dep.zeros()
    loc.Stop()
    serveur.Stop()
    print("FIN programme")