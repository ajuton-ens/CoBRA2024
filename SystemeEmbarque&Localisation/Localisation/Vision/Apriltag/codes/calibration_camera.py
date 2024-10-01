import numpy as np
import cv2
import glob
# Définition des paramètres du motif
pattern_size = (8,8)  # Nombre de coins internes du motif
square_size = 1.0  # Taille d'un carré dans le motif en unités arbitraires

# Préparation des points du motif
obj_points = []
img_points = []

# Création des points 3D du motif
objp = np.zeros((np.prod(pattern_size), 3), dtype=np.float32)
objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size

# Chargement des images
images = glob.glob('images calibration/*.jpg')  # Mettez le chemin correct vers vos images

for fname in images:
    
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print(fname)
    # Trouver les coins du motif
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
    
    # Si les coins sont trouvés, ajouter les points correspondants
    if ret:
        img_points.append(corners)
        obj_points.append(objp)

        # Dessiner et afficher les coins sur l'image
        img = cv2.drawChessboardCorners(img, pattern_size, corners, ret)
        cv2.imshow('Chessboard Corners', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# Calibration de la caméra
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

# Affichage des résultats
print("Matrice intrinsèque (fx, fy, cx, cy):\n", mtx)
print("Coefficients de distorsion:\n", dist)