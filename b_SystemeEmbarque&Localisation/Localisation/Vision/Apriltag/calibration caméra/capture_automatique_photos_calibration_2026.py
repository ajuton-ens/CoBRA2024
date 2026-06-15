import cv2
from picamera2 import Picamera2
import numpy as np
import time
import os

# CONFIGURATION
WIDTH, HEIGHT = 1152, 648    # Résolution
NB_PHOTOS = 30                  # Nombre de photos à récupérer
DELAI = 5                       # Délai (s) entre chaque photo
nb_cols = 7                     # coins intérieurs horizontaux du damier
nb_rows = 8                     # coins intérieurs verticaux

save_dir = f"/home/banane/Documents/apriltag_env/work/images_{WIDTH}x{HEIGHT}/"
os.makedirs(save_dir, exist_ok=True)

# INITIALISATION CAMERA 
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "XRGB8888", "size": (WIDTH, HEIGHT)}
    )
)
picam2.start()
time.sleep(1)  # stabilisation

print(f"\nCAPTURE CALIBRATION {WIDTH}x{HEIGHT}")
print(f"Objectif : {NB_PHOTOS} photos valides")
print(f"Dossier : {save_dir}\n")

# BOUCLE DE CAPTURE 
photos_valides = 0
tentatives = 0

while photos_valides < NB_PHOTOS:
    # Décompte
    for s in range(DELAI, 0, -1):
        print(f"  {s}", end=" ", flush=True)
        time.sleep(1)
    print("CAPTURE")

    # Capture
    image = picam2.capture_array()
    tentatives += 1

    # Validation : détection du damier
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, _ = cv2.findChessboardCorners(
        gray,
        (nb_cols, nb_rows),
        cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    if ret:
        photos_valides += 1
        filename = os.path.join(save_dir, f"photo_{photos_valides:02d}.jpg")
        cv2.imwrite(filename, image)
        print(f"Photo {photos_valides}/{NB_PHOTOS} validée ({filename})\n")
    else:
        print(f"Damier non détecté (tentative {tentatives}), on réessaie\n")

picam2.stop()
print(f"TERMINÉ : {NB_PHOTOS} photos en {tentatives} tentatives")