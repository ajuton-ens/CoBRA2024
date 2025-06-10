import cv2
from picamera2 import Picamera2
from pyapriltags import Detector
import numpy as np
import smbus 
import math

class Tag :
    def __init__(self):
        self.picam2 = Picamera2()
        
        self.WIDTH = 1536
        self.HEIGH = 864
        self.picam2.configure(self.picam2.create_preview_configuration({'size':(self.WIDTH,self.HEIGH)}))
        self.picam2.start()

        self.at_detector = Detector(families="tag36h11",nthreads=1,quad_sigma=0.0,refine_edges=1,\
decode_sharpening=0.25,debug=0)

        #coefficients de distorsion de la camera

        self.mtx = np.array([[ 977.08159964 	,  0.00000000e+00,  789.18761132],[ 0.00000000e+00,  977.14004212, 434.47165678],[ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])
        self.dist = np.array([[-0.02727091,  0.1312434,   0.00479796,  0.00269239, -1.30723302]])
        self.fx = self.mtx[0][0]
        self.cx = self.mtx[0][2]
        self.fy = self.mtx[1][1]
        self.cy = self.mtx[1][2]
        
        #Positions des tags dans l'environnement
        
        self.listePoints3D = {6:(0,0,0)}
        self.matrice=np.array([[-1,0,0],[0,1,0],[0,0,1]])

    def Detection_Tags(self):
        img=cv2.cvtColor(self.picam2.capture_array(),cv2.COLOR_BGR2GRAY) #prise d'une photo puis correction
        img_undistorded = cv2.undistort(img, self.mtx, self.dist, None, newCameraMatrix=self.mtx)
        #indication de la taille des tags, lancement de la detection
        tags=self.at_detector.detect(img_undistorded,estimate_tag_pose=True,camera_params=[self.fx,self.fy,self.cx,self.cy],tag_size=0.172) 
        return tags

    def calculAngles(self,R):
        sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
        singular = sy < 1e-6
        if not singular:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0
        return np.degrees(np.array([x, y, z]))



    def localisation(self):
        """Renvoie:
            (x, y, z, alpha)
            - La position de la caméra (x, y, z) dans le repère du sol
            - L'angle de lacet (c'est le seul qui nous interesse dans le cas d'un dirigeable
            """
    
        tags=self.Detection_Tags()
    
        positions=[]
        angles=[]
        
        positionMoyenne=np.array([0,0,0],dtype='float64')
        angleMoyen=np.array([0,0,0],dtype='float64')
    
        for tag in tags:
        
            angles.append(np.array(self.calculAngles(tag.pose_R)))
        
            pose=np.dot(np.transpose(tag.pose_R),tag.pose_t)
       
            try :
                positions.append(np.dot(self.matrice,np.transpose(pose)[0])+np.array(self.listePoints3D[tag.tag_id])) 
            except : 
                print("Tag inconnu")
         
            for position in positions:
                positionMoyenne += position
            for angle in angles:
                angleMoyen += angle
    
        n=len(positions)
        if n!=0:
            positionMoyenne=positionMoyenne/n
            angleMoyen=angleMoyen/n

            #            X                    Y                     Z              Lacet
            return(positionMoyenne[0], positionMoyenne[1], positionMoyenne[2], angleMoyen[2]) 

tag=Tag()

class LidarTFLuna: # pour lire la distance mesurée par le LiDAR TF Luna en utilisant le protocole I2C
    def __init__(self, i2c_address=0x10, i2c_bus=1):
        # Initialiser le bus I2C
        self.address = i2c_address
        self.bus = smbus.SMBus(i2c_bus)
    
    def read_distance(self):
        # Le TF Luna envoie les données de distance en 2 octets
        try:
            # Lire les 2 bytes (octets) de données de distance
            distance_data = self.bus.read_i2c_block_data(self.address, 0x00, 2)  #arguments: adresse unique du périphérique, adresse du premier registre à lire,  nbre de bytes à lire
            # Combiner les 2 octets en une seule valeur de distance en cm
            distance = (distance_data[0] + (distance_data[1] << 8))
            return distance
        except Exception as e:
            print(f"Erreur de lecture du LiDAR TF Luna : {e}")
            return None

lidar = LidarTFLuna()

class PID:
    def __init__(self, Kp, Ki, Kd, consigne):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.consigne = consigne

        self.previous_error = 0
        self.integral = 0

    def compute(self, measured_value):
        
        
        """Calcule la sortie PID en fonction de la valeur mesurée"""
        error = self.consigne - measured_value

        # Terme proportionnel
        P = self.Kp * error

        # Terme intégral
        self.integral += error
        I = self.Ki * self.integral

        # Terme dérivé
        D = self.Kd * (error - self.previous_error)
        self.previous_error = error

        R=P+I+D

        # Sortie PID (limitée entre 0 et 100 pour la vitesse du moteur)
        output = max(min(R, 50), 10)
        return output
    
    def compute2(self, measured_value):
        
        
        """Calcule la sortie PID en fonction de la valeur mesurée"""
        error = self.consigne - measured_value
        if error > 180:
            error -= 360
        elif error < -180:
            error += 360  

        # Terme proportionnel
        P = self.Kp * error

        # Terme intégral
        self.integral += error
        self.integral = max(min(self.integral, 100), -100)
        I = self.Ki * self.integral

        # Terme dérivé
        D = self.Kd * (error - self.previous_error)
        self.previous_error = error

        R=P+D
        print (R)
        # Sortie PID (limitée entre -50,-20 et 20,50 pour la vitesse du moteur)
        if R<0 : 
            output = min(max(R, -50), -20)
        else :
            output = max(min(R, 50), 20)
        return output
    
    def compute3(self, error):
               
        """Calcule la sortie PID en fonction de l'erreur mesurée"""

        # Terme proportionnel
        P = self.Kp * error

        # Terme intégral
        self.integral += error
        self.integral = max(min(self.integral, 100), -100)
        I = self.Ki * self.integral

        # Terme dérivé
        D = self.Kd * (error - self.previous_error)
        self.previous_error = error

        R=P+D

        # Sortie PID (limitée entre 0 et 100 pour la vitesse du moteur)
        if R>0 : 
            output = max(min(R, 50), 20)
        else : 
            output=min(max(R,50),20)
        return output

# Asservissement en hauteur init :
    
consigneh = int(input("donner consigne hauteur:"))
pidh = PID(0.5,0.1,0.05,consigneh)

xc = int(input("donner abcisse consigne:"))
yc = int(input("donner ordonée consigne:"))

tag=Tag()

x0=tag.localisation()[0]
y0=tag.localisation()[1]
a0=tag.localisation()[3]

angleradc=math.atan2(yc/xc)
angledegc=math.degrees(angleradc)

pid = PID(0.5,0.1,0.05,angledegc)


while True : 
    # PARTIE HAUTEUR 
    distanceh = lidar.read_distance()
    # print(f"La distance mesurée par le télémètre infrarouge est: {distance}cm")   
    vitesseh=pidh.compute(distanceh)
    mot_brushless.commande(vitesseh,0)
    # PARTIE XY 
    
    x=tag.localisation()[0]
    y=tag.localisation()[1]
    angle=tag.localisation()[3]
    
    dx=xc-x
    dy=yc-y
    anglerad=math.atan2(dy/dx)
    angledeg=math.degrees(anglerad)
    vitesse=pid.compute2(angledeg)
    mot_brushless.commande(vitesse,0)
    
    distance=math.sqrt(dx**2+dy**2)
    
    if abs(angledeg-angledegc) < 5 :
        vitesse2=pid.compute3(distance)
        mot_brushless.commande(vitesse2,0)
        
