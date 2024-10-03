# Systèmes embarqués et Localisation

Enseignant référent : Anthony Juton

Cette page est destinée à présenter l'avancement du travail sur :

* La prise en main de la carte Raspberry Pi Zero 2 W
* L'évaluation des télémètres infrarouge (Capteur de Distance LIDAR 8m TF-Luna)
* L'amélioration des bibliothèque d'utilisation des capteurs (BNO055, télémètre) et actionneurs (variateurs ESC et servo-moteurs)
* L'évaluation des capteurs Bosch proprioceptifs
* La localisation

## Présentation des 2 solutions de localisation retenues après le travail de 2023-2024

**Vision apriltag**

*Mathieu Guerin* et *Maxime Degraeve* ont installé Raspberry OS sur une RPI zéro. L'acquisition de l'image d'une caméra USB est opérationnel. Ils ont commencé à installer apriltag pour la reconnaissance des tags (QR Code grossiers) et le calcul de leur position et orientation. Avec la position de 1 ou plusieurs tags (placés précisément dans l'atrium) dans le repère du dirigeable, on peut retrouver la position du dirigeable dans l'atrium. Leur code est dans le dossier Localisation

**GPS Indoor**

*Pierre-Louis Filoche* après un travail commun avec *Pierrot Cadeilhan* et *Simon Chardin* a mis en oeuvre le GPS Indoor de Marvel Mind (https://marvelmind.com/)


## Bibliographie

[1] R. Fedorenko et V. Krukhmalev, « Indoor Autonomous Airship Control and Navigation System », MATEC Web of Conferences, vol. 42, p. 01006, 2016, doi: 10.1051/matecconf/20164201006 (http://www.matec-conferences.org/10.1051/matecconf/20164201006)

[2] J. Rao, Z. Gong, J. Luo, et S. Xie, « A flight control and navigation system of a small size unmanned airship », in IEEE International Conference Mechatronics and Automation, 2005, juill. 2005, p. 1491-1496 Vol. 3. doi: 10.1109/ICMA.2005.1626776. Disponible sur: https://ieeexplore.ieee.org/document/1626776

[3] Le site web des centrales inertielles de bosch : https://www.bosch-sensortec.com/products/motion-sensors/imus/

[8] Marvelmind propose plusieurs kits de localisation d'intérieur : https://marvelmind.com

[9] AprilTags https://april.eecs.umich.edu/software/apriltag

