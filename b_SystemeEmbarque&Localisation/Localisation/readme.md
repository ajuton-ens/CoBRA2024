# Localisation d'intérieur




**Objectif** : évaluer et comparer des techniques de localisation en intérieur (ex:  radiogoniométrie Bluetooth, capteur de flux optique, fingerprinting, triangulation par vision, centrale inertielle...)

**Matériel disponible** : 
* des cartes microcontrôleurs Microbit programmables en python (avec récepteur bluetooth), des cartes microcontrôleur STM32 programmables en C, des raspberry Pi et raspberry Pi zéro (Wifi + bluetooth)
* des caméras RPI 2
* des capteurs de pression bme280
* des centrales inertielles avec Motion Processor Unit BNO055 et des centrales MPU9250
* tous les détecteurs de présence bluetooth de l'école et toutes les bornes wifi
* un kit MarvelMind Starter set Super-MP [8]



## Vision SLAM

*Mathis Goupillon* et *Guillian Audry* ont installé {Ubuntu 22.04 ; ROS2 Humble} sur une RPI4. Ils s'intéressent maintenant à la mise en oeuvre des 3 noeuds : 

* acquisition de l'image de la caméra (caméra RPI ou caméra USB)
* acquisition des données de la centrale inertielle (IMU)
* mise en oeuvre du noeud SLAM pour obtenir la carte et la position sur la carte.

Si tout fonctionne bien, il est envisageable sans trop de difficulté avec ROS2 de délocaliser le noeud SLAM sur un PC fixe, les noeuds acquisition image et IMU restant évidemment dans le contrôleur embarqué dans le dirigeable.

## Vision apriltag

*Mathieu Guerin* et *Maxime Degraeve* ont installé Raspberry OS sur une RPI zéro. L'acquisition de l'image d'une caméra USB est opérationnel. Ils ont commencé à installer apriltag pour la reconnaissance des tags (QR Code grossiers) et le calcul de leur position et orientation. Avec la position de 1 ou plusieurs tags (placés précisément dans l'atrium) dans le repère du dirigeable, on peut retrouver la position du dirigeable dans l'atrium.
L'utilisation de la smart-caméra HuskyLens est laissée de côté pour l'instant, ayant trop peu de possibilités de réglage.

## Radio

*Simon Chardin*, *Pierre-Louis Filoche* et *Pierrot Cadeilhan* ont travaillé sur le fingerprint. Après quelques essais et de la lecture biblio, la solution semble, comme on pouvait s'y attendre, peu précise (2,6 m annonce la biblio). Elle est donc abandonnée.
En attendant l'évaluation d'un système Marvelmind au retour des vacances, les étudiants ont travaillé sur micro:bit à la mise en oeuvre de télémètre ultrason SRF02 et SRF10 pour la détection d'obstacle.

## Proprioception
*Damien Chevalier* met en oeuvre sur micro:bit le capteur BME280 (température, pression, humidité) et fait une recherche de capteurs de pression plus précis. *Mathias Le Maigat* met en oeuvre la centrale inertielle (IMU) BNO055 pour estimer d'abord l'orientation du dirigeable (roll, pitch, yaw) et si possible pour estimer la position relative à la position de départ.


## Bibliographie

[1] Ellisys Bluetooth Video #14: Bluetooth Direction Finding, (8 mai 2019). Disponible sur: https://www.youtube.com/watch?v=38O2aK-aiaw

[2] R. Fedorenko et V. Krukhmalev, « Indoor Autonomous Airship Control and Navigation System », MATEC Web of Conferences, vol. 42, p. 01006, 2016, doi: 10.1051/matecconf/20164201006 (http://www.matec-conferences.org/10.1051/matecconf/20164201006)

[3] J. Rao, Z. Gong, J. Luo, et S. Xie, « A flight control and navigation system of a small size unmanned airship », in IEEE International Conference Mechatronics and Automation, 2005, juill. 2005, p. 1491-1496 Vol. 3. doi: 10.1109/ICMA.2005.1626776. Disponible sur: https://ieeexplore.ieee.org/document/1626776

[4] S. Subedi et J.-Y. Pyun, « Practical Fingerprinting Localization for Indoor Positioning System by Using Beacons », Journal of Sensors, vol. 2017, p. e9742170, déc. 2017, doi: 10.1155/2017/9742170 (https://www.hindawi.com/journals/js/2017/9742170/)

[5] X. Yu, H. Wang, et J. Wu, « A method of fingerprint indoor localization based on received signal strength difference by using compressive sensing », EURASIP Journal on Wireless Communications and Networking, vol. 2020, nᵒ 1, p. 72, avr. 2020, doi: 10.1186/s13638-020-01683-8 (https://doi.org/10.1186/s13638-020-01683-8)

[6] Angle of Arrival - Bluetooth 5.1 Direction Finding Explanation, (28 janvier 2019). Disponible sur: https://www.youtube.com/watch?v=c3XqbEKmNcM

[7] « Optical flow », Wikipedia. Disponible sur: https://en.wikipedia.org/w/index.php?title=Optical_flow&oldid=1152281324

[8] Marvelmind propose plusieurs kits de localisation d'intérieur : https://marvelmind.com

[9] AprilTags https://april.eecs.umich.edu/software/apriltag

