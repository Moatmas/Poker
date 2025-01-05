from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
from pypokerengine.utils.game_state_utils import restore_game_state
import random

class RLPlayer(BasePokerPlayer):
    def __init__(self):
        self.q_table = {}  # Une table Q pour stocker les valeurs des actions
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.exploration_rate = 1.0  # Commencer avec une exploration maximale
        self.exploration_decay = 0.995

    # Setup de l'Emulator pour la simulation
    def receive_game_start_message(self, game_info):
        player_num = game_info["player_num"]
        max_round = game_info["rule"]["max_round"]
        small_blind_amount = game_info["rule"]["small_blind_amount"]
        ante_amount = game_info["rule"]["ante"]
        blind_structure = game_info["rule"]["blind_structure"]
        
        self.emulator = Emulator()
        self.emulator.set_game_rule(player_num, max_round, small_blind_amount, ante_amount)
        self.emulator.set_blind_structure(blind_structure)
        
        # Enregistrer chaque joueur (ici, un modèle simple pour la simulation)
        for player_info in game_info["seats"]["players"]:
            self.emulator.register_player(player_info["uuid"], SmartPlayer())  # Utiliser un joueur basique pour l'opposant

    # Déclarer une action (basée sur la stratégie d'exploration/exploitation)
    def declare_action(self, valid_actions, hole_card, round_state):
        state = self.get_state(hole_card, round_state)  # Extraire l'état du jeu
        action = self.choose_action(state, valid_actions)
        amount = valid_actions[2]["amount"] if action == "raise" else 0
        return action, amount

    # Choisir une action basée sur l'exploration/exploitation
    def choose_action(self, state, valid_actions):
        if random.random() < self.exploration_rate:
            return random.choice(valid_actions)["action"]  # Exploration (choisir une action aléatoire)
        else:
            return self.best_action(state)  # Exploitation (choisir la meilleure action selon la Q-table)

    # Trouver la meilleure action selon la Q-table
    def best_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0] * len(self.num_actions)  # Initialiser les Q-values si elles n'existent pas encore
        return max(range(len(self.num_actions)), key=lambda a: self.q_table[state][a])

    # Calculer l'état actuel du jeu
    def get_state(self, hole_card, round_state):
        # Par exemple, tu pourrais simplement utiliser l'évaluation de la main et la taille du pot
        hand_strength = self.evaluate_hand(hole_card, round_state)
        pot_size = round_state['pot']['total']
        return (hand_strength, pot_size)

    # Évaluer la main (pour simplification)
    def evaluate_hand(self, hole_card, round_state):
        card_ranks = [card[0] for card in hole_card]
        if "A" in card_ranks:
            return 0.8  # Forte main avec As
        elif len(set(card_ranks)) == 1:
            return 0.6  # Paire
        else:
            return 0.4  # Main faible

    # Mise à jour de la Q-table après chaque action
    def update_q_table(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = [0] * len(self.num_actions)
        if next_state not in self.q_table:
            self.q_table[next_state] = [0] * len(self.num_actions)

        # Calculer la valeur maximale de l'action suivante
        future_q_value = max(self.q_table[next_state])
        
        # Mise à jour de la Q-value pour l'état actuel
        self.q_table[state][action] = (1 - self.learning_rate) * self.q_table[state][action] + self.learning_rate * (reward + self.discount_factor * future_q_value)

    def receive_round_result_message(self, winners, hand_info, round_state):
        for hand in hand_info:
            reward = 1 if hand['player'] in winners else -1  # Récompense simple
            state = self.get_state(hand['hole_card'], round_state)
            next_state = self.get_state(hand['hole_card'], round_state)
            self.update_q_table(state, action, reward, next_state)  # Mise à jour de la Q-table après chaque main

    # Réduire progressivement le taux d'exploration
    def decay_exploration_rate(self):
        self.exploration_rate *= self.exploration_decay

# Fonction de configuration
def setup_ai():
    return RLPlayer()
