import time
import math
import numpy as np


class interpol:
    def __init__(self, sensor):
        # on prend le capteur en paramètre au lieu de le recréer
        self.sensor = sensor

    def init(self):
        sensor = self.sensor

        #===============================
        #norme de l'accélération de la pesanteur
        #===============================
        print("Calcul de la norme de l'accélération de la pesanteur...")
        somme_g = 0
        for i in range(100):
            ax, ay, az = sensor.accxyz()
            g = math.sqrt(ax**2 + ay**2 + az**2)
            somme_g += g
            time.sleep(0.01)
        self.g_ms2imu = somme_g/100
        print("Norme de la pesanteur en m/s^2 capteur:", self.g_ms2imu)

        #===================================
        #détermination du repère fixe (dirigeable immobile)
        #===================================
        print("Détermination du repère fixe dans 2 secondes, dirigeable immobile...")
        time.sleep(2)
        somme_ax = somme_ay = somme_az = 0
        for i in range(100):
            ax, ay, az = sensor.accxyz()
            somme_ax += ax
            somme_ay += ay
            somme_az += az
            time.sleep(0.01)
        ax = somme_ax/100
        ay = somme_ay/100
        az = somme_az/100
        Phi_init_rad = np.arctan2(ay, az)
        Theta_init_rad = np.arctan2(-ax, np.sqrt(ay**2+az**2))
        Psi_init_rad = 0
        R_init_fixe_vers_IMU = sensor.Rotation(Phi_init_rad, Theta_init_rad, Psi_init_rad)
        self.R_init_fixe_vers_IMU = R_init_fixe_vers_IMU
        print("Repère fixe déterminé. Phi=", Phi_init_rad, "Theta=", Theta_init_rad, "Psi=", Psi_init_rad)

        #===================================
        #estimation des biais de l'IMU
        #===================================
        print("Estimation des biais de l'IMU, dirigeable immobile...")
        somme_ax_imu = somme_ay_imu = somme_az_imu = 0
        for i in range(100):
            ax, ay, az = sensor.accxyz()
            somme_ax_imu += ax
            somme_ay_imu += ay
            somme_az_imu += az
            time.sleep(0.01)
        ax_imu = somme_ax_imu/100
        ay_imu = somme_ay_imu/100
        az_imu = somme_az_imu/100
        gravite_imu = np.dot(R_init_fixe_vers_IMU, np.array([0, 0, self.g_ms2imu]))
        self.biais_acc_imu_vec = np.array([ax_imu, ay_imu, az_imu]) - gravite_imu
        print("Biais accéléromètre m/s^2:", self.biais_acc_imu_vec)

        #initialisation des états
        self.t1 = time.time()
        self.Phi_acc_est_PB = Phi_init_rad
        self.Phi_acc_est_rad_1 = Phi_init_rad
        self.Theta_acc_est_PB = Theta_init_rad
        self.Theta_acc_est_rad_1 = Theta_init_rad
        self.Phi_est_gyro_rad_PB = Phi_init_rad
        self.Theta_est_gyro_rad_PB = Theta_init_rad
        self.Theta_est_gyro_rad_1 = 0
        self.Phi_est_gyro_rad_1 = 0

    def pos(self, X, Y, Z, Vx, Vy, Vz, Phi, Theta, Psi):
        sensor = self.sensor
        Angles = np.array([Phi, Theta, Psi])

        t1 = self.t1
        Phi_acc_est_PB = self.Phi_acc_est_PB
        Phi_acc_est_rad_1 = self.Phi_acc_est_rad_1
        Theta_acc_est_PB = self.Theta_acc_est_PB
        Theta_acc_est_rad_1 = self.Theta_acc_est_rad_1
        Phi_est_gyro_rad_PB = self.Phi_est_gyro_rad_PB
        Theta_est_gyro_rad_PB = self.Theta_est_gyro_rad_PB
        Phi_est_gyro_rad_1 = self.Phi_est_gyro_rad_1
        Theta_est_gyro_rad_1 = self.Theta_est_gyro_rad_1
        g_ms2imu = self.g_ms2imu
        biais_acc_imu_vec = self.biais_acc_imu_vec

        t2 = time.time()
        ax, ay, az = sensor.accxyz()
        gx, gy, gz = sensor.gyrxyz()

        Phi_acc_rad = np.arctan2(ay, az)
        Theta_acc_rad = np.arctan2(-ax, np.sqrt(ay**2+az**2))

        Phi_gyro_rad = gx
        Theta_gyro_rad = gy
        Psi_gyro_rad = gz

        Dangle_gyro_rad = np.array([Phi_gyro_rad, Theta_gyro_rad, Psi_gyro_rad])
        R_current = sensor.Rotation(Angles[0], Angles[1], Angles[2])
        Dangle_gyro_rad_fixe = np.dot(R_current, Dangle_gyro_rad)
        Angles_est_gyro_rad = Dangle_gyro_rad_fixe
        Phi_est_gyro_rad = Angles_est_gyro_rad[0]
        Theta_est_gyro_rad = Angles_est_gyro_rad[1]
        Psi_est_gyro_rad = Angles[2] + Angles_est_gyro_rad[2] * (t2 - t1)

        Phi_acc_est_rad = np.arctan2(ay, az)
        Theta_acc_est_rad = np.arctan2(-ax, np.sqrt(ay**2+az**2))

        K_acc = 1
        Tau_acc = 0.2
        K_gyro = 1
        Tau_gyro = 0.2

        Phi_acc_est_PB = sensor.passe_bas(K_acc, (t2-t1), Tau_acc, Phi_acc_est_PB, Phi_acc_est_rad, Phi_acc_est_rad_1)
        Theta_acc_est_PB = sensor.passe_bas(K_acc, (t2-t1), Tau_acc, Theta_acc_est_PB, Theta_acc_est_rad, Theta_acc_est_rad_1)
        Phi_acc_est_rad_1 = Phi_acc_est_rad
        Theta_acc_est_rad_1 = Theta_acc_est_rad

        Phi_est_gyro_rad_PB = sensor.passe_bas(K_gyro, t2-t1, Tau_gyro, Phi_est_gyro_rad_PB, Phi_est_gyro_rad, Phi_est_gyro_rad_1)
        Theta_est_gyro_rad_PB = sensor.passe_bas(K_gyro, t2-t1, Tau_gyro, Theta_est_gyro_rad_PB, Theta_est_gyro_rad, Theta_est_gyro_rad_1)
        Psi_est_gyro_rad_PB = Psi_est_gyro_rad
        Phi_est_gyro_rad_1 = Phi_est_gyro_rad
        Theta_est_gyro_rad_1 = Theta_est_gyro_rad

        Phi_est_rad = Phi_acc_est_PB #+ Phi_est_gyro_rad_PB
        Theta_est_rad = Theta_acc_est_PB #+ Theta_est_gyro_rad_PB
        Psi_est_rad = Psi_est_gyro_rad_PB

        acc_imu_vec = np.array([ax, ay, az])
        acc_imu_vec_em = acc_imu_vec - np.dot(R_current, np.array([0, 0, g_ms2imu])) - biais_acc_imu_vec
        acc_fixe_mesuree = np.dot(R_current, acc_imu_vec_em)
        A_Fixe_ms2_vec = acc_fixe_mesuree

        p0 = np.array([X, Y, Z])
        v0 = np.array([Vx, Vy, Vz])

        V_Fixe_ms_vec = v0 + A_Fixe_ms2_vec * (t2 - t1)
        P_Fixe_m_vec = p0 + V_Fixe_ms_vec * (t2 - t1)

        self.t1 = t2
        self.Phi_acc_est_PB = Phi_acc_est_PB
        self.Phi_acc_est_rad_1 = Phi_acc_est_rad_1
        self.Theta_acc_est_PB = Theta_acc_est_PB
        self.Theta_acc_est_rad_1 = Theta_acc_est_rad_1
        self.Phi_est_gyro_rad_PB = Phi_est_gyro_rad_PB
        self.Theta_est_gyro_rad_PB = Theta_est_gyro_rad_PB
        self.Phi_est_gyro_rad_1 = Phi_est_gyro_rad_1
        self.Theta_est_gyro_rad_1 = Theta_est_gyro_rad_1

        return P_Fixe_m_vec[0], P_Fixe_m_vec[1], P_Fixe_m_vec[2], Phi_est_rad, Theta_est_rad, Psi_est_rad
