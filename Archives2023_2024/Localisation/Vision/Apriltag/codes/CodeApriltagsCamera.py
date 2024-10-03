import cv2
from picamera2 import Picamera2
import time
from dt_apriltags import Detector
import numpy as np

picam2 = Picamera2()
HEIGH,WIDTH=1232,1640
picam2.configure(picam2.create_preview_configuration({'size':(WIDTH,HEIGH)}))
picam2.start()

t0=time.time()
Lfps=[]

at_detector = Detector(families="tag36h11",nthreads=1,quad_sigma=0.0,refine_edges=1,decode_sharpening=0.25,debug=0)

fx=1242.8
fy=1242.6
cx=810.4
cy=664.04
dist=np.array([0.007343,1.236,-0.001877,0.0068044]) #coefficients de distorsion de la camera
camera_matrice=np.array([[fx,0,cx],[0,fy,cy],[0,0,1]]) #matrice de la camera



#Liste_points_3D = {0:(0.0,2.0,0.0),1:(0.0,0.0,0.0),2:(2.0,2.0,0.0),3:(2.0,0.0,0.0),6:(1.0,0.0,0.0),5:(1.0,1.0,0.0),4:(0.0,1.0,0.0),22:(1.0,1.0,0.74)}
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Liste_points_3D = {0:(0.0,0.0,0.0),8:(0.0,3.0,0.0),30:(0.0,6.0,0.0),31:(0.0,9.0,0.0),32:(0.0,12.0,0.0),33:(0.0,15.0,0.0),34:(0.0,18.0,0.0),15:(3.0,0.0,0.0),9:(3.0,3.0,0.0),10:(3.0,6.0,0.0),11:(3.0,9.0,0.0),12:(3.0,12.0,0.0),13:(3.0,15.0,0.0),14:(3.0,18.0,0.0),16:(6.0,0.0,0.0),17:(6.0,3.0,0.0),18:(6.0,6.0,0.0),19:(6.0,9.0,0.0),20:(6.0,12.0,0.0),51:(6.0,15.0,0.0),35:(6.0,18.0,0.0)}

#position petits tags (test)
#Liste_points_3D = {9:(0,0,0),10:(0.1165,0,0),11:(0.233,0,0),6:(0,0.105,0),7:(0.1165,0.105,0),8:(0.233,0.105,0),3:(0,0.21,0),4:(0.1165,0.21,0),5:(0.233,0.21,0),0:(0,0.315,0),1:(0.1165,0.315,0),2:(0.233,0.315,0)}

def capture():
    img=cv2.cvtColor(picam2.capture_array(),cv2.COLOR_BGR2GRAY) #prise d'une photo
    tag=at_detector.detect(img, estimate_tag_pose=True, camera_params=[fx,fy,cx,cy], tag_size=0.173) #tag_size=0.052
    return tag


def angle(R):
    
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



matrice=np.array([[-1,0,0],[0,1,0],[0,0,1]])
while True:
    tag=capture()
    Positions=[]
    PositionsD={}
    PositionMoyenne=np.array([0,0,0],dtype='float64')
    
    
    for i in tag:
         #print(angle(i.pose_R))
         pose=np.dot(np.transpose(i.pose_R),i.pose_t)
         Positions.append(np.dot(matrice,np.transpose(pose)[0])+np.array(Liste_points_3D[i.tag_id])) #formule pour trouver la position  partir du resultat apriltag
         #PositionsD[i.tag_id]=np.dot(matrice,np.transpose(pose)[0])+np.array(Liste_points_3D[i.tag_id])
         
    for e in Positions:
        #PositionMoyenne[0]+=e[0]
        #PositionMoyenne[1]+=e[1]
        #PositionMoyenne[2]+=e[2]
        PositionMoyenne+=e
    n=len(Positions)
    
    if n!=0:
        PositionMoyenne=PositionMoyenne/n
        PositionMoyenne[2]+=0.05
        print(PositionMoyenne,n)
    
    #t1=time.time()
    #Lfps.append(1/(t1-t0))
    #print(str(sum(Lfps[-50:])/50)+" FPS")
    #t0=t1