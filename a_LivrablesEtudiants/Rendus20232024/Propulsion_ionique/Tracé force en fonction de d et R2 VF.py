
import numpy as np
import matplotlib.pyplot as plt

R_petit = 50*10**-6 # rayon fil

R_grand = np.linspace(10**-4,10**-2,1000 ) # Rayon tube

eps0=8.85*10**(-12) 

d=np.linspace(10**-2,3*10**-2,10) #distance entre electrode
C=[] #capa
e=[] # energie
V=20*10**3 # tension
L = 1 # longueur tubes et fils

# for i in range(len(R_grand)):
#     C.append( (2*np.pi*eps0) / ( np.log( (d-R_grand[i])*(d-R_petit) / (R_petit*R_grand[i])  ))) 
#     e.append( 0.5*C[i]*V**2)
    
# plt.plot(R_grand,C)
# plt.legend(['Capacité en fonction du Rayon'])
# plt.show()

# plt.plot(R_grand,e)
# plt.legend(['énergie en fonction du Rayon'])
# plt.show()



### Force :
Cd = 1 #coef trainé
mub = 2 * 10 ** -4 #mobilité ion
A = 2 * 10**-23 #surface transversale electron
I = 1*10 **-3
V = 20 * 10**3
phi0 = 6 *10**3
eps0=8.85*10**-12


##variable de test
beta = 1

##

cte = I*Cd/mub
FD=[]
FEHD=[]
S_grand=np.pi*R_grand*L
Legend=[]

for i in range(len(d)):
    fd=[]
    fehd=[]
    lc=0
    for j in range(len(R_grand)):
        lc= 10 + (d[i]-10)*beta
        
        fd.append( cte * S_grand[j]*d[i] )
        fehd.append( (9*eps0*d[i]*(V - phi0)**2 ) / (8*lc**2))
        
    FD.append(fd)
    FEHD.append(fehd)
    plt.plot(R_grand*10**3,(np.array(fehd) - np.array(fd))*10**3 )
    
    Legend.append('d={:.0f} mm'.format(d[i]*10**3))

plt.legend(Legend)
plt.xlabel('Rayon grosse eleectrode en mm')
plt.ylabel('Poussé en mN / m')

plt.show()
