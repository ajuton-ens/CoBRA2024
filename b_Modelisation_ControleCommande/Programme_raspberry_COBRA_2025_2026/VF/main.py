# systemctl start main.service
# systemctl stop main.service
# systemctl status main.service
# journalctl -u main.service -f

import time
from math import *
from PID import *
import smbus2
from serveur import *
from fusions_capteurs_old import FusionsCapteurs
from fusions_commandes import FusionCommandes


myi2cbus = smbus2.SMBus(1) # Initialisation du bus I2C


capteurs = FusionsCapteurs(myi2cbus)

commandes = FusionCommandes(myi2cbus)


dt_etat = 0


PID_ = {"Kp":0, "Ki":0, "Kd":0, "sample_time":0, "filtre_derivee":0, "saturation":0}
recv_donnee = {"alt":0, "angle":0, "etas_alt":0, "etas_angle":0, "etas_pos":0, "PID_alt":PID_.copy(), "PID_angle":PID_.copy(), "c":"", "offset_alt":0, "x":0, "y":0, "amp":0}
send_donnee = {"=alt":78, "=angle":0, "=alt_cons":0, "=angle_cons":0, "=alt_force":0, "=angle_force":0, "=x":1, "=y":2, "=x_fix":0, "=y_fix":0, "=angle_fix":0}
# le "=" permet de dire que c'est une donnée que peut être mis sur un graphique 


serveur = Serveur(recv_donnee, send_donnee)
serveur.start()


PID_alt = PID(50, 0, 100, 50, 0.2, 40)
PID_lacet = PID(1, 0, 3, 50, 0.2, 40)

PID_x = PID(15, 0.0, 0, 50, 1, 30)
PID_y = PID(15, 0.0, 0, 50, 1, 30)


commande_x = 0
commande_y = 0
commande_angle = 0
commande_z = 0


stab_time = 5

lacet_consigne = 0

recv_donnee["amp"] = 30
recv_donnee["alt"] = PID_alt.consigne
recv_donnee["angle"] = lacet_consigne
recv_donnee["x"] = PID_x.consigne
recv_donnee["y"] = PID_y.consigne
recv_donnee["PID_alt"] = PID_alt.getPIDJson()
recv_donnee["PID_angle"] = PID_lacet.getPIDJson()
recv_donnee["PID_pos"] = PID_x.getPIDJson()


delta_time_out = 1

time_out = delta_time_out

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
            PID_alt.consigne = recv_donnee["alt"]
            print("altitude consigne : ", PID_alt.consigne)
            lacet_consigne = recv_donnee["angle"]
            PID_x.consigne = recv_donnee["x"]
            PID_y.consigne = recv_donnee["y"]
            
            PID_alt.setPIDJson(recv_donnee["PID_alt"])
            PID_lacet.setPIDJson(recv_donnee["PID_angle"])
            PID_x.setPIDJson(recv_donnee["PID_pos"])
            PID_y.setPIDJson(recv_donnee["PID_pos"])
            print(serveur.new_data_type)
            


            PID_alt.etat = recv_donnee["etas_alt"]
            PID_lacet.etat = recv_donnee["etas_angle"]
            PID_x.etat = recv_donnee["etas_pos"]
            PID_y.etat = recv_donnee["etas_pos"]


            serveur.new_data_type = []

        capteurs.update(dt)

        relative_lacet = capteurs.relative_lacet(lacet_consigne)

        purcent_lacet = PID_lacet.update(relative_lacet, dt)
        purcent_alt = PID_alt.update(capteurs.z, dt)
        print("altitude : ", capteurs.z, " consigne : ", PID_alt.consigne, " force : ", purcent_alt)

        purcent_x = PID_x.update(capteurs.x, dt)
        purcent_y = PID_y.update(capteurs.y, dt)

        


        send_donnee["=alt"] = capteurs.z
        send_donnee["=angle"] = relative_lacet

        send_donnee["=alt_cons"] = PID_alt.consigne
        send_donnee["=angle_cons"] = lacet_consigne % 360

        send_donnee["=alt_force"] = purcent_alt
        send_donnee["=angle_force"] = purcent_lacet
        
        send_donnee["=x"] = capteurs.x
        send_donnee["=y"] = capteurs.y
        send_donnee["=x_cons"] = PID_x.consigne
        send_donnee["=y_cons"] = PID_y.consigne
        send_donnee["=x_force"] = purcent_x
        send_donnee["=y_force"] = purcent_y
        serveur.new_donnee = True
        
        
        if recv_donnee["c"]:
            amp = recv_donnee["amp"]
            commande_x = 0
            commande_y = 0
            commande_angle = 0
            commande_z = 0
            match recv_donnee["c"]:

                case "z":
                    commande_x = -amp
                
                case "s":
                    commande_x = amp
                
                case "q":
                    commande_y = amp
                
                case "d":
                    commande_y = -amp
                
                case "a":
                    commande_angle = -amp
                
                case "e":
                    commande_angle = amp
                
                case "Shift_L":
                    commande_z = amp

                
                case "Control_L":
                    commande_z = -amp
                    
                case "r":
                    commande_x = 0
                    commande_y = 0
                    commande_angle = 0
                    commande_z = 0
            time_out = delta_time_out
            recv_donnee["c"] = ""


        time_out -= dt

        if time_out <= 0:
            time_out = 0
            commande_x = 0
            commande_y = 0
            commande_angle = 0
            commande_z = 0


        commandes.setAltitude(purcent_alt + recv_donnee["offset_alt"] + commande_z)#* PID_alt.etat + commande_z)
        #print(purcent_alt + recv_donnee["offset_alt"] * PID_alt.etat + commande_z)
        commandes.setAngle(-purcent_lacet + commande_angle)
        #commandes.setX(purcent_x + commande_x) 
        #commandes.setY(purcent_y + commande_y)

except KeyboardInterrupt:
    commandes.zeros()
    capteurs.Stop()
    serveur.Stop()
    print("FIN programme")
            
    