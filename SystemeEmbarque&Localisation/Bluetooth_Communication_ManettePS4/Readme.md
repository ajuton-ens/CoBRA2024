# Bluetooth
## Appairage de la manette de PS4
- Utiliser l'icône bluetooth sur la PI pour voir les appareils bluetooth. Pour connecter la manette il faut maintenir appuyés le bouton PS et le bouton share de la manette. La manette est en mode appairage si elle clignotte de cette manière : .. .. ..

## Bibliothèque Python
- La bibliothèque à installer est pyPS4Controller. Pour l'installer écrire dans la console de commande:
  ```pip install pyPS4Controller```
- Pour utiliser l'exemple donné par la bibliothèque :
  ```https://pypi.org/project/pyPS4Controller/1.1.1/```
- L'exemple est inutilisable tel quel, il faut changer la dernière ligne par :
  ```MyController(interface="/dev/input/js0", connecting_using_ds4drv=False).listen()```
- Il suffit de modifier les instructions présentes dans les fonctions de la classe MyController afin que celles-ci soient exécutées au moment où l'action décrite est réalisée (ex: augmenter la vitesse des moteurs lorsque la gachette gauche est appuyée)
