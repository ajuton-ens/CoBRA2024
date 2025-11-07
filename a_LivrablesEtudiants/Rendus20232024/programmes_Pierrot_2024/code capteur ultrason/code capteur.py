import RPi.GPIO as GPIO
import time
 
# Module GPIO: BOARD ou BCM (numérotation comme la sérigraphie de la carte ou comme le chip) #
GPIO.setmode(GPIO.BCM) 
 
# Définition des broches GPIO #
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Définition des broches en entrées ou en sortie #
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
 
def distance():
    # Mise à l'état haut de la broche Trigger #
    GPIO.output(GPIO_TRIGGER, True)
 
    # Mise à l'état bas de la broche Trigger aprés 10 µS #
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # Enregistrement du temps de départ des ultrasons #
    while GPIO.input(GPIO_ECHO) == 0:
        pass
 
    # Enregistrement du temps d'arrivés des ultrasons #
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # Calcul de la durée de l'aller-retour des US #
    TimeElapsed = StopTime - StartTime
    # On multiplue la durée par la vitesse du son: 34300 cm/s #
    # et on divise par deux car il s'agit d'un aller et retour. #
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 
if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print("Distance mesurée = %.1f cm" % dist)
            time.sleep(1)
 
        # On reset le programme via CTRL+C #
    except KeyboardInterrupt:
        print("Mesure stoppée")
        GPIO.cleanup()
