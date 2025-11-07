# Projet Cobra étude 2 
# Résolution équa diff à omega constant 

import numpy as np
import scipy.integrate as integr
import matplotlib.pyplot as plt

m = 2.73  # masse totale ballon + nacelle
rho = 1.20  # masse volumique de l'air
R = 0.582  # rayon de la coupe de face de l'enveloppe
S = np.pi * R**2  # surface du cercle de coupe de face de l'enveloppe
Cx = 0.100  # coefficient de trainée 
alpha = 5.82e-6
beta = 3.1e-4
omega_max = 640  # vitesse de rotation maximale des hélices pour une tension de 12V (en rad/s)

def f(v,t):
    return (alpha * omega_max**2)/m - (beta * omega_max * v)/m - (rho * Cx * S * v**2)/(2 * m) 

T = np.arange(0, 30, 0.01)
V = integr.odeint(f, 0, T)
P = alpha * omega_max**2 - beta * omega_max * V
Tr = (rho * Cx * S * V**2)/2
plt.plot(T, V)
plt.plot(T, P)
plt.plot(T, Tr)
plt.grid()
plt.xlabel("temps en s")
plt.ylabel("vitesse en m/s, poussée des hélices en N et force de trainée en N")
plt.show()

V_max = V[-1][0]
print("Vitesse max :",V[-1][0])

indice_t5 = np.argmax(T > 0.95 * V_max)
t5 = T[indice_t5]
print("Temps de réponse à 5% :",t5)





