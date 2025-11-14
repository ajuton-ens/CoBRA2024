# Systèmes embarqués et Localisation

Enseignant référent : Anthony Juton

Cette page est destinée à présenter l'avancement du travail sur :

* La prise en main de la carte Raspberry Pi Zero 2 W
* L'évaluation des télémètres infrarouge (Capteur de Distance LIDAR 8m TF-Luna)
* L'amélioration des bibliothèque d'utilisation des capteurs (BNO055, télémètre) et actionneurs (variateurs ESC et servo-moteurs)
* L'évaluation des capteurs Bosch proprioceptifs
* La localisation

## Avancement 2025-2026

**Vision**
07/11 : tests sur une nouvelle caméra des méthodes de calibration et détection des Apriltags réussis. Familiarisation avec le code de localisation utilisé actuellement sur le dirigeable. Codage sur une nouvelle camera pour la detection du centre du nouveau tag issu de la bibliothèque Aruco pour détecter le dirigeable depuis le plafond, même lorsqu'il est loin. Ceci sert pour détecter la translation du dirigeable. Pour plus tard : finalisation de ce codage pour détecter les rotations.

**GPS Indoor**
GPS Indoor sous Dashboard

Tuto vidéo : https://youtu.be/Uj2_BGS1AjI 

Matériel :
- logiciel Dashboard  
-set marvelmind robotics super-MP-3D (5 beacon et un modem)

Protocole : 
1)	Installer Dashboard sur https://marvelmind.com/download/#SW ainsi que les driver nécessaire
2)	Allumer 2=ON 
3)	Connecter beacon sur le pc en filaire 
4)	Upgrade le firmware de chaque balise et du modem en haut à gauche de l’écran
5)	Cliquer sur le bouton default pour chaque beacon en bas à droite de l’écran
6)	Définir une adresse différence pour chaque beacon (ex : 1,2,3,4,5) et cliquer sur write change en haut à droite de l’écran
7)	Identifier chaque balise en mobile (Mobile Beacon a.k.a. “Hedgehog” ) ou fixe (Stationary Beacon) avec le hedgedog mode en enable ou disable . 
8)	Faire de même pour le modem (firmware+default button)
9)	Placer les balises en mesurant les distances qui les sépares et leurs altitudes respectives. 
10)	Personnellement les balises sont placées à la même hauteur (0.75 m du sol )et forme une surface rectangulaire de 3,5x5,18 m2 (voir carte associé)
11)	Créer une submap
12)	Réveiller chaque balise fixe dans la submap 0 
13)	Rentré manuellement leur position relative(x,y,z) car le mode placement auto n’est pas précis( clique droit sur le beacon sur la carte)
14)	freezsubmap 
15)	Réveiller balise mobile et fixer son altitude



=>On peut maintenant se déplacer dans l’espace (voir vidéo test)  

Piste d’amélioration :
 -placer les balises en hauteur orienté vers la zone à couvrir pour augmenter la zone et réduire les interférences du au passage des humains dans l’espace 
 
-l’altitude ne marche pas (à régler)

-position peu précise(plusieurs frezze de position) ( parfois la balise disparait) 
=>peu fiable et robuste pour le moment 
=> plus fiable/robuste avec 2 balise comme sur la vidéo tuto 

-faire un essai/test sur dirigeable en mouvement 

-intérêt pour le projet final ? 




**Proprioception**
07/11 : test du capteur BMI088, les données sont reçues via un arduino intermédiaire prochaine séance: voire à enlever l'arduino et recevoir les données directement sur le PI via I2C


## Bibliographie

[1] R. Fedorenko et V. Krukhmalev, « Indoor Autonomous Airship Control and Navigation System », MATEC Web of Conferences, vol. 42, p. 01006, 2016, doi: 10.1051/matecconf/20164201006 (http://www.matec-conferences.org/10.1051/matecconf/20164201006)

[2] J. Rao, Z. Gong, J. Luo, et S. Xie, « A flight control and navigation system of a small size unmanned airship », in IEEE International Conference Mechatronics and Automation, 2005, juill. 2005, p. 1491-1496 Vol. 3. doi: 10.1109/ICMA.2005.1626776. Disponible sur: https://ieeexplore.ieee.org/document/1626776

[3] Le site web des centrales inertielles de bosch : https://www.bosch-sensortec.com/products/motion-sensors/imus/

[8] Marvelmind propose plusieurs kits de localisation d'intérieur : https://marvelmind.com

[9] AprilTags https://april.eecs.umich.edu/software/apriltag

[10] Projet abouti https://github.com/elenagiraldo3/april_tags_autolocalization/blob/main/detect_apriltag.py

