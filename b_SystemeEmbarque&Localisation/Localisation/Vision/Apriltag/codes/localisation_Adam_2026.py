from XYZ_Adam import Localisation
import time
from datetime import datetime

listePointsAtrium = {
    20: (0.0, 5.0, 0.0), 21: (1.0, 5.0, 0.0), 22: (2.0, 5.0, 0.0), 23: (3.0, 5.0, 0.0),
     4: (0.0, 4.0, 0.0),  9: (1.0, 4.0, 0.0), 14: (2.0, 4.0, 0.0), 19: (3.0, 4.0, 0.0),
     3: (0.0, 3.0, 0.0),  8: (1.0, 3.0, 0.0), 13: (2.0, 3.0, 0.0), 18: (3.0, 3.0, 0.0),
     2: (0.0, 2.0, 0.0),  7: (1.0, 2.0, 0.0), 12: (2.0, 2.0, 0.0), 17: (3.0, 2.0, 0.0),
     1: (0.0, 1.0, 0.0),  6: (1.0, 1.0, 0.0), 11: (2.0, 1.0, 0.0), 16: (3.0, 1.0, 0.0),
     0: (0.0, 0.0, 0.0),  5: (1.0, 0.0, 0.0), 10: (2.0, 0.0, 0.0), 15: (3.0, 0.0, 0.0),
}

# Le bloc ci-dessous ne s'exécute QUE si on lance ce fichier directement.
# Il ne s'exécute pas si un autre script fait `from localisation_Adam import listePointsAtrium`.
if __name__ == "__main__":
    localisation = Localisation(listePointsAtrium)
    t_start = time.time()
    nom_fichier = f"essai_{datetime.now().strftime('%m%d_%H%M')}.txt"
    fichier = open(nom_fichier, "a")
    fichier.write("\n\n# Nouvel essai\n\n")

    while time.time() - t_start < 30:
        t = time.time()
        mes = localisation.mesure()
        if mes is not None:
            print(f"t={t-t_start:.3f}  pos={mes[2]}  conf={mes[4]}")
            conf_str = ";".join([f"{id_t}:{p}" for id_t, p in mes[4]])
            ligne = f"{t-t_start},{mes[0][0]},{mes[0][1]},{mes[0][2]},{mes[1][0]},{mes[1][1]},{mes[1][2]},{mes[2][0]},{mes[2][1]},{mes[2][2]},{mes[3][0]},{mes[3][1]},{mes[3][2]},{conf_str}"
        else:
            print(f"t={t-t_start:.3f}s  aucun tag")
            ligne = f"{t-t_start}"
        fichier.write(ligne + "\n")

    fichier.close()
