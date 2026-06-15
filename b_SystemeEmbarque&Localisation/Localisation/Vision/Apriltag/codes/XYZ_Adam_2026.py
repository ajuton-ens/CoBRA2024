from turtle import position

import cv2
from picamera2 import Picamera2
from pyapriltags import Detector
import numpy as np
import time


class Localisation():
    def __init__(self, ListePoints):
        self.picam2 = Picamera2()
        WIDTH, HEIGHT = 4608, 2592
        self.picam2.configure(self.picam2.create_video_configuration(
            main={"size": (WIDTH, HEIGHT), "format": "XRGB8888"}
        ))
        self.picam2.start()

        self.at_detector = Detector(families="tag36h11", nthreads=1, quad_sigma=0.0,
                                refine_edges=1, decode_sharpening=0.25, debug=0)

        # Chargement automatique de la calibration correspondant à la résolution
        calib_file = f"/home/banane/Documents/apriltag_env/work/calibration_{WIDTH}x{HEIGHT}.npz"
        data = np.load(calib_file)
        self.mtx = data["mtx"]
        self.dist = data["dist"]
        print(f"Calibration chargée : {calib_file} (RMS = {float(data['rms']):.4f})")

        self.fx, self.fy = self.mtx[0,0], self.mtx[1,1]
        self.cx, self.cy = self.mtx[0,2], self.mtx[1,2]

        self.Liste_points_3D = ListePoints
        self.matrice = np.array([[-1,0,0],[0,1,0],[0,0,1]])


    def capture(self):
        img=cv2.cvtColor(self.picam2.capture_array(),cv2.COLOR_BGR2GRAY)
        ##img = cv2.undistort(img, mtx, dist)
        tag=self.at_detector.detect(img, estimate_tag_pose=True, camera_params=[self.fx,self.fy,self.cx,self.cy], tag_size=0.172)
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

        return np.degrees(np.array([x, y, z])) #roll (sur X), pitch (sur Y), yaw (sur Z)

    def correction_Z(self, position):
        position_copy = position.copy()           # on travaille sur une copie pour éviter d'écraser la position originale dans le cas où l'on voudrait juste relever l'erreur sans appliquer la correction
        position_copy[2] += position_copy[2]*0.05439219 + 0.03588545
        return position_copy

    def mesure(self):
        tag = self.capture()
        if not tag : 
            return None 
        
        positions_brutes = []
        angles_brutes = []
        scores = []
        id_utilises = []

        for i in tag:
            #Calcul du score individuel
            #score_indiv = max(0.001, i.decision_margin - i.pose_err)
            score_indiv = max(0.001, i.decision_margin)

            #Calcul de la position brute
            pose=np.dot(np.transpose(i.pose_R),i.pose_t) #Si on fait tR, alors on a les coordonnées du tag par rapport à la base caméra. En faisant R_transposée*t, on obtient les coordonnées de la caméra par rapport à la base du tag.
            
            #Enregistrement des données 
            positions_brutes.append(np.dot(self.matrice,np.transpose(pose)[0])+np.array(self.Liste_points_3D[i.tag_id])) #On ajoute aux coordonnées, la coordonnée du tag dans notre espace 3D.
            angles_brutes.append(self.angle(i.pose_R))
            scores.append(score_indiv)
            id_utilises.append(i.tag_id)

        #Calcul avec la moyenne simple
        position_moyenne = np.mean(positions_brutes, axis=0)
        angle_moyen = -np.mean(angles_brutes, axis=0)

        position_moyenne = self.correction_Z(position_moyenne)

        #Calcul avec la moyenne pondérée
        position_moyenne_pond = np.average(positions_brutes, axis=0, weights=scores)
        position_moyenne_pond = self.correction_Z(position_moyenne_pond)
        angle_moyen_pond = -np.average(angles_brutes, axis=0, weights=scores)

        total_score = sum(scores)
        liste_confiance = [(id_tag, round((s / total_score) * 100, 2)) for id_tag, s in zip(id_utilises, scores)]
    
    def get_pose(self):
        """
        Effectue une mesure et renvoie (X, Y, Z, roulis, tangage, lacet).
        Utilise la moyenne pondérée. Renvoie None si aucun tag détecté.
        """
        mes = self.mesure()
        if mes is None:
            return None
        _, _, pos_pond, ang_pond, _ = mes
        return (pos_pond[0], pos_pond[1], pos_pond[2],
                ang_pond[0], ang_pond[1], ang_pond[2])