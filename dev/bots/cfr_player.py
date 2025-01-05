import random
from collections import defaultdict
from pypokerengine.players import BasePokerPlayer
import json


class CFRPlayer(BasePokerPlayer):
    
    def __init__(self):
        self.regrets = defaultdict(float)
        self.strategy = defaultdict(float)
        self.opp_strategy = defaultdict(float)
        self.num_actions = 3  # Fold, Call, Raise
    
    def declare_action(self, valid_actions, hole_card, round_state):
        hand_strength = self.evaluate_hand(hole_card, round_state)
        print(f"Hand strength: {hand_strength}")
        
        # Simuler un choix basé sur la stratégie apprise
        strategy = self.get_strategy(hole_card, round_state)
        action = self.sample_action(strategy)
        
        # Si la main est forte, choisir "raise" plus souvent
        if hand_strength > 0.7:
            if "raise" in valid_actions:
                action = "raise"
            else:
                action = "call"
        
        return action, 10  # Mise par défaut

    
    def cfr_round(self, hole_card, round_state):
        # Vérifier la structure de round_state['pot']
        print(round_state)
        print(round_state['pot'])

        # Supposons que round_state['pot'] soit un dictionnaire avec une clé 'total'
        if isinstance(round_state['pot'], dict) and 'total' in round_state['pot']:
            pot_value = round_state['pot']['total']
            amount = pot_value * 0.5
        else:
            # Gérer le cas où round_state['pot'] n'est pas dans le format attendu
            amount = 10  # Valeur par défaut

        # Retourner l'action et le montant
        return "raise", amount

    
    def get_strategy(self, hole_card, round_state):
        # Convertir hole_card en tuple pour le rendre immuable
        hole_card_tuple = tuple(hole_card)
        
        # Convertir round_state en une chaîne JSON pour le rendre immuable
        round_state_str = json.dumps(round_state, sort_keys=True)
        
        # Calculer la stratégie du joueur (utilise les regrets passés pour mettre à jour la stratégie)
        strategy = [max(0, self.regrets[(hole_card_tuple, round_state_str, a)]) for a in range(self.num_actions)]
        sum_of_strategy = sum(strategy)
        
        # Si la somme de la stratégie est positive, normaliser, sinon, retourner une stratégie uniforme
        if sum_of_strategy > 0:
            strategy = [s / sum_of_strategy for s in strategy]
        else:
            # Ajout d'une probabilité de raise plus forte
            strategy = [0.33, 0.33, 0.34]  # Fold, Call, Raise - ajuster selon les préférences du jeu
        
        return strategy




    
    def sample_action(self, strategy):
        # Choisir une action selon la probabilité définie par la stratégie
        rand = random.random()
        cumulative_prob = 0.0
        for action, prob in enumerate(strategy):
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return ["fold", "call", "raise"][action]
        return "fold"  # Défaut en cas de problème

    def update_regrets(self, action, reward, hole_card, round_state):
        # Calculer les regrets pour une action spécifique
        strategy = self.get_strategy(hole_card, round_state)
        total_reward = sum([strategy[i] * reward for i in range(self.num_actions)])
        for a in range(self.num_actions):
            if a == action:
                regret = reward - total_reward
            else:
                regret = -strategy[a] * reward
            self.regrets[(hole_card, round_state, a)] += regret


    def evaluate_hand(self, hole_card, round_state):
        card_ranks = [card[0] for card in hole_card]  
        card_suits = [card[1] for card in hole_card]
        
        # Logique simple d'évaluation
        if "A" in card_ranks and "K" in card_ranks:
            return 0.9  # Main très forte (exemple)
        elif len(set(card_ranks)) == 1:
            return 0.6  # Paires
        elif "A" in card_ranks:
            return 0.7  # As + autre carte
        else:
            return 0.4  # Autres mains plus faibles

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        for hand in hand_info:
            print(hand)  # Affiche la structure complète de 'hand'
            if 'action' in hand:
                # Exemple basique de calcul de récompense
                reward = 1 if hand['player'] in winners else -1
                self.update_regrets(hand['action'], reward, hand['hole_card'], round_state)
            else:
                print("Key 'action' not found in hand:", hand)



def setup_ai():
    return CFRPlayer()
