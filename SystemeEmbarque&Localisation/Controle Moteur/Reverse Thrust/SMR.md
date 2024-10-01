# SMR (pour Switching Motor Rotation ? anyway)
## En gros...
Le SMR est un paramètre booléen interne au variateur qui permet à un signal logique transmis par un 4ème fil (Reverse Signal Wire) de commander le sens de rotation du moteur. Il est par défaut à OFF, il faut donc l'activer en passant par le mode programmation du variateur.\
![image](https://github.com/bruno2nis/cobra/assets/147141994/8a5a0588-629a-4f7c-abd6-8c0723318ba5)

## Pour le Pichler XQ 20
### Documents utiles
On a la [doc du XQ20](https://asset.conrad.com/media10/add/160267/c1/-/gl/003014603ML00/mode-demploi-3014603-pichler-xq-20-slim-regulateur-brushless-pour-avion-charge-admissible-max-30-a.pdf).
- /!\ Le constructeur annonce un risque de déterioration si SMR est utilisé à plus de 50% de la puissance du moteur (envisager une commande en trapèze pour inverser la vitesse, pour éviter les efforts inertiels ?)
- ESSAYER LA PROCHAINE FOIS


Plus de précision sur le programmation mode dans la [doc de la série XQ](http://www.pichler.de/PDF/XQ20160414.pdf).
- On comprend comment naviguer dans le menu programmation
- La fonction SMR n'est pas dispo dans toutes les variateurs de la série XQ
- /!\ Le paramètre MR n'est pas le même que SMR (MR ne permet pas une gestion dynamique)

## Point sur la situation (17/05/24)
Protocole: (manettte radiolink, récepteur radiolink, variateur, batterie)
- Connecter le variateur sur le CH2 du R8EF
- Mettre le joystick de propulsion en position haute
- Mettre sous tension le variateur
  
On est alors dans le mode programmation. 
- Mettre le joystick en position haute fait défiler les fonctions
- Mettre le joystick en position basse change le paramètre de la fonction (il défilera parmis les paramètres possibles)
- Mettre le joystick en position haute pour valider

 Cependant /!\
- Il y a 13 fonctions au lieu de 10 (., .., ..., ...., _, _ ., _ .., _ ..., _ ...., _ _, _ _ ., _ _ .., _ _ ...) -> problème pour crossréférencer les fonctions (Hypoyhèse: Dans l'ordre pour les 10 premières !!)

Je vais essayer avec le sens de rotation -> CCW -> ça marche !!
ça marche aussi pour le SMR.

## Résumé
### Matériel
- récepteur radiolink R82F
- télécommande radiolink T8BF
- variateur XQ20
- batterie
### Protocole
- Connecter le variateur sur le CH2 du R8EF
- Mettre le joystick de propulsion en position haute
- Mettre sous tension le variateur

On entend .. puis une musique, annonçant qu'on est dans le menu de programmation. Les fonctions vont défiler de 1 à 13, signalées leur code sonore.

![image](https://github.com/bruno2nis/cobra/assets/147141994/bfce861c-ed57-4c1b-8853-4755ce0fb280)
|  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8  |  9  | 10  | 11  | 12  | 13  |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|  .  | ..  | ... |.... |  _  | _.  | _.. |_... |_....| _ _ | _ _.|_ _..|_ _...|
- Mettre le joystick en position basse pour sélectionner <strong>la première fonction</strong> (SMR)
- Les paramètres vont défiler, signalés par leur code sonore
- Relever le joystick en position haute pour sélectionner <strong>le second paramètre</strong> (ON)
On entend une musique signalant que le paramètre est modifié, on peut alors mettre le variateur hors tension et remettre le joystick en position basse
