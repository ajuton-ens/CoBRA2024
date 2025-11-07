import time
import numpy as np
import lib_moteurs_capteurs as lib

ESCchiant = [[2000, 1150], [1, 0]]
MCCchiant = [[1829, 1525, 1520, 1112], [1, 0, 0, -1]]

alt_mot = lib.brushless(lib.BRUSHLESS, 1, 6)
alt_mot.set_pulse_width(1000)
av_mot = lib.brushless(ESCchiant, 0, 5)
av_mot.set_pulse_width(1000)
lac_mot = lib.MCC(MCCchiant, 2)
lac_mot.set_pulse_width(1000)

capt = lib.capteurs()

x, y = 0, 0
x_prec, y_prec = 0, 0
dt = 0.1
vit_x, vit_y = 0, 0



def commande_altitude(consigne):
	commande = (consigne - capt.get()[0])/50
	return 1 if commande >= 1 else 0 if commande <= 0 else commande

k = 0.3
def commande_lacet(consigne):
    commande = k * (consigne - capt.get()[4])/30
    return k if commande >= k else k if commande <= k else commande


def ligne_droite(p_mot_av, consigne_alt, consigne_lac):
    quit = False
    av_mot.commande_puissance(p_mot_av)
    t0 = time.time()
    while not quit:
        #alt_mot.commande_puissance(commande_altitude(consigne_alt))
        lac_mot.commande_puissance(commande_lacet(consigne_lac))
        if time.time()-t0 > 20:
            quit = True
    av_mot.commande_puissance(0)

