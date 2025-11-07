import numpy as np
import smbus2
import time
import sensors_lib.MyBNO055 as MyBNO055
import sensors_lib.MyTFLuna as MyTFLuna
import sensors_lib.MyTag  as MyTag# Assure-toi que la classe Tag est bien définie dedans

class Fusion:
    # Indices des données
    PITCH_INDEX    = 0
    ROLL_INDEX     = 1
    HEADING_INDEX  = 2
    X_INDEX = 3
    Y_INDEX = 4
    Z_INDEX = 5

    def __init__(self):
        # Capteurs
        self.lidar = MyTFLuna.LidarTFLuna()
        self.i2cbus = smbus2.SMBus(1)
        self.bno = MyBNO055.BNO055(self.i2cbus)
        # self.bno.calibration() 
        self.tag_camera = MyTag.Tag()
        self.fusion_heading_filtered = None  # mémoire du heading corrigé
        self.alpha_heading = 0.98  # poids de confiance dans le BNO (valeur entre 0.95 et 0.99)
        # temps
        self.last_heading_correction_time = time.time()

        # Stockage des mesures
        self.measures_matrix = np.zeros((6, 0))  # Colonnes = temps
        self.current_measure = np.zeros((6, 1))

    def get_current_measures(self):
        labels = ["PITCH", "ROLL", "HEADING", "X", "Y", "Z"]
        return {labels[i]: self.current_measure[i, 0] for i in range(6)}

    def step(self, mode=False, mode2=False):
        # Lecture BNO055
        angle_euler = self.bno.read_euler()
        pitch = angle_euler["pitch"]
        roll = angle_euler["roll"]
        heading_bno = angle_euler["heading"]

        # Lecture LiDAR
        distance = self.lidar.read_distance()
        dist_z_lidar = abs(distance * np.cos(np.radians(roll)) * np.cos(np.radians(pitch)))

        # Lecture caméra et fusion
        # Lecture caméra et fusion
        try:
            x_cam, y_cam, z_cam, heading_cam = self.tag_camera.localisation()
            nb_tags = self.tag_camera.nb_tag_detect()

            if nb_tags > 0:
                print("lidar_z", dist_z_lidar)
                print("lheading_bno", heading_bno)
                print("z_cam", z_cam)
                print("heading_cam", heading_cam)

                if mode == True:
                    fusion_z = (dist_z_lidar + nb_tags * z_cam) / (1 + nb_tags)
                else:
                    fusion_z = dist_z_lidar

                current_time = time.time()
                should_correct_heading = (current_time - self.last_heading_correction_time >= 3) and (nb_tags > 0)

                if should_correct_heading:
                    fusion_heading = heading_cam
                    self.last_heading_correction_time = current_time
                    print(">>> Correction heading: BNO aligné sur caméra")
                else:
                    fusion_heading = heading_bno

            else:
                fusion_z = dist_z_lidar
                fusion_heading = heading_bno



        except Exception as e:
            print("Erreur caméra:", e)
            x_cam, y_cam, z_cam = 0.0, 0.0, dist_z_lidar
            fusion_z = dist_z_lidar
            fusion_heading = heading_bno

        # Stockage des mesures
        self.current_measure[self.PITCH_INDEX, 0] = pitch
        self.current_measure[self.ROLL_INDEX, 0] = roll
        self.current_measure[self.HEADING_INDEX, 0] = fusion_heading
        self.current_measure[self.X_INDEX, 0] = x_cam
        self.current_measure[self.Y_INDEX, 0] = y_cam
        self.current_measure[self.Z_INDEX, 0] = fusion_z

        self.measures_matrix = np.column_stack((self.measures_matrix, self.current_measure))
        
        return x_cam, y_cam
     
    def donnee_fusion(self):
        
        return x_cam, y_cam


    def run_csv(self, steps=100, delay=0.1):
        for _ in range(steps):
            self.step()
            print(self.get_current_measures())
            time.sleep(delay)

        if save_csv:
            np.savetxt("mesures.csv", self.measures_matrix, delimiter=",")
            print("Mesures sauvegardées dans mesures.csv")


if __name__ == "__main__":
    fusion_sys = Fusion()
    for i in range (500):
        fusion_sys.step()
        print(fusion_sys.donnee_fusion())
        time.sleep(0.2)

