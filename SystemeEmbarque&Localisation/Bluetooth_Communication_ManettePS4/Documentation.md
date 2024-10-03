# INTERFACE DE PILOTAGE: le controlleur Dualshock4
## Présentation:
Cette documentation vous guidera à travers l'implémentation dans python du controlleur Dualshock4 comme périphérique d'entrée.
- On utilisera une carte Rapsberry Pi Zero Wireless sous [Raspbian](https://www.raspberrypi.com/software/)
- La bibliothèque [pyPS4Controller](https://pypi.org/project/pyPS4Controller/)

## Préparation du materiel
- Il convient d'abord d'installer une configuration adéquate sur la Pi Zero. Pour ce faire, se réferer au [tutoriel](Installation_RaspberryPi4_minimum.pdf) fourni par Anthony Juton.
- Il faut appairer le controlleur Dualshock4 à la Pi Zero dans les paramètres bluetooth, via l'interface graphique RealVNC.

## Bibliothèque pyPS4Controller
- Il faut installer dans un premier lieu la bibliothèque à l'aide de la commande ```pip install pyPS4Controller```
- On peut ensuite adapter l'[exemple complet](https://pypi.org/project/pyPS4Controller/1.1.1/) fourni dans la documentation de la bibliothèque.
- /!\ L'exemple tel quel n'est pas exploitable, car le mapping par défaut des entrées n'est pas bon. Il faut donc changer la dernière ligne de l'exemple par ```MyController(interface="/dev/input/js0", connecting_using_ds4drv=False).listen()```, où le parametre ```connecting_using_ds4drv``` mis à False permet d'éviter cette erreur d'identification des entrées.
- /!\ Lors de l'exécution des fonctions ```on_'event'()```, la détection des autres entrées s'interrompt. Il faut donc éviter d'exécuter des codes de commande trop long, ou utiliser du multi-threading le cas échéant. 
