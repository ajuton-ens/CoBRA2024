import time
from math import *
import tf_luna   # lidar
from centrale_inirtielle import *
import localisation_2026
import listes_points
from position_cam_fix import PosCamFix
import filtres_2025 as filtre


def mediane(liste):
    s = sorted(liste)
    n = len(s)
    if n == 0:
        raise ValueError("liste vide")
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


class FusionsCapteurs:
    def __init__(self, myi2cbus):
        self.lidar = tf_luna.LidarTFLuna(myi2cbus)

        self.v_max = 10

        self.loc_cam_int = localisation_2026.LocalisationRuning(listes_points.liste_course, self.v_max)
        self.loc_cam_ext = PosCamFix()

        #self.IMU = BNO055(myi2cbus)

        self.loc_cam_int.Start()
        self.loc_cam_ext.start()

        self.x = 0
        self.y = 0
        self.z = 0
        self.lacet = 0

        self.old_z_lidar = 0


        self.distance_filter = filtre.PasseBas_ordre_1(4)



    def update(self, dt):


        tangage_IMU, roulis_IMU, lacet_IMU = (0,0, 0)  #self.IMU.read_euler()

        d = self.lidar.mesure_distance()
        z_lidar_ = d*cos(tangage_IMU*pi/180)*cos(roulis_IMU*pi/180)

        z_lidar = self.distance_filter.filtre1(z_lidar_, dt)

        lacet_cam_int = (360 - self.loc_cam_int.lacet - 90) % 360
        
        v_z = (z_lidar - self.old_z_lidar)/dt
        if abs(v_z) <= self.v_max:
            self.old_z_lidar = z_lidar



        self.z = z_lidar


        self.x = self.loc_cam_int.x
        self.y = self.loc_cam_int.y
        
        self.lacet = lacet_cam_int


    def Stop(self):
        self.loc_cam_int.Stop()
        self.loc_cam_ext.Stop()

    def RepTags_to_RepCobra(self, X0, Y0):
        X1 = (X0 - self.x) * cos(self.lacet * pi/180) + (Y0 - self.y) * sin(self.lacet * pi/180)
        Y1 = (Y0 - self.y) * cos(self.lacet * pi/180) - (X0 - self.x) * sin(self.lacet * pi/180)
        return (X1, Y1)
    

    def relative_lacet(self, lacet_consigne):
        return (self.lacet - (lacet_consigne % 360) + 180) % 360 - 180

