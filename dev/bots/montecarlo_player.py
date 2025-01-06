import random
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card
from pypokerengine.engine.card import Card

class MonteCarloPlayer(BasePokerPlayer):

    def declare_action(self, valid_actions, hole_card, round_state):
        # Conversion des cartes en objets nécessaires
        hole_cards = gen_cards(hole_card)
        community_cards = gen_cards(round_state['community_card'])

        # Estimer la probabilité de victoire avec la méthode Monte Carlo
        win_rate = self.estimate_win_rate(
            nb_simulation=500,
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

    def estimate_win_rate(self, nb_simulation, nb_player, hole_card, community_card):
        win_count = sum([self._montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
        return 1.0 * win_count / nb_simulation

    def _montecarlo_simulation(self, nb_player, hole_card, community_card):
        # Remplir les cartes communautaires si nécessaire
        community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
        unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
        
        # Distribuer des cartes aux autres joueurs
        opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
        
        # Calculer les scores des adversaires
        opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
        
        # Calculer le score du bot
        my_score = HandEvaluator.eval_hand(hole_card, community_card)
        
        # Retourner si le bot gagne
        return 1 if my_score >= max(opponents_score) else 0

    def _fill_community_card(self, base_cards, used_card):
        need_num = 5 - len(base_cards)
        return base_cards + _pick_unused_card(need_num, used_card)

    def _pick_unused_card(self, card_num, used_card):
        used = [card.to_id() for card in used_card]
        unused = [card_id for card_id in range(1, 53) if card_id not in used]
        choiced = random.sample(unused, card_num)
        return [Card.from_id(card_id) for card_id in choiced]

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
    return MonteCarloPlayer()
