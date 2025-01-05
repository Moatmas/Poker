from pypokerengine.players import BasePokerPlayer

class EmulatorPlayer(BasePokerPlayer):
    def __init__(self):
        super(EmulatorPlayer, self).__init__()
        self.seat_id = None  # Initialisation du seat_id
        self.NB_SIMULATION = 10  # Nombre de simulations pour chaque action

    def declare_action(self, valid_actions, hole_card, round_state):
        if self.seat_id is None:
            print("Error: seat_id is not set.")
            return 'fold', 0

        try_actions = ['fold', 'call', 'min_raise', 'max_raise']
        action_scores = {action: 0 for action in try_actions}

        for try_action in try_actions:
            self._setup_model_for_action(try_action)
            simulation_results = []

            for _ in range(self.NB_SIMULATION):
                updated_state = self._simulate_game(try_action, round_state)

                if "players" not in updated_state or not 0 <= self.seat_id < len(updated_state["players"]):
                    print("Error: Invalid state or seat_id.")
                    continue

                player_state = updated_state["players"][self.seat_id]
                if 'stack' not in player_state:
                    print("Error: 'stack' key not found in player state.")
                    continue

                result = player_state["stack"]
                simulation_results.append(result)

            if simulation_results:
                action_scores[try_action] = sum(simulation_results) / len(simulation_results)

        best_action = max(action_scores, key=action_scores.get)
        print(f"Best action: {best_action} with scores: {action_scores}")
        return best_action, self._get_action_amount(best_action, valid_actions)

    def set_seat(self, seat_id):
        self.seat_id = seat_id
        print(f"Seat ID set to: {self.seat_id}")

    def receive_game_start_message(self, game_info):
        if 'players' not in game_info:
            print("Erreur: la clé 'players' est manquante dans game_info")
            return

        for idx, player in enumerate(game_info['players']):
            if player['uuid'] == self.uuid:
                self.set_seat(idx)
                break

    def receive_round_start_message(self, round_count, hole, seats):
        print(f"Tour {round_count} commence.")
        print(f"Cartes privatives (hole): {hole}")
        print(f"Places assises: {seats}")
        self.hole_cards = hole
        self.seats = seats

    def receive_street_start_message(self, street, round_state):
        """Gestion du début de chaque rue de paris (ex: pre-flop, flop, turn, river)."""
        print(f"Début de la rue {street}.")
        print(f"Etat du tour: {round_state}")
        # Tu peux ici prendre des actions spécifiques pour chaque rue
        # Par exemple, en analysant les cartes visibles pour prendre des décisions stratégiques.

    def _simulate_game(self, action, round_state):
        simulated_state = {
            "players": [
                {"name": "emulator_player", "stack": 250},
                {"name": "fish_player", "stack": 200},
                {"name": "smart_player", "stack": 300},
                {"name": "cfr_player", "stack": 280},
            ]
        }

        if action == "fold":
            pass
        elif action == "call":
            simulated_state["players"][self.seat_id]["stack"] -= 10
        elif action == "min_raise":
            simulated_state["players"][self.seat_id]["stack"] += 20
        elif action == "max_raise":
            simulated_state["players"][self.seat_id]["stack"] += 50

        for i, player in enumerate(simulated_state["players"]):
            if i != self.seat_id:
                if player["stack"] > 250:
                    player["stack"] += 5
                else:
                    player["stack"] -= 5

        return simulated_state

    def _setup_model_for_action(self, action):
        print(f"Setting up model for action: {action}")

    def _get_action_amount(self, action, valid_actions):
        if action == 'fold':
            return 0
        elif action == 'call':
            return valid_actions[1]['amount']
        elif action == 'min_raise':
            return valid_actions[2]['amount']['min']
        elif action == 'max_raise':
            return valid_actions[2]['amount']['max']

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

# Fonction pour enregistrer le joueur
def setup_ai():
    return EmulatorPlayer()
