import matplotlib.pyplot as plt

# Lecture des données
t1 = []
consigne = []
mesure = []

with open("test_indiciel1.txt", "r") as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) == 3:
            t1.append(float(parts[0]))
            consigne.append(float(parts[1]))
            mesure.append(float(parts[2]))

# Tracé des courbes
plt.figure(figsize=(10,5))
plt.plot(t1, consigne, label="Consigne")
plt.plot(t1, mesure, label="Mesure")
plt.xlabel("t1 (s)")
plt.ylabel("Valeur")
plt.title("Consigne et mesure en fonction du temps")
plt.legend()
plt.grid(True)
plt.show()