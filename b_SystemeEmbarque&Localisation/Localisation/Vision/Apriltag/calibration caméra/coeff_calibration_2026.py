import numpy as np
import cv2 as cv
import glob
import os

# CONFIGURATION 
WIDTH, HEIGHT = 1152, 648       # Résolution à calibrer
nb_cols = 7                     # coins intérieurs horizontaux
nb_rows = 8                     # coins intérieurs verticaux
square_size = 0.03              # taille réelle d'une case (mètres)

base_dir = "/home/banane/Documents/apriltag_env/work/"
images_dir = os.path.join(base_dir, f"images_{WIDTH}x{HEIGHT}/")
output_dir = os.path.join(base_dir, f"annotated_{WIDTH}x{HEIGHT}/")
calib_file = os.path.join(base_dir, f"calibration_{WIDTH}x{HEIGHT}.npz")
os.makedirs(output_dir, exist_ok=True)

criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# POINTS 3D REELS
objp = np.zeros((nb_rows * nb_cols, 3), np.float32)
objp[:, :2] = np.mgrid[0:nb_cols, 0:nb_rows].T.reshape(-1, 2)
objp *= square_size

objpoints = []
imgpoints = []

images = glob.glob(os.path.join(images_dir, "*.jpg"))

if not images:
    print(f"Aucune image trouvée dans {images_dir}")
    exit()

# DETECTION
for fname in images:
    img = cv.imread(fname)
    if img is None:
        continue

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    ret, corners = cv.findChessboardCorners(
        gray,
        (nb_cols, nb_rows),
        cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_NORMALIZE_IMAGE
    )

    if ret:
        corners2 = cv.cornerSubPix(gray, corners, (21, 21), (-1, -1), criteria)
        objpoints.append(objp)
        imgpoints.append(corners2)

        cv.drawChessboardCorners(img, (nb_cols, nb_rows), corners2, ret)
        cv.imwrite(os.path.join(output_dir, os.path.basename(fname)), img)

        print(f"[OK] {fname}")
    else:
        print(f"[NO] {fname}")

# VERIFICATION
if not objpoints:
    print("Aucun damier détecté. Calibration impossible.")
    exit()

# CALIBRATION
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)


print("\nCALIBRATION TERMINEE")
print(f"Résolution : {WIDTH}x{HEIGHT}")
print(f"Images utilisées : {len(objpoints)}/{len(images)}")
print(f"Erreur RMS : {ret:.4f}")
print(f"Matrice intrinsèque :\n{mtx}")
print(f"Distorsion :\n{dist}")

# SAUVEGARDE 
np.savez(calib_file, width=WIDTH, height=HEIGHT, mtx=mtx, dist=dist, rms=ret)
print(f"\nCalibration sauvegardée dans : {calib_file}")