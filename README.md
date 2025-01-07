# Python Poker Project

Ce projet Python implémente un jeu de poker en utilisant les bibliothèques **PyPokerEngine** et **PyPokerGUI**. Vous pouvez simuler des parties de poker et personnaliser les configurations selon vos besoins.

## Installation

Avant de commencer, assurez-vous que Python est installé sur votre système. Ensuite, installez les dépendances nécessaires :

```bash
pip install PyPokerEngine
pip install PyPokerGUI
```

## Configuration du jeu

Dans le fichier `main.py`, vous pouvez modifier les paramètres de simulation en ajustant la configuration initiale. Voici un exemple :

```python
config = setup_config(max_round=10, initial_stack=initial_stack, small_blind_amount=5)
```
- **max_round** : Nombre maximum de tours dans une partie.
- **initial_stack** : Montant initial des jetons pour chaque joueur (par défaut : 5000).
- **small_blind_amount** : Montant de la petite blind.

Vous pouvez également ajuster d'autres paramètres comme :

```python
nb_games = 20
initial_stack = 5000
```

## Interface graphique

L'interface graphique est gérée par **PyPokerGUI**, ce qui permet de visualiser les parties en temps réel. Pour lancer l'interface graphique, utilisez la commande suivante :

```bash
pypokergui serve /Users/User/Desktop/Poker/poker_conf.yaml --port 8000 --speed fast
```
- **--port** : Spécifie le port sur lequel le serveur sera lancé (par défaut : 8000).
- **--speed** : Contrôle la vitesse de la simulation (options : `fast`, `normal`, `slow`).

## Exécution du projet

Pour exécuter le projet, utilisez la commande suivante :

```bash
python main.py
```

Assurez-vous que les bibliothèques nécessaires sont installées et que votre configuration est correcte.
