# Avancement de la modélisation et du contrôle

En octobre, prise en main du dirigeable, essais de réglage du correcteur de l'axe z.

Bilan ?

Quels programmes sont fonctionnels ?

Novembre : 
Séance du 7 novembre

PID_eloi : stable mais non précis -> erreur de 5cm pour 2m
Première approche des April Tags : grande liste convient , vibration du moteur pour vitesse > 25 : tags non détecté
Erreur de minimum : 2 minimums détectés -> lié au calcul de position 

Essai en XY (code essai..._dg , fichier: 10:24) : commande avant : gauche positif, droit négatif
Bascule et chute en commande avant-arrière

Travail sur lacet : sens horaire : 4 moteurs en positif

Séance 14 novembre
PID :

PID_alt = PID(30, 0, 1e6, 40, 0.1, 0.00001)
PID_lacet = PID(2, 0, 1e4, 30, 0.05, 0.0001)

28 novembre :

Changement pin moteur : pin 3 -> zg et pin 6 -> zd 
test_lib v12 
