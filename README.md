# Projet RPC

Auteur: Camile Skalli

## Description

Vous êtes responsable de la logistique au Service d′Acheminement National dédié au Trans-
port d′Articles de la Compagnie Logistique Aérienne Ultra Spéciale. Vous disposez de plusieurs
véhicules spécialisés (Technologies de Roulage Avancées, Innovantes et Novatrices pour En-
gins Autonomes Urbains) de capacités différentes et d′une liste d′articles à livrer à différentes
adresses. Votre objectif est d′optimiser la répartition des colis dans les véhicules pour minimiser
le nombre de véhicules utilisés tout en respectant les capacités de charge maximale de chaque
véhicules.

La description complète du projet est disponible sur Moodle [sujet.pdf](https://moodle.epita.fr/course/view.php?id=2188).

## Outils

Ce répertoire contient les outils suivants :
- `generate.py` : générateur de données d’entrée
- `visualize.py` : visualisateur de données de sortie
- `cp.py` : solveur basé sur la méthode CP-SAT.

### `generate.py`

Permet de gérénérer des données d'entrée pour le projet pour les trois leagues (bronze, silver et gold).

Utiliser la commande :

```bash
python3 generate.py --help
```

Pour voir comment l’utiliser.

### `visualize.py`

Permet de visualiser les données de sortie du projet.

Utiliser la commande :

```bash
python3 visualize.py --help
```

Pour voir comment l’utiliser.

### `cp.py` 

Permet de résoudre le problème d'optimisation de répartition logistique en utilisant une approche CP-SAT.

#### Format attendu pour l'entrée

Le fichier d'entrée doit contenir :

- Première ligne : Les dimensions du camion (L W H).
- Deuxième ligne : Le nombre d'articles (N).
- Lignes suivantes : Les dimensions de chaque article (L2 W2 H2) suivies d'un ordre de livraison (D) avec D=-1 si il n'y a pas d'ordre.

#### Format produit pour la sortie

- SAT si une solution est trouvée, ou UNSAT si aucune solution n'existe.
- Une ligne par article dans l'ordre de l'entrée, contenant : L'identifiant du véhicule (v). Les coordonnées (x0, y0, z0) du coin le plus proche de l'origine. Les coordonnées (x1, y1, z1) du coin opposé.

Utiliser la commande :

```bash
python3 cp.py input.txt output.txt
```

Pour lancer cette méthode.

