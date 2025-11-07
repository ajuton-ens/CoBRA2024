import socket
import json
import matplotlib.pyplot as plt
from collections import deque


plt.ion() 
fig, ax = plt.subplots()
max_points = 100 


x_vals = deque(maxlen=max_points)
y_vals = deque(maxlen=max_points)
z_vals = deque(maxlen=max_points)
t_vals = deque(maxlen=max_points)

line_x, = ax.plot([], [], label='x', color='red')
line_y, = ax.plot([], [], label='y', color='green')
line_z, = ax.plot([], [], label='z', color='blue')

ax.set_ylim(-180, 180)  
ax.set_xlim(0, max_points)
ax.legend()





adresse_socket_serveur = ("192.168.1.224", 65432)  
socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket_client.connect(adresse_socket_serveur)
print("Client connecté au serveur")

i = 0
while True:
    try:
        donnees_recues = socket_client.recv(4096).decode("utf-8")
        if donnees_recues:
            donnees = json.loads(donnees_recues)


            # x_vals.append(donnees['x'])
            # y_vals.append(donnees['y'])
            # z_vals.append(donnees['z'])
            x_vals.append(donnees['pitch'])
            y_vals.append(donnees['roll'])
            z_vals.append(donnees['heading'])
            t_vals.append(i)
            i += 1


            line_x.set_data(t_vals, x_vals)
            line_y.set_data(t_vals, y_vals)
            line_z.set_data(t_vals, z_vals)

            ax.set_xlim(max(0, i - max_points), i)
            ax.relim()
            ax.autoscale_view(True, True, False)

            plt.pause(0.01)
    except KeyboardInterrupt:
        print("Interruption par l'utilisateur")
        break
    except Exception as e:
        print(f"Erreur : {e}")
        break

socket_client.close()
print("Connexion fermée")
