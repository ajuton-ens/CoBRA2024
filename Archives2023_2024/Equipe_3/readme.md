# 24/05/2024
## Caractérisation des moteurs
### Protocole expérimental
![WhatsApp Image 2024-05-24 à 12 20 04_9289effe](https://github.com/bruno2nis/cobra/assets/147141994/4054ca87-7891-4ea9-a5ca-c1d3c632abe3)
On relève la force de poussée pour différentes largeurs d'impulsions imposées.
/!\ Les mesures sont faites en statique -> peut être que le comportement dynamique diffèrera un peu
### Moteur pour la poussée horizontale
![image](https://github.com/bruno2nis/cobra/assets/147141994/b54a4cca-bf85-43ca-b628-a87d235da68a)
![WhatsApp Image 2024-05-24 à 12 17 27_020dbe35](https://github.com/bruno2nis/cobra/assets/147141994/60445831-4727-41ab-94c5-411934a1a3ae)
On peut modéliser le moteur par un gain sans trop d'erreurs.
### Moteur pour la poussée verticale
![image](https://github.com/bruno2nis/cobra/assets/147141994/68c98d25-8630-4c8d-9c76-3331c199dbf1)

Le moteur a brûlé pour une impulsion de 2000 µs. Il en a été recommandé un nouveau. Cela doit être dû à un couple trop important, qui peut venir du dimensionnement de l'hélice ou d'un frottement.
## Inventaire des masses embarquées


## Asservissement
Asservissement en vitesse pour la chaîne de propulsion horizontale.
Asservissement en position pour la chaîne de propulsion verticale.
Asservissement en position angulaire pour la chaîne de propulsion du lacet.

## Stratégies de contrôle
METTRE DES SCHEMAS
### Stratégie naïve 1
Polaire
### Stratégie naïve 2
Différence angulaire
### Autre solution
Polaire avec correction par symétrie
