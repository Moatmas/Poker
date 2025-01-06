import matplotlib.pyplot as plt
import pandas as pd
from pypokerengine.api.game import setup_config, start_poker
from bots.fish_player import FishPlayer
from bots.smart_player import SmartPlayer
from bots.cfr_player import CFRPlayer
from bots.emulator_player import EmulatorPlayer
from bots.montecarlo_player import MonteCarloPlayer

# Initialisation des bots en dehors de la fonction run_game
cfr_bot = CFRPlayer()
fish_bot = FishPlayer()
smart_bot = SmartPlayer()
emulator_bot = EmulatorPlayer()
montecarlo_bot = MonteCarloPlayer()


# Configuration initiale
def run_game(initial_stack=5000):
    config = setup_config(max_round=10, initial_stack=initial_stack, small_blind_amount=5)

    # Inscription des joueurs IA
    config.register_player(name="FishPlayer", algorithm=FishPlayer())
    config.register_player(name="SmartPlayer", algorithm=SmartPlayer())
    config.register_player(name="Cfr_player", algorithm=CFRPlayer())
    config.register_player(name="Emulator_player", algorithm=EmulatorPlayer())
    config.register_player(name="MonteCarlo_player", algorithm=MonteCarloPlayer())

    # Lancement de la partie
    game_result = start_poker(config, verbose=0)
    return game_result

# Fonction pour simuler plusieurs parties
def simulate_games(nb_games, initial_stack=5000):
    stats = {"FishPlayer": 0, "SmartPlayer": 0, "Cfr_player": 0, "Emulator_player": 0, "MonteCarlo_player": 0}
    stacks_history = {"FishPlayer": [], "SmartPlayer": [], "Cfr_player": [], "Emulator_player": [], "MonteCarlo_player": []}

    for i in range(nb_games):
        game_result = run_game(initial_stack=initial_stack)

        # Trouver le gagnant de la partie
        winner = max(game_result['players'], key=lambda p: p['stack'])
        print(f"Partie {i + 1} terminée. Gagnant: {winner['name']} avec {winner['stack']} de stack.")  # Affiche la fin de la partie

        # Mise à jour des statistiques
        for player in game_result['players']:
            stacks_history[player['name']].append(player['stack'])
            if player['stack'] == max(p['stack'] for p in game_result['players']):
                stats[player['name']] += 1

    return stats, stacks_history

# Simulation
nb_games = 20
initial_stack = 5000 
stats, stacks_history = simulate_games(nb_games, initial_stack)

# Affichage des résultats globaux
print("Nombre de victoires par bot :")
for bot, wins in stats.items():
    print(f"{bot}: {wins} victoires")

# Visualisations
# 1. Camembert des victoires
plt.figure(figsize=(8, 8))
labels = stats.keys()
sizes = stats.values()
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.tab10.colors)
plt.title("Proportion des victoires par bot")
plt.show(block=False)

# 2. Histogramme des stacks finaux
plt.figure(figsize=(10, 6))
for bot, stacks in stacks_history.items():
    plt.hist(stacks, bins=15, alpha=0.7, label=bot)
plt.title("Distribution des stacks finaux par bot")
plt.xlabel("Stack")
plt.ylabel("Fréquence")
plt.legend()
plt.show(block=False)

# 3. Boxplot des performances
plt.figure(figsize=(10, 6))
plt.boxplot([stacks_history[bot] for bot in stats.keys()], labels=stats.keys())
plt.title("Performance des bots (stacks finaux)")
plt.ylabel("Stack final")
plt.xlabel("Bot")
plt.show(block=False)

# 4. Victoires cumulatives
# cumulative_wins = {bot: [0] * nb_games for bot in stats.keys()}
# for i in range(nb_games):
#     game_result = run_game(initial_stack=initial_stack)
#     max_stack_bot = max(game_result['players'], key=lambda p: p['stack'])['name']
#     for bot in stats.keys():
#         cumulative_wins[bot][i] = cumulative_wins[bot][i-1] + (1 if bot == max_stack_bot else 0)

# plt.figure(figsize=(10, 6))
# for bot, wins in cumulative_wins.items():
#     plt.plot(wins, label=bot)
# plt.title("Évolution des victoires cumulées")
# plt.xlabel("Partie")
# plt.ylabel("Nombre de victoires")
# plt.legend()
# plt.show(block=False)

# 5. Tableau des statistiques
average_stacks = {bot: sum(stacks) / len(stacks) for bot, stacks in stacks_history.items()}
data = {
    "Bot": list(stats.keys()),
    "Victoires": list(stats.values()),
    "Stack moyen": list(average_stacks.values())
}
df = pd.DataFrame(data)
print("\nTableau récapitulatif :")
print(df)

# 6. Impact de la taille initiale des stacks
initial_stacks = [100, 500, 1000,5000]
average_wins = []

# Simulation pour différentes tailles de stacks
# for stack_size in initial_stacks:
#     if nb_games // 10 > 0:
#         stats, _ = simulate_games(nb_games // 10, initial_stack=stack_size)
#         average_wins.append([stats[bot] / (nb_games // 10) for bot in stats.keys()])
#     else:
#         print("Erreur : nb_games // 10 est égal à zéro.")

# # Vérifier si average_wins contient des données avant d'afficher le graphique
#     if average_wins:
#         plt.figure(figsize=(10, 6))
#         for i, bot in enumerate(stats.keys()):
#             plt.plot(initial_stacks, [wins[i] for wins in average_wins], label=bot)

#         plt.title("Impact de la taille des stacks initiaux sur les victoires")
#         plt.xlabel("Taille initiale des stacks")
#         plt.ylabel("Proportion de victoires")
#         plt.legend()
#         plt.show(block=False)
#     else:
#         print("Aucune donnée n'a été générée pour les victoires moyennes.")

plt.show()
