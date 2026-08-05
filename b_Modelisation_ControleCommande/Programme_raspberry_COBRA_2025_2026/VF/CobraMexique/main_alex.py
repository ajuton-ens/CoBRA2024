from smbus2 import SMBus
from bmm350 import BMM350
from imubis import IMU
from IMU_fonc import interpol
from loc_clem_json import PosCamFix
from tf_luna import LidarTFLuna
import time
import math
import asyncio
import json
import os
import numpy as np
from filterpy.kalman import KalmanFilter

# ============================
# Capteurs
# ============================
bus = SMBus(1)

mag = BMM35(bus)
sensor = IMU(bus)
lidar = LidarTFLuna(bus, i2c_address=0x10)


mag._init_sensor()
print("BMM350 prêt")

sensor.allumage_accel()
time.sleep(0.05)
sensor.init_accel()
sensor.init_gyro()
print("IMU prête")

print("LiDAR TF Luna prêt")

fusion = interpol(sensor)    # on passe le sensor à la fusion
fusion.init()

camfix = PosCamFix()
camfix.start()
print("Serveur caméra fixe lancé")

# ============================
# Etat partagé
# ============================
class Etat:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.vz = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.actif = True

etat = Etat()
etat_lock = asyncio.Lock()

# ============================
# Kalman 3D
# ============================
dt = 0.01

kf = KalmanFilter(dim_x=6, dim_z=3)
kf.x = np.zeros(6)
kf.F = np.array([
    [1, dt, 0, 0,  0, 0 ],
    [0, 1,  0, 0,  0, 0 ],
    [0, 0,  1, dt, 0, 0 ],
    [0, 0,  0, 1,  0, 0 ],
    [0, 0,  0, 0,  1, dt],
    [0, 0,  0, 0,  0, 1 ],
])
kf.H = np.array([
    [1, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 1, 0],
])
kf.P *= 10
kf.Q = np.eye(6) * 0.1

R_CAM_FIXE = np.diag([1, 1, 50])
R_LIDAR    = np.diag([1e6, 1e6, 1])

kf_yaw = KalmanFilter(dim_x=1, dim_z=1)
kf_yaw.x = np.array([0.0])
kf_yaw.F = np.array([[1.0]])
kf_yaw.H = np.array([[1.0]])
kf_yaw.P *= 10
kf_yaw.Q = np.array([[0.01]])

R_MAG    = 1
R_CAM_YAW = 0.5

kalman_lock = asyncio.Lock()

# ============================
# Fichier de pose partagé pour l'asservissement
# ============================
FICHIER_POSE = "/tmp/pose.json"

# ============================
# IMU 100 Hz
# ============================
async def tache_imu():
    while etat.actif:
        async with etat_lock:
            x0, y0, z0 = etat.x, etat.y, etat.z
            vx0, vy0, vz0 = etat.vx, etat.vy, etat.vz
            roll0, pitch0, yaw0 = etat.roll, etat.pitch, etat.yaw

        x_imu, y_imu, z_imu, roll, pitch, yaw_imu = fusion.pos(
            x0, y0, z0, vx0, vy0, vz0, roll0, pitch0, yaw0
        )

        async with kalman_lock:
            kf.predict()
            kf_yaw.predict()
            async with etat_lock:
                etat.x = kf.x[0] / 100.0
                etat.y = kf.x[2] / 100.0
                etat.z = kf.x[4] / 100.0
                etat.vx = kf.x[1] / 100.0
                etat.vy = kf.x[3] / 100.0
                etat.vz = kf.x[5] / 100.0
                etat.roll = roll
                etat.pitch = pitch
                etat.yaw = kf_yaw.x[0]

        await asyncio.sleep(dt)

# ============================
# Magnétomètre 25 Hz
# ============================
async def tache_magneto():
    while etat.actif:
        cap_deg = mag.get_cap()
        yaw_mag = math.radians(cap_deg)
        if yaw_mag > math.pi:
            yaw_mag -= 2 * math.pi

        async with kalman_lock:
            kf_yaw.R = np.array([[R_MAG]])
            kf_yaw.update(np.array([yaw_mag]))
            async with etat_lock:
                etat.yaw = kf_yaw.x[0]

        await asyncio.sleep(0.04)

# ============================
# LiDAR 20 Hz
# ============================
async def tache_lidar():
    while etat.actif:
        z_lidar = lidar.mesure_distance()

        if z_lidar is not None and 0.05 < z_lidar < 8.0:
            z_lidar_cm = z_lidar * 100.0
            x_actuel_cm = kf.x[0]
            y_actuel_cm = kf.x[2]

            async with kalman_lock:
                kf.R = R_LIDAR
                kf.update(np.array([x_actuel_cm, y_actuel_cm, z_lidar_cm]))
                async with etat_lock:
                    etat.z = kf.x[4] / 100.0
                    etat.vz = kf.x[5] / 100.0

        await asyncio.sleep(0.05)

# ============================
# Caméra fixe 10 Hz
# ============================
async def tache_camera_fixe():
    while etat.actif:
        x = camfix.x0
        y = camfix.y0
        z = camfix.z0
        theta = camfix.theta

        if x == 0 and y == 0 and z == 0 and theta == 0:
            await asyncio.sleep(0.1)
            continue

        x_cm = x * 100.0
        y_cm = y * 100.0
        z_cm = z * 100.0
        yaw_cam = math.radians(theta)

        async with kalman_lock:
            kf.R = R_CAM_FIXE
            kf.update(np.array([x_cm, y_cm, z_cm]))
            kf_yaw.R = np.array([[R_CAM_YAW]])
            kf_yaw.update(np.array([yaw_cam]))
            async with etat_lock:
                etat.x = kf.x[0] / 100.0
                etat.y = kf.x[2] / 100.0
                etat.z = kf.x[4] / 100.0
                etat.yaw = kf_yaw.x[0]

        await asyncio.sleep(0.1)

# ============================
# Ecriture du fichier de pose 50 Hz - pour l'asservissement
# ============================
async def tache_export_pose():
    tmp = FICHIER_POSE + ".tmp"

    while etat.actif:
        async with etat_lock:
            pose = {
                "t": time.time(),
                "x": etat.x,
                "y": etat.y,
                "z": etat.z,
                "yaw": etat.yaw,
                "vx": etat.vx,
                "vy": etat.vy,
                "vz": etat.vz,
                "roll": etat.roll,
                "pitch": etat.pitch,
            }

        with open(tmp, "w") as f:
            json.dump(pose, f)
        os.replace(tmp, FICHIER_POSE)

        await asyncio.sleep(0.02)

# ============================
# Sauvegarde fichier historique 25 Hz
# ============================
async def tache_fichier():
    fichier = open("mesures.txt", "w")
    fichier.write("# time,x_m,y_m,z_m,yaw_deg\n")
    try:
        while etat.actif:
            async with etat_lock:
                x, y, z, yaw = etat.x, etat.y, etat.z, etat.yaw
            yaw_deg = math.degrees(yaw)
            ligne = f"{time.time()},{round(x,3)},{round(y,3)},{round(z,3)},{round(yaw_deg,1)}\n"
            fichier.write(ligne)
            fichier.flush()
            print(f"x={x:+.3f}m y={y:+.3f}m z={z:+.3f}m yaw={yaw_deg:+.1f}°")
            await asyncio.sleep(0.04)
    finally:
        fichier.close()
        print("Fichier mesures.txt sauvegardé.")

# ============================
# Main asyncio
# ============================
async def main():
    await asyncio.gather(
        tache_imu(),
        tache_magneto(),
        tache_lidar(),
        tache_camera_fixe(),
        tache_export_pose(),
        tache_fichier(),
    )

print("\nDémarrage de la localisation fusionnée... Ctrl+C pour arrêter\n")

try:
    asyncio.run(main())
except KeyboardInterrupt:
    etat.actif = False
    print("\nArrêt demandé.")
finally:
    camfix.Stop()
    bus.close()
    print("Bus I2C fermé. Bye !")
