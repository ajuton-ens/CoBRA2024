from math import *

# simple filtre passe bas d'ordre 1 avec la fréquence de coupure "fc"
# utilisé notament pour la dérivée du PID

class PasseBas_ordre_1:
    def __init__(self, fc):

        self.fc = fc
        self.s = None
    

    def filtre1(self, e, dt):
        if self.s == None: self.s = e
   
        if self.fc:
            tau = 1 / (2 * pi * self.fc)

        alpha = dt / (tau + dt)

        self.s = self.s + alpha * (e - self.s)

        return self.s
