import random
import json
from collections import defaultdict
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.hand_evaluator import HandEvaluator
from pypokerengine.utils.card_utils import _pick_unused_card, _fill_community_card
from pypokerengine.engine.card import Card


class HybridPlayer(BasePokerPlayer):
    
    def __init__(self):
        self.regrets = defaultdict(float)
        self.num_actions = 3  # Fold, Call, Raise

    def declare_action(self, valid_actions, hole_card, round_state):
        # Estimation hybride (CFR + Monte Carlo)
        strategy = self.get_hybrid_strategy(hole_card, round_state)
        action = self.sample_action(strategy)
        return self._choose_action(valid_actions, action)

    def get_strategy(self, hole_card, round_state):
        hole_card_tuple = tuple(hole_card)
        round_state_str = json.dumps(round_state, sort_keys=True)
        strategy = [max(0, self.regrets[(hole_card_tuple, round_state_str, a)]) for a in range(self.num_actions)]
        sum_of_strategy = sum(strategy)

        if sum_of_strategy > 0:
            strategy = [s / sum_of_strategy for s in strategy]
        else:
            strategy = [1 / self.num_actions] * self.num_actions
        return strategy

    def get_monte_carlo_strategy(self, hole_card, round_state):
        win_rate = self.estimate_win_rate(
            nb_simulation=500,  # Nombre réduit pour accélérer
            nb_player=len([p for p in round_state['seats'] if p['state'] != "folded"]),
            hole_card=gen_cards(hole_card),
            community_card=gen_cards(round_state['community_card'])
        )
        if win_rate > 0.7:
            return [0.1, 0.2, 0.7]  # Fold, Call, Raise
        elif win_rate > 0.3:
            return [0.3, 0.5, 0.2]
        else:
            return [0.7, 0.2, 0.1]

    def get_hybrid_strategy(self, hole_card, round_state):
        cfr_strategy = self.get_strategy(hole_card, round_state)
        monte_carlo_strategy = self.get_monte_carlo_strategy(hole_card, round_state)
        weight_cfr = 0.6
        weight_mc = 0.4
        return [
            weight_cfr * cfr + weight_mc * mc
            for cfr, mc in zip(cfr_strategy, monte_carlo_strategy)
        ]

    def estimate_win_rate(self, nb_simulation, nb_player, hole_card, community_card):
        win_count = sum([self._montecarlo_simulation(nb_player, hole_card, community_card) for _ in range(nb_simulation)])
        return 1.0 * win_count / nb_simulation

    def _montecarlo_simulation(self, nb_player, hole_card, community_card):
        community_card = _fill_community_card(community_card, used_card=hole_card + community_card)
        unused_cards = _pick_unused_card((nb_player - 1) * 2, hole_card + community_card)
        opponents_hole = [unused_cards[2 * i:2 * i + 2] for i in range(nb_player - 1)]
        opponents_score = [HandEvaluator.eval_hand(hole, community_card) for hole in opponents_hole]
        my_score = HandEvaluator.eval_hand(hole_card, community_card)
        return 1 if my_score >= max(opponents_score) else 0

    def sample_action(self, strategy):
        rand = random.random()
        cumulative_prob = 0.0
        for action, prob in enumerate(strategy):
            cumulative_prob += prob
            if rand <= cumulative_prob:
                return action
        return 0  # Default to "fold" if something goes wrong

    def _choose_action(self, valid_actions, action_index):
        action_type = ["fold", "call", "raise"][action_index]
        for action in valid_actions:
            if action['action'] == action_type:
                if action_type == "raise":
                    amount = random.randint(action['amount']['min'], action['amount']['max'])
                    return action_type, amount
                return action_type, action.get('amount', 0)
        return valid_actions[0]['action'], valid_actions[0].get('amount', 0)

    def receive_game_start_message(self, game_info):
        self.nb_players = len(game_info['seats'])

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.hole_card = hole_card

    def receive_street_start_message(self, street, round_state):
        self.current_street = street

    def receive_game_update_message(self, new_action, round_state):
        self.round_state = round_state

    def receive_round_result_message(self, winners, hand_info, round_state):
        for hand in hand_info:
            if 'action' in hand:
                reward = 1 if hand['player'] in winners else -1
                self.update_regrets(hand['action'], reward, hand['hole_card'], round_state)

    def update_regrets(self, action, reward, hole_card, round_state):
        strategy = self.get_strategy(hole_card, round_state)
        total_reward = sum([strategy[i] * reward for i in range(self.num_actions)])
        hole_card_tuple = tuple(hole_card)
        round_state_str = json.dumps(round_state, sort_keys=True)
        for a in range(self.num_actions):
            regret = reward - total_reward if a == action else -strategy[a] * reward
            self.regrets[(hole_card_tuple, round_state_str, a)] += regret


def setup_ai():
    return HybridPlayer()
