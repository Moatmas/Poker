from pypokerengine.players import BasePokerPlayer

class SmartPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        hand_strength = self.evaluate_hand(hole_card, round_state)
        
        if hand_strength < 0.3:
            action = "fold"
        elif hand_strength > 0.7:
            action = "raise"
            amount = valid_actions[2]["amount"]
        else:
            action, amount = valid_actions[1]["action"], valid_actions[1]["amount"]
        
        return action, amount

    def evaluate_hand(self, hole_card, round_state):
        # hole_card est une liste de chaînes de caractères (par exemple, ["2H", "AS"])
        card_ranks = [card[0] for card in hole_card]  # Premier caractère de chaque carte
        card_suits = [card[1] for card in hole_card]  # Deuxième caractère de chaque carte
        
        # Exemple de logique simple pour évaluer une main
        if "A" in card_ranks:
            return 0.8  # Forte main avec As
        elif len(set(card_ranks)) == 1:  # Paire
            return 0.6
        else:
            return 0.4

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass
def setup_ai():
    return SmartPlayer()