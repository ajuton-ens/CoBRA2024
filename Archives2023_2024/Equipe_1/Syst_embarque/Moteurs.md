# Documentation de l'équipe 1 pour l'utilisation des moteurs

## Servo-moteurs

Un servo moteur est défini par plusieurs paramètres :
- angles : `[angle_max, angle_repos, angle_min]`
- les instructions PWM associées  : `[pwm_max, pwm_repos, pwm_min]`
- le channel de connection : `int : c`

Attention : l'index  de la position `1` sur les boards est souvent le channel `0` !!

On définit plusieurs fonctions pour le servo :
#### `calculate_imp(angle)`

Permet de calculer la largeur d'impulsion à envoyer pour atteindre la position demandée. Les valeurs limites `angle_max` et `angle_min` entrées lors de la définition servent de bornes pour éviter d'abimer le servo.

#### `set_angle(angle)`

Permet d'envoyer la commande pwm au servo via le channel associé.
Une conversion liée à la bibliothèque `adafruit_servokit` est alors nécessaire.

## Moteurs brushless

Un moteur brushless est défini par plusieurs paramètres :
- les instructions PWM associées aux vitesses max et min  : `[pwm_max, pwm_min]`
- le channel de connection : `int : c`

Le moteur est commandé en vitesse entre `0` (min) et `1` (max).
Les valeurs de pwm calculées seront comprises entre 1000 µs et 2000 µs.

#### `initialisation()`

Il est nécessaire d'initialiser les ESC au démarrage. On envoit donc pendant quelques secondes une commande d'impulsion nulle (`pwm = 1000`). Le delay n'est pas placé dans cette fonction mais doit être pris en compte dans le script global.

#### `calculate_imp(speed)`

Permet de calculer la largeur d'impulsion à envoyer pour atteindre la vitesse demandée. Les valeurs limites `0` et `1`servent de bornes pour éviter d'abimer le moteur ou l'ESC.

#### `set_speed(speed)`

Permet d'envoyer la commande pwm à l'ESC via le channel associé.
Une conversion liée à la bibliothèque `adafruit_servokit` est alors nécessaire.



## Machine à courant continue

La MCC possède 2 sens de rotation et est commandée comme un moteur brushless. Il y a donc 2 plages de valeurs à définir :
- sens positif : `forward` entre `0` et `1`
- sens invers : `backward` entre `0` et `-1`

Une MCC est défini par plusieurs paramètres :
- les instructions PWM associées aux vitesses max et min  : `[pwm_max_forw, pwm_min_forw, pwm_min_back, pwm_max_back]`
- le channel de connection : `int : c`

Les plages de valeurs en pwm seront comprises entre 1000 µs et 2000 µs et une zone morte est construite dans l'ESC commandant la MCC autour de 1550 µs.

Le moteur est commandé en vitesse entre `0` (min) et `1` (max).

#### `initialisation()`

Il est nécessaire d'initialiser les ESC au démarrage. On envoit donc pendant quelques secondes une commande d'impulsion nulle (`pwm = 1550` pour la MCC). Le delay n'est pas placé dans cette fonction mais doit être pris en compte dans le script global.

#### `calculate_imp(speed)`

Permet de calculer la largeur d'impulsion à envoyer pour atteindre la vitesse demandée. Les valeurs limites `0`, `1` et `-1` servent de bornes pour éviter d'abimer le moteur ou l'ESC.

#### `set_speed(speed)`

Permet d'envoyer la commande pwm à l'ESC via le channel associé.
Une conversion liée à la bibliothèque `adafruit_servokit` est alors nécessaire.

#### `stop()`

Envoit comme consigne la valeur `pwm = 1550` pour un arrêt du moteur (zone morte de l'ESC).
