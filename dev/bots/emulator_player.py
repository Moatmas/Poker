import random
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import estimate_hole_card_win_rate, gen_cards

class EmulatorPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        # Conversion des cartes en objets nécessaires
        hole_cards = gen_cards(hole_card)
        community_cards = gen_cards(round_state['community_card'])

        # Estimer la probabilité de victoire
        win_rate = estimate_hole_card_win_rate(
            nb_simulation=1000,
            nb_player=len([p for p in round_state['seats'] if p['state'] != "folded"]),
            hole_card=hole_cards,
            community_card=community_cards
        )

        # Prendre une décision en fonction de la probabilité de victoire
        if win_rate > 0.7:
            action = self._choose_action(valid_actions, "raise")
        elif win_rate > 0.3:
            action = self._choose_action(valid_actions, "call")
        else:
            action = self._choose_action(valid_actions, "fold")

        return action

    def _choose_action(self, valid_actions, action_type):
        for action in valid_actions:
            if action['action'] == action_type:
                if action_type == "raise":
                    # Déterminer le montant du raise
                    amount = random.randint(
                        action['amount']['min'], 
                        action['amount']['max']
                    )
                    return action_type, amount
                else:
                    return action_type, action.get('amount', 0)
        # Si l'action demandée n'est pas possible, effectuer l'action par défaut
        return valid_actions[0]['action'], valid_actions[0].get('amount', 0)

    def receive_game_start_message(self, game_info):
        # Initialisation au début du jeu
        self.nb_players = len(game_info['seats'])

    def receive_round_start_message(self, round_count, hole_card, seats):
        # Début d'une nouvelle manche
        self.hole_card = hole_card

    def receive_street_start_message(self, street, round_state):
        # Début d'un nouveau tour (Flop, Turn, River)
        self.current_street = street

    def receive_game_update_message(self, new_action, round_state):
        # Mise à jour de l'état du jeu suite à une action d'un autre joueur
        self.round_state = round_state

    def receive_round_result_message(self, winners, hand_info, round_state):
        # Résultats d'une manche
        self.last_winners = winners

def setup_ai():
    return EmulatorPlayer()
