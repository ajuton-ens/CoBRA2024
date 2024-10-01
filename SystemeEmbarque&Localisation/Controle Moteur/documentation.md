# COMMANDE DES MOTEURS AVEC UNE RAPSBERRY PI
## Bibliothèque
### Idée
La bibliothèque que nous avons écrite se base sur la bibliothèque adafruit_servokit. 
Elle introduit la grandeur throttle (thr) variant de -1 à 1, correspondant à une largeur d'impulsion entre 720µs et 2170µs.
En effet, c'est par largeur d'impulsion que sont commandés les actionneurs (servo-moteurs ou variateurs-moteurs).\
![doc](https://github.com/bruno2nis/cobra/assets/147141994/01f9eb00-a285-41cd-b173-7381aed1cdec)

### Implémentation
- Classe élémentaire
```
Actionneur(type, pin)              
  pulse_width_to_thr(self, pw)     #convertit une largeur d'impulsion en throttle
  set_pulse_width(self, pw)        #envoie sur le pin de l'actionneur un signal de commande de largeur d'impulsion pw
```
- Calsses héritées
```
Servo(caract, pin)                 #caract est une suite associant les angles max, repos et min à leurs largeurs d'impulsions: [[anglemax, anglerepos, anglemin], [pwmax, pw0, pwmin]]
  commande_angle(self, angle)      #envoie sur le pin de l'actionneur un signal de commande correspondant à l'angle demandé /!\ dépend de la caractéristique caract
```
```
MCC(caract, pin)                   #caract est une suite associant les puissances max, limites et min à leurs largeurs d'impulsions: [[1, 0, 0, -1], [pwmax, pwlim1, pwlim2, pwmin]]
  commande_puissance(self, puis)  #envoie sur le pin de l'actionneur un signal de commande correspondant à la puissance demandée /!\ dépend de la caractéristique caract
```
```
Brushless(caract, pin)             #caract est une suite associant les puissances max et repos à leurs largeurs d'impulsions: [[1, 0], [pwmax, pw0]]
  commande_puissance(self, puis)  #envoie sur le pin de l'actionneur un signal de commande correspondant à la puissance demandée /!\ dépend de la caractéristique caract
``` 
## Caractérisation des moteurs et variateurs
### Pierrot et Damien
| Moteur                          | Angles(°)/Throttles      | Pulse Width (μs)             |
| :--------                       | :-----------------:      | ---------------:             |
| HS-225BB                        | [270, 0, -90]            | [1840, 1107, 857]            |
| Brushless + Var (hobbywing)     | [1, 0]                   | [1539, 1024]              (1)|
| MCC + Var                       | [1, 0, 0, -1]            | [1829, 1525, 1453, 1112]  (2)|

### Moteur 1
| Moteur                          | Throttles                | Pulse Width (μs)             |
| :--------                       | :-----------------:      | ---------------:             |
| Brushless + Var (hobbywing)     | [1, 0]                   | [2000, 1045]              (1)|

### Moteur 2
| Moteur                          | Throttle                 | Pulse Width (μs)             |
| :--------                       | :-----------------:      | ---------------:             |
| Brushless + Var (hobbywing)     | [1, 0]                   | [2000, 1150]              (1)|

### Moteur 3
| Moteur                          | Throttle                 | Pulse Width (μs)             |
| :--------                       | :-----------------:      | ---------------:             |
| Brushless + Var (hobbywing)     | [1, 0]                   | [2000, 1150]              (1)|

### Moteur 4
| Moteur                          | Throttle                 | Pulse Width (μs)             |
| :--------                       | :-----------------:      | ---------------:             |
| Brushless + Var (hobbywing)     | [1, 0]                   | [2000, 1150]              (1)|

- (1) Plage de poussée [0%, 100%] -> pwmin en limite du seuil
- (2) Plage de poussée [-100%, 100%] -> présence d'une zone de seuil où le moteur ne tourne pas -> pwlim1 et pwlim2
