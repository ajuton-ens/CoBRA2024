from gpiozero import LED
import time

class PCA9685: #pour commander les sorties pwm
    def __init__(self, bus, address_PCA9685=0x40):
        # DÉFINITION des registres (valeurs initiales)
        self.address_PCA9685 = address_PCA9685
        self.bus=bus
        self.MODE1 = 0x00  # self.REGISTRE = adresse_registre
        self.MODE2 = 0x01

        # liste de dictionnaires. Chaque dictionnaire definit les registres d'une sortie PWM de la PCA9685
        self.PWMs = [{"ON_L": 0x06, "ON_H": 0x07, "OFF_L": 0x08, "OFF_H": 0x09},
                     {"ON_L": 0x0A, "ON_H": 0x0B, "OFF_L": 0x0C, "OFF_H": 0x0D},
                     {"ON_L": 0x0E, "ON_H": 0x0F, "OFF_L": 0x10, "OFF_H": 0x11},
                     {"ON_L": 0x12, "ON_H": 0x13, "OFF_L": 0x14, "OFF_H": 0x15},
                     {"ON_L": 0x16, "ON_H": 0x17, "OFF_L": 0x18, "OFF_H": 0x19},
                     {"ON_L": 0x1A, "ON_H": 0x1B, "OFF_L": 0x1C, "OFF_H": 0x1D},
                     {"ON_L": 0x1E, "ON_H": 0x1F, "OFF_L": 0x20, "OFF_H": 0x21},
                     {"ON_L": 0x22, "ON_H": 0x23, "OFF_L": 0x24, "OFF_H": 0x25},
                     {"ON_L": 0x26, "ON_H": 0x27, "OFF_L": 0x28, "OFF_H": 0x29},
                     {"ON_L": 0x2A, "ON_H": 0x2B, "OFF_L": 0x2C, "OFF_H": 0x2D},
                     {"ON_L": 0x2E, "ON_H": 0x2F, "OFF_L": 0x30, "OFF_H": 0x31},
                     {"ON_L": 0x32, "ON_H": 0x33, "OFF_L": 0x34, "OFF_H": 0x35}
                    #  {"ON_L": 0x36, "ON_H": 0x37, "OFF_L": 0x38, "OFF_H": 0x39},
                    #  {"ON_L": 0x3A, "ON_H": 0x3B, "OFF_L": 0x3C, "OFF_H": 0x3D},
                    #  {"ON_L": 0x3E, "ON_H": 0x3F, "OFF_L": 0x40, "OFF_H": 0x41}
                    #  {"ON_L": 0x42, "ON_H": 0x43, "OFF_L": 0x44, "OFF_H": 0x45},
                    #  {"ON_L": 0x46, "ON_H": 0x47, "OFF_L": 0x48, "OFF_H": 0x49}
        ]

        self.PRE_SCALE = 0xFE # Numero du registre qui code la periode
        self.freqPWM_Hz = 50 # Frequence des PWM à 50Hz
        self.periodPWM = 1/self.freqPWM_Hz # Période à 20 millisecondes
        #Valeur théorique (avec formule datasheet) qui ne fonctionne pas à cause de l'imprécision de la clock 
            #self.PCA9685_PRE_SCALE_VALUE = (round(25*10**6/(4096*self.freqPWM_Hz)-1))  # configure la fréquence de la PWM sur tous les canaux
        #Valeur réelle fonctionnelle (+1)
        self.PCA9685_PRE_SCALE_VALUE = 123  # configure la fréquence de la PWM sur tous les canaux
        
        print("PRESCALE : ",self.PCA9685_PRE_SCALE_VALUE)

        # CONFIGURATION des registres du PCA9685
        # write_byte_data prend trois arguments: l'adresse de l'appareil i2C, le nom de registre où on veut écrire, les données à écrire (byte/octet en hexadécimal)
        self.bus.write_byte_data(self.address_PCA9685,self.MODE1,0x10) # 
        self.bus.write_byte_data(self.address_PCA9685,self.PRE_SCALE,self.PCA9685_PRE_SCALE_VALUE) # 25MHz/(4096*freqPWM_Hz)-1 # attention, 25MHz pas precis
        
        self.bus.write_byte_data(self.address_PCA9685,self.MODE1,0x20)
        
        # 

   
        self.bus.write_byte_data(self.address_PCA9685,self.MODE2,0x04) 

        # Intervalles d’allumage et d’extinction (largeur d'impulsion) pour chaque PWM de self.PWMs.
        for PWM in self.PWMs: 
            #self.bus.write_byte_data(self.address_PCA9685, PWM["ON_L"], 0)     
            # self.bus.write_byte_data(self.address_PCA9685, PWM["ON_H"], 0x0)   
            # self.bus.write_byte_data(self.address_PCA9685, PWM["OFF_L"], 0x40) #0x153 pour ancien variateur
            # self.bus.write_byte_data(self.address_PCA9685, PWM["OFF_H"], 1) #0x1
        
            self.bus.write_i2c_block_data(self.address_PCA9685, PWM["ON_L"], [0,0x0,0x40,1])
        

    def commande_moteur_vitesse_us(self, temps_off_us, num_PWM):
        # On se base sur les points physiques qui ont fait tourner le moteur :
        # 1000 us = 205 points | 2000 us = 410 points
        # Formule de correspondance directe et linéaire :
        points_off = 205 + ((temps_off_us - 1000) * (410 - 205) / (2000 - 1000))
        
        # Sécurité 12-bits
        points_off = int(min(max(points_off, 0), 4095)) 
        
        temps_H = points_off // 256
        temps_L = points_off % 256
        self.bus.write_i2c_block_data(self.address_PCA9685, self.PWMs[num_PWM]["OFF_L"], [temps_L, temps_H])

    def commande_2_moteurs_vitesse_pourcent(self, temps_off_us1, temps_off_us2, num_PWM1): # ne marche que pour des moteurs dont les numéros de registres se SUIVENT !!
        points_off = temps_off_us1*4095/(self.periodPWM*1e6)
        temps_H1 = points_off//256
        temps_L1 = points_off%256
        points_off = temps_off_us2*4095/(self.periodPWM*1e6)
        temps_H2 = points_off//256
        temps_L2 = points_off%256
        self.bus.write_i2c_block_data(self.address_PCA9685,self.PWMs[num_PWM1]["OFF_L"], [int(temps_L1),int(temps_H1),0,0,int(temps_L2),int(temps_H2)])
        
class brushless:
    def __init__(self, PCA9685, num_moteur):
        self.num_moteur = num_moteur
        self.myPCA9685 = PCA9685
        
        # Le point mort (0% de vitesse) est bien à 1500 us (milieu)
        self.valeur_repos_us = 1500  
        self.zoneMorteP = 10.5 
        self.zoneMorteN = 4.5 

        # --- SÉQUENCE D'ARMEMENT SPÉCIFIQUE ESC 4D ---
        print(f"Moteur {num_moteur} [ESC 4D] : Étape 1 - Envoi du minimum (1000 us)...")
        self.myPCA9685.commande_moteur_vitesse_us(1000, self.num_moteur)
        time.sleep(2.0)  # Premier bip d'initialisation
        
        print(f"Moteur {num_moteur} [ESC 4D] : Étape 2 - Passage au Point Mort (1500 us)...")
        self.myPCA9685.commande_moteur_vitesse_us(1500, self.num_moteur)
        time.sleep(2.0)  # Bip de confirmation de zone neutre
        
        print(f"Moteur {num_moteur} prêt pour la marche avant et arrière !")
        
        # Initialisation finale à 0% (1500 us)
        self.cmd_vit_pourcent(0) 

    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent < -100: vitesse_pourcent = -100
        if vitesse_pourcent > 100:  vitesse_pourcent = 100
        
        # Gestion de tes zones mortes d'origine
        if 0 < vitesse_pourcent :
            vitesse_pourcent = self.zoneMorteP + vitesse_pourcent 
        if 0 > vitesse_pourcent :
            vitesse_pourcent = -self.zoneMorteN + vitesse_pourcent   
        
        # Calcul de la commande :
        # -100% -> 1500 + (-100 * 5) = 1000 us (Marche arrière max)
        #    0% -> 1500 + (0 * 5)    = 1500 us (Point mort / Arrêt)
        #  100% -> 1500 + (100 * 5)  = 2000 us (Marche avant max)
        temps_etat_haut_us = self.valeur_repos_us + (vitesse_pourcent * 5)
        
        self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us, self.num_moteur)
    def cmd_vit_pourcent_2_moteurs(self, vitesse_pourcent1, vitesse_pourcent2):
        if vitesse_pourcent1 < -100:
            vitesse_pourcent1 = -100
        if vitesse_pourcent1 > 100:
            vitesse_pourcent1 = 100
        if vitesse_pourcent2 < -100:
            vitesse_pourcent2 = -100
        if vitesse_pourcent2 > 100:
            vitesse_pourcent2 = 100
        if 0 < vitesse_pourcent1 :
            vitesse_pourcent1 = self.zoneMorteP + vitesse_pourcent1
        if 0 > vitesse_pourcent1 :
            vitesse_pourcent1 = -self.zoneMorteN+vitesse_pourcent1
        if 0 < vitesse_pourcent2 :
            vitesse_pourcent2 = self.zoneMorteP + vitesse_pourcent2
        if 0 > vitesse_pourcent2 :
            vitesse_pourcent2 = -self.zoneMorteN+vitesse_pourcent2
        temps_etat_haut_us1 = self.valeur_repos_us + vitesse_pourcent1 * 5  # 100% correspond à +500us
        temps_etat_haut_us2 = self.valeur_repos_us + vitesse_pourcent2 * 5  # 100% correspond à +500us
        self.myPCA9685.commande_2_moteurs_vitesse_pourcent(temps_etat_haut_us1, temps_etat_haut_us2, self.num_moteur)   

# Dictionnaire des marques de servomoteurs et leurs caractéristiques
marques = { "FUTABA S3107":     {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286},
            "HITEC HS-475HB":   {"valeur_repos_us": 1.5*10**3, "angle_min": -50, "angle_max": 70, "decalage_us_max": 1.286}
            }


class MCC:
    def __init__(self,PCA9685,num_PWM_vitesse,pin_sens_AV,pin_sens_AR):
        
        self.num_PWM_vitesse = num_PWM_vitesse
        self.pin_sens_AV = LED(pin_sens_AV)
        self.pin_sens_AR = LED(pin_sens_AR)
        self.myPCA9685 = PCA9685
        self.pin_sens_AV.off()
        self.pin_sens_AR.off()
        self.valeur_repos_us = 1500 # valeur milieu de la commande en us=> pour laquelle la vitesse est nulle
        self.cmd_vit_pourcent(0)
        
    def cmd_vit_pourcent(self, vitesse_pourcent):
        if vitesse_pourcent < -100:
            vitesse_pourcent = -100
        if vitesse_pourcent > 100:
            vitesse_pourcent = 100
        if 0 < vitesse_pourcent :
            self.pin_sens_AV.off()
            self.pin_sens_AR.on()
        if 0 > vitesse_pourcent :
            self.pin_sens_AV.on()
            self.pin_sens_AR.off()
            vitesse_pourcent=-vitesse_pourcent
        if vitesse_pourcent==0 :
            self.pin_sens_AV.off()
            self.pin_sens_AR.off()
        
        temps_etat_haut_us= 50 + vitesse_pourcent*190 #100% correspond à +19ms
        self.myPCA9685.commande_moteur_vitesse_us(temps_etat_haut_us,self.num_PWM_vitesse)

 


# =====================================================================
# PROGRAMME DE TEST GLOBAL (À METTRE À LA SUITE DE VOS CLASSES)
# =====================================================================
if __name__ == "__main__":
    import smbus2

    print("=======================================================")
    print("  TEST DU CONTRÔLEUR T-HOBBY 16A F3P 3D/4D (BI-DIRECTIONNEL) ")
    print("=======================================================")
    
    # 1. Initialisation du matériel I2C
    try:
        myi2cbus = smbus2.SMBus(1) # Connexion au bus I2C n°1 de la Raspberry
        myPCA9685 = PCA9685(myi2cbus) # Configuration du PCA9685 à 50Hz
        print("[I2C] Connexion au PCA9685 réussie (Adresse 0x40).")
    except Exception as e:
        print(f"[ERREUR I2C] Impossible de parler au PCA9685 : {e}")
        print("Vérifiez que l'I2C est activé sur la Pi et que les câbles sont bien mis.")
        exit(1)

    # 2. Création et Armement automatique du moteur
    # Modifie l'index 0 si ton ESC est branché sur un autre canal du PCA9685
    NUMERO_CANAL = 0 
    print(f"\n[INITIALISATION] Création de l'objet moteur sur le canal {NUMERO_CANAL}...")
    
    # ATTENTION : Cette ligne va lancer la séquence d'armement de 4 secondes (1000us puis 1500us)
    moteur = brushless(myPCA9685, NUMERO_CANAL)
    
    print("\n[INFO] Si vous avez entendu la double série de bips, l'ESC est déverrouillé !")
    print("Repères de commande :")
    print("  ->   0 %  : Point mort (Arrêt total - 1500 us)")
    print("  ->  100 % : Marche AVANT maximum (2000 us)")
    print("  -> -100 % : Marche ARRIÈRE maximum (1000 us)")
    print("=======================================================\n")

    # 3. Boucle interactive de commande
    while True:
        try:
            # Demande de la consigne à l'utilisateur
            saisie = input("Entrez la vitesse en % (-100 à 100) ou 'q' pour quitter : ")
            
            # Option pour quitter proprement
            if saisie.lower() == 'q':
                print("\nArrêt demandé par l'utilisateur.")
                break
                
            commande_vitesse = int(saisie)
            
            if commande_vitesse < -100 or commande_vitesse > 100:
                print("⚠️ Erreur : La valeur doit être comprise entre -100 et 100.")
                continue

            # Envoi de la commande à l'ESC
            moteur.cmd_vit_pourcent(commande_vitesse)
            
            # Calcul théorique pour affichage de contrôle à l'écran
            # (Permet de vérifier visuellement si la logique du code suit)
            us_theorique = 1500 + (commande_vitesse * 5)
            print(f" -> Consigne envoyée : {commande_vitesse}% (Signal physique généré : ~{us_theorique} us)")

        except ValueError:
            print("⚠️ Entrée invalide. Veuillez saisir un nombre entier entre -100 et 100.")
        except KeyboardInterrupt:
            # Sécurité si l'utilisateur fait un Ctrl+C dans le terminal
            print("\n\n[SÉCURITÉ] Interruption détectée ! Coupure immédiate des moteurs.")
            break

    # 4. Procédure d'arrêt propre en quittant le script
    print("[STOP] Remise des gaz au point mort (0%)...")
    moteur.cmd_vit_pourcent(0)
    print("Fin du programme de test.")