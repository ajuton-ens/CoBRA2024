import cv2
from picamera2 import Picamera2
from pyapriltags import Detector
import numpy as np

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