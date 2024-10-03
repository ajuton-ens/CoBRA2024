# Avancement:
## Angle of arrival, Angle of departure (bof bof)
- Les signaux bluetooth/WiFi ont la bonne longueur d'onde ! Mais...
- Les signaux sont trop bruités pour obtenir une mesure de déphasage de la porteuse claire [1]
- Les signaux WiFi sont modulés en Phase/Frequence donc la mesure de déphasage en serait impactée
## RSSI based localisation technique (fingerprinting, triangulation, etc) (bof bof)
- Le RSSI, pour Received Signal Strength Indicator s'exprime en dBm selon la formule RSSI = log(P/Pref) avec Pref = 1mW
- L'incertitude mesurée sur le RSSI est de 50% autour de -30dBm, on a donc /\P = ln(10)xPrefx10^(RSSI)x/\RSSI = Pxln(10)x/\RSSI, d'où /\P/P = 69.1
- De plus, la température influence le RSSI (à prendre en compte !) [2]
- Et les meilleurs résultats ne sont pas suffisant vis à vis du CDC [3]
## Ultrason (??)
- On a fait le montage une fois ahah
## Marvelmind indoor GPS (en cours)
meilleur solution so far
Premier test de prise dans l'atrium : bon résultats, bonne précisions: sur le logiciel fourni regardez le tableau des distances et pas la carte au début 
Simon : utilisation de bibli python pour avoir les résultats directement du routeur mobile sur la console python et ainsi pouvoir les traiter manuellement.
Pilou : mise en config de la pi0, OS, reso et mise en place des script python
Pierrot : algo de distances


22/12/2023
On veut quantifier la surface couverte par un kit dans l'atrium. Mesure de l'écartement maximale entre 2 balises fixes qui nous permet de garder une précision de l'ordre du décimètre.
Choix des points: (0, 0, 0), (0, 15.2, 0), (-5.14, 30.4, 0)
Python : création d'une map dynamique à l'aide des positions xyz obtenues


Pi0 :
adresse du routeur 192.168.50.1 (covapsy;covapsy$2022)
nom d'hote : tpresopierr
username : pierr
mdp : pierr2023
IP : 192.168.50.18

WIFI : 
covapsy2
covapsy$2022

Terminal : 
ping + ip : permet de verifier la bonne connexion à l'appareil
ssh pierr@192.168.50.18

detection avec une camera branché sur une raspberry pi zero 2 (id : cobra0 / mdp : cobra0)
accés par routeur covapsy (id : covapsy2 / mdp : covapsy$2022) interface admin (id : covapsy / mdp : covapsy$2022)
port pi0 : /dev/ttyAMS0
FERMER LE logiciel MarvelMind

22/03: FAIRE la map dès le début et faire la batterie de test &
sudo chmod a+rw /dev/ttyACM0 pour avoir accès au port (trouver sur https://askubuntu.com/questions/1219498/could-not-open-port-dev-ttyacm0-error-after-every-restart)

22/03 : réception des nouvelles balises. Pb avec dashboard obligé de re télécharger.
step 1 : connecter les nouvelles balises, noter leur numéro pour les placer dans la salle
step 2 : faire la map sur dashboard 

semaine suivante : création de la map en mesurant approximativement la salle : on obtient déjà une bonne précision : next step faire une équipe pour mesurer l'atrium précisement

--vol ordi + vacances => retour en arrière -- 

26/04 : réinstallation de l'environnement marvelMind et reconnexion manuelle de toutes les balises   
        réinstallation des programmes python et reconnexion ç la RPI0


-- MarvelMind guide -- @Pilou
Le kit de balise MarvelMind permet de localiser un objet en mouvement quelque soit l'environnement (en intérieur => pas de gps). Le système de positionnement fonctionne grâce aux ultrasons et les balises communiquent entre elles via des ondes radio.
Matos à disposition : 2 kit de 5 balises + 1 modem.
Attention les 2 kits ne sont pas compatibles car pas la même fréquences de communications entre les balises (ancienne et nouvelle générations).
Le kit dernière génération fonctionne sur la fréquence 915/868 MHz. Bien faire attention à cela si on rachète un autre kit mais normalement ceux en vente actuellement sont sur ces fréquences.

Fonctionnement pratique : 5 balises = 4 balises fixes et une balise mobile à placer sur l'objet dont on veut connaitre la position. N'importe laquelle des 5 balises peut être utilisées pour être la balise mobile. Le modem (6e élément de la boite permet la communication entre les balises et avec l'ordi.

Logiciel : télécharger Dashboard (https://marvelmind.com/download/#SW aller à step5) 

Mise en place : brancher le modem à l'ordi, lancer dashboard (à trouver dans tous les fichiers après avoir de zipper le truc telechargé mais ça se trouve). Le modem devrait être reconnu direct par le logiciel => penser à télécharger le driver si pas de connexion trouver (step 4 du lien de téléchargement => il faut l'executer et relancer dashboard/l'ordi). Enlever le modem et connecter toutes las balises :
https://marvelmind.com/pics/marvelmind_navigation_system_manual.pdf p88 bonne explication de comment faire. pour les allumer mettre le pztit switch le plus à l'exterieur de la balise en ON. => penser à les éteindre après utilisation pour ne pas décharger les batteries.

Pour faire de l'embarqué. 
On utilise une RPI 0 2 connectée à covapsy3 (covapsy$2022) username : pierr , name: pierr , mdp : pierr.
ping pierr.local #pour tester la connexion à la carte
ping pierr.local -4 #pour avoir l'adresse ip
ssh pierr@192.168.50.44 pour se connecter à la carte sur cmd
sudo raspi-config #une fois connect en ssh permet de enable vnc










# Sources
- [1] Anthony Juton
- [2] https://www.researchgate.net/figure/The-change-of-RSSI-according-to-temperature_fig15_51873264
- [3] https://www.researchgate.net/publication/338944361_RoboMapper_An_Automated_Signal_Mapping_Robot_for_RSSI_Fingerprinting
