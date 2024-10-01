import cv2
from picamera2 import Picamera2
from dt_apriltags import Detector
import numpy as np

class Localisation():
    def __init__(self,ListePoints):
        self.picam2 = Picamera2()
        HEIGH,WIDTH=1232,1640
        self.picam2.configure(self.picam2.create_preview_configuration({'size':(WIDTH,HEIGH)}))
        self.picam2.start()

        self.at_detector = Detector(families="tag36h11",nthreads=1,quad_sigma=0.0,refine_edges=1,decode_sharpening=0.25,debug=0)

        self.fx=1242.8
        self.fy=1242.6
        self.cx=810.4
        self.cy=664.04
        self.dist=np.array([0.007343,1.236,-0.001877,0.0068044]) #coefficients de distorsion de la camera

        #self.camera_matrice=np.array([[self.fx,0,self.cx],[0,self.fy,self.cy],[0,0,1]]) #matrice de la camera
        
        self.Liste_points_3D = ListePoints

        self.matrice=np.array([[-1,0,0],[0,1,0],[0,0,1]]) #définition d'une matrice pour la symétrie sur un axe


    def capture(self):
        img=cv2.cvtColor(self.picam2.capture_array(),cv2.COLOR_BGR2GRAY) #prise d'une photo
        tag=self.at_detector.detect(img, estimate_tag_pose=True, camera_params=[self.fx,self.fy,self.cx,self.cy], tag_size=0.173) #tag_size=0.052 pour les petits
        return tag
    
    def angle(self,R):
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
        


    def mesure(self):
        tag=self.capture()
        Positions=[]
        PositionMoyenne=np.array([0,0,0],dtype='float64')
        
        
        for i in tag:
            pose=np.dot(np.transpose(i.pose_R),i.pose_t)
            Positions.append(np.dot(self.matrice,np.transpose(pose)[0])+np.array(self.Liste_points_3D[i.tag_id])) #formule pour trouver la position à partir du resultat apriltag pour le i-ème tag
        for e in Positions:
            PositionMoyenne+=e
        
        n=len(Positions)
        if n!=0:
            PositionMoyenne=PositionMoyenne/n
            PositionMoyenne[2]+=0.05 #présence d'un offset sur l'axe z

            return(PositionMoyenne,n)
        else:
            return None