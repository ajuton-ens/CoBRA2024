# Utilisation du BME280
 - Damien Chevalier
## Description du capteur
Le BME280 est un capteur d'humidité, pression et température pouvant donc être utilisé comme altimètre (à 30cm près). Il peut être connecté en I2C (adresse 0x76)
Les données renvoyées par le capteur ne sont que des indicateurs des grandeurs physiques mesurées, et il est nécessaire de réaliser une correction afin d'obtenir les données réelles. Les corrections à réaliser sont expliquées dans la datasheet, ainsi que les différentes adresses mémoire.

