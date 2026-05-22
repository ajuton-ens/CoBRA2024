from math import *
from XY4 import Localisation
import threading
import filtres_2025 as filtre
import time


# (x0, y0) : base dans le referentiel des tags
# (x1, y1) : base dans le referentiel du Cobra


class LocalisationRuning(Localisation):
    def __init__(self, ListePoints, v_max):
        
        self.v_max = v_max

        for i in ListePoints.keys():
            ListePoints[i]=(ListePoints[i][1],ListePoints[i][0],ListePoints[i][2])

        super().__init__(ListePoints)

        self.x0 = 0.0
        self.y0 = 0.0
        self.lacet = 0.0


        fc = 0.5
        self.filtre_x = filtre.PasseBas_ordre_1(fc)
        self.filtre_y = filtre.PasseBas_ordre_1(fc)


        self.running = False
        self.old_t = 0
        self.thread = threading.Thread(target=self.localiser_loop)

        self.old_x0 = 0
        self.old_y0 = 0

        self.new_data = False


    def Start(self):
        self.thread = threading.Thread(target=self.localiser_loop)
        self.running = True
        self.old_t = time.time()
        self.thread.start()

    def Stop(self):
        self.running = False
        self.thread.join()


    def localiser_loop(self):
        while self.running:

            t = time.time()
            dt = t - self.old_t
            self.old_t = t


            try:
                pos = self.mesure()
            except :
                print("erreur mesure camera")
                pos = None

            if pos is None:
                continue
            
            x, y, lacet = pos

            v_mes = ((self.old_x0 - x)**2 + (self.old_y0 - y)**2)**0.5/dt
            self.old_x0, self.old_y0 = x, y

            if v_mes > self.v_max:
                continue


            self.x0 = self.filtre_x.filtre1(x, dt)
            self.y0 = self.filtre_y.filtre1(y, dt)
            self.lacet = lacet

            self.new_data = True




    def Rtags_to_Rcobra(self, X0, Y0):
        X1 = (X0 - self.x0) * cos(self.lacet * pi/180) + (Y0 - self.y0) * sin(self.lacet * pi/180)
        Y1 = (Y0 - self.y0) * cos(self.lacet * pi/180) - (X0 - self.x0) * sin(self.lacet * pi/180)
        return (X1, Y1)


