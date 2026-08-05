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

        self.x = 0.0
        self.y = 0.0
        self.lacet = 0.0


        fc = 0.5
        self.filtre_x = filtre.PasseBas_ordre_1(fc)
        self.filtre_y = filtre.PasseBas_ordre_1(fc)


        self.running = False
        self.old_t = 0
        self.thread = threading.Thread(target=self.localiser_loop)

        self.old_x = 0
        self.old_y = 0

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

            v_mes = ((self.old_x - x)**2 + (self.old_y - y)**2)**0.5/dt
            self.old_x, self.old_y = x, y

            #if v_mes > self.v_max:
            #    continue


            self.x = self.filtre_x.filtre1(x, dt)
            self.y = self.filtre_y.filtre1(y, dt)
            self.lacet = lacet

            self.new_data = True


