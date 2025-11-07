# Info 2024/25

Pour désactiver la sortie 5 volts de la carte Raspberry pi 5

Ouvrir le fichier config.txt: sudo nano /boot/firmware/config.txt

Ajouter la igne suivante :
PSU_MAX_CURRENT=5000
