# Architecture de la carte raspberry pi 5

Par Lucie, Anis, Lisa et Matisse

## Fonction à intéger

* réulateur de tension (batterie -> 5V 3A) (OKL-T/6-W12N-C) (ajouté sur schéma carte)
* controleur pwm (x6 sorties) (ajouté sur schéma carte)
* centrale intertielle (bno055) (ajouté sur schéma carte)
* capteur pression ambiante (icp101 ou LPS22) (on a mis des pins sur le schéma de la carte)
* Pont en H (L293) (ajouté sur le schéma de la carte)
* ventilateur (pas besoin de le mettre sur la carte, on l'ajoutera directement sur la RPI5 - il faudra prévoir un trou dans le PCB)
* télémètre LUNA (on a rajouté des pins sur le schéma de la carte)
* branchement des moteurs (on a rajouté 8 pins sur le schéma de la carte)
* pince et treuil (on a rajouté des pins sur le schéma de la carte pour commander leurs moteurs)

## Fonctions intégrés