import cv2
from picamera2 import Picamera2
import time
from pyapriltags import Detector
import numpy as np
import os


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

        self.mtx = np.array([[ 977.08159964     ,  0.00000000e+00,  789.18761132],[ 0.00000000e+00,  977.14004212, 434.47165678],[ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00]])
        self.dist = np.array([[-0.02727091,  0.1312434,   0.00479796,  0.00269239, -1.30723302]])
        self.fx = self.mtx[0][0]
        self.cx = self.mtx[0][2]
        self.fy = self.mtx[1][1]
        self.cy = self.mtx[1][2]
        
        #Positions des tags dans l'environnement
        
        #Test à l'atruim
        self.listePoints3D = { 84: (0.0, 14.0, 0.0), 85: (1.0, 14.0, 0.0), 86: (2.0, 14.0, 0.0), 87: (3.0, 14.0, 0.0), 88: (4.0, 14.0, 0.0), 89: (5.0, 14.0, 0.0)
,78: (0.0, 13.0, 0.0), 79: (1.0, 13.0, 0.0), 80: (2.0, 13.0, 0.0), 81: (3.0, 13.0, 0.0), 82: (4.0, 13.0, 0.0), 83: (5.0, 13.0, 0.0)
,72: (0.0, 12.0, 0.0), 73: (1.0, 12.0, 0.0), 74: (2.0, 12.0, 0.0), 75: (3.0, 12.0, 0.0), 76: (4.0, 12.0, 0.0), 77: (5.0, 12.0, 0.0)
,66: (0.0, 11.0, 0.0), 67: (1.0, 11.0, 0.0), 68: (2.0, 11.0, 0.0), 69: (3.0, 11.0, 0.0), 70: (4.0, 11.0, 0.0), 71: (5.0, 11.0, 0.0)
,60: (0.0, 10.0, 0.0), 61: (1.0, 10.0, 0.0), 62: (2.0, 10.0, 0.0), 63: (3.0, 10.0, 0.0), 64: (4.0, 10.0, 0.0), 65: (5.0, 10.0, 0.0)
,54: (0.0, 9.0, 0.0), 55: (1.0, 9.0, 0.0), 56: (2.0, 9.0, 0.0), 57: (3.0, 9.0, 0.0), 58: (4.0, 9.0, 0.0), 59: (5.0, 9.0, 0.0)
,48: (0.0, 8.0, 0.0), 49: (1.0, 8.0, 0.0), 50: (2.0, 8.0, 0.0), 51: (3.0, 8.0, 0.0), 52: (4.0, 8.0, 0.0), 53: (5.0, 8.0, 0.0)
,42: (0.0, 7.0, 0.0), 43: (1.0, 7.0, 0.0), 44: (2.0, 7.0, 0.0), 45: (3.0, 7.0, 0.0), 46: (4.0, 7.0, 0.0), 47: (5.0, 7.0, 0.0)
,36: (0.0, 6.0, 0.0), 37: (1.0, 6.0, 0.0), 38: (2.0, 6.0, 0.0), 39: (3.0, 6.0, 0.0), 40: (4.0, 6.0, 0.0), 41: (5.0, 6.0, 0.0)
,30: (0.0, 5.0, 0.0), 31: (1.0, 5.0, 0.0), 32: (2.0, 5.0, 0.0), 33: (3.0, 5.0, 0.0), 34: (4.0, 5.0, 0.0), 35: (5.0, 5.0, 0.0)
,24: (0.0, 4.0, 0.0), 25: (1.0, 4.0, 0.0), 26: (2.0, 4.0, 0.0), 27: (3.0, 4.0, 0.0), 28: (4.0, 4.0, 0.0), 29: (5.0, 4.0, 0.0)
,18: (0.0, 3.0, 0.0), 19: (1.0, 3.0, 0.0), 20: (2.0, 3.0, 0.0), 21: (3.0, 3.0, 0.0), 22: (4.0, 3.0, 0.0), 23: (5.0, 3.0, 0.0)
,12: (0.0, 2.0, 0.0), 13: (1.0, 2.0, 0.0), 14: (2.0, 2.0, 0.0), 15: (3.0, 2.0, 0.0), 16: (4.0, 2.0, 0.0), 17: (5.0, 2.0, 0.0)
,6:  (0.0, 1.0, 0.0),  7: (1.0, 1.0, 0.0),  8: (2.0, 1.0, 0.0),  9: (3.0, 1.0, 0.0), 10: (4.0, 1.0, 0.0), 11: (5.0, 1.0, 0.0)
,0:  (0.0, 0.0, 0.0),  1: (1.0, 0.0, 0.0),  2: (2.0, 0.0, 0.0),  3: (3.0, 0.0, 0.0),  4: (4.0, 0.0, 0.0),  5: (5.0, 0.0, 0.0)}
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

            #            X                    Y                  
            return(positionMoyenne[0], positionMoyenne[1]) 
"""
tag = Tag()
while 1:

    print(tag.localisation())
"""
"""
picam2 = Picamera2()
WIDTH = 1536
HEIGH = 864
picam2.configure(picam2.create_preview_configuration({'size':(WIDTH,HEIGH)}))
picam2.start()
picam2.capture_file("hfh.png")
"""