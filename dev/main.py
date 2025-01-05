from pypokerengine.api.game import setup_config, start_poker
from bots.fish_player import FishPlayer
from bots.smart_player import SmartPlayer
from bots.cfr_player import CFRPlayer 
from bots.rl_player import RLPlayer
from bots.emulator_player import EmulatorPlayer
# Configuration de la partie
config = setup_config(max_round=10, initial_stack=300, small_blind_amount=5)

# Inscription des joueurs IA
config.register_player(name="FishPlayer", algorithm=FishPlayer())
config.register_player(name="SmartPlayer", algorithm=SmartPlayer())
config.register_player(name="Cfr_player", algorithm=CFRPlayer())
config.register_player(name="Emulator_player", algorithm=EmulatorPlayer())





# Lancement de la partie
game_result = start_poker(config, verbose=1)

# Affichage des résultats
print("Résultat de la partie :")
print(game_result)
print("Résultat de la partie :\n")

# Extraction des stacks finaux
for player in game_result['players']:
    print(f"Joueur: {player['name']} | Stack final: {player['stack']}")

# Déterminer le gagnant
gagnant = max(game_result['players'], key=lambda p: p['stack'])
print(f"\nLe gagnant est {gagnant['name']} avec {gagnant['stack']} jetons.")

