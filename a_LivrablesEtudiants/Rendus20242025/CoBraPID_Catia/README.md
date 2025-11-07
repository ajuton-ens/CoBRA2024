# Remarques sur le contenu de ce dossier

Globalement, j'y ai mis les principaux fichiers nécessaires pour faire la propulsion du dirigeable. Certains manquent, comme le fichier Eagle de la carte électronique et le schéma de branchement, mais sont déjà sur le GitHub. J'ai tout modélisé sur Fusion360 donc j'ai mis les fichiers mais j'imagine que vous ne les utiliserez pas. Je n'ai mis que les fichiers aboutis, sauf le fichier principal du programme python qui fait fonctionner le dirigeable : c'est Victor qui a l'intégralité des dépendances et bibliothèques qu'il a utilisées/crées sur ROS2 sur une carte TF donc je n'ai mis que ma version de travail du programme ("main version de travail.py"). 

Vous y trouverez :

- **Le dossier "Impression"** qui contient uniquement et intégralement les fichiers stl de la structure. Quelques remarques et pistes d'amélioration :
  - "Supports moteurs bas rework.stl" est de mauvaise conception : l'hélice est trop proche de l'enveloppe et l'effet de peau fait que l'hélice aspire même en soufflant dans le bon sens. Sinon la structure est robuste et très très légère. J'ai modélisé une version améliorée mais je ne l'ai pas imprimée et donc pas testée...
  - "Supports moteurs bas.stl" est correct mais légèrement fragile selon moi et nécessiterait de mettre un cercle autour des hélices pour protéger l'utilisateur
  - "support pi cam inclinée.stl" n'a finalement pas été  utilisé puisque nous avons choisi de ne pas mettre de caméra inclinée (il était prévu d'en mettre une avec un angle de 35°)
- **Les dossiers "catia treuil AG" et "pince"** contiennent les fichiers CATIA des pièces pour la pince et le treuil. Ces pièces ont été modélisées par Ulises et Antoine Gallissian
- J'ai fourni notre poster qui contient quelques schémas et des indications utiles
- "cobra_TFLUNA_v03.py" est une version de test fonctionnelle du TFLUNA. La fonction peut être implémentée telle quelle
- "main version travail.py" : comme je disais, j'avais fait une copie du programme qui tourne pendant le fonctionnement du ballon pour travailler dessus avant d'effectuer les modifications dans le code de la raspberry (pour travailler chez moi et à cause des limites du tunnel ssh). C'est donc une version temporaire qui ne fonctionne pas forcément (je ne me souviens plus) mais qui donne 99% du fonctionnement global de la boucle 
- J'ai inclus aussi le dessin technique de la caméra raspberry utilisée (afin de la modéliser sur le fichier 3D) et la "documentation" (très incomplète et imprécise) du driver du moteur brushless.

Amusez-vous bien sur le meilleur projet de Saphire ! 😀 