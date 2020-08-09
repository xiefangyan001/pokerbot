'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import numpy as np
import eval7
import random

class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''

        self.mc_num = 30
        self.keep_num = 20
        self.permu_wrong_dict = []
        self.total_showdown = 0
        self.total_showdown_crit = 200  # the criteria on how many showdown we need to find the permutation
        self.this_round_permu = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.each_round_showdown_a = []
        self.each_round_showdown_b = []
        self.each_round_delta = []
        self.pre_dict = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q',
                         13: 'K', 14: 'A'}
        self.inverse_dict = {self.pre_dict[key]: key for key in self.pre_dict}
        self.color = ['s', 'd', 'c', 'h']
        self.card_li = []
        self.win_preflop = False
        self.win_flop = False
        self.win_turn = False
        self.win_river = False
        self.has_win = False
        self.win_rate = 0
        for key in self.pre_dict:
            for each_c in self.color:
                self.card_li.append(self.pre_dict[key] + each_c)

        def permu_init():
            original_permutation = [2, 3, 4, 5, 6, 7, 8, 9, 'T', 'J', 'Q', 'K', 'A']
            proposed_permutation = []
            for i in range(13):
                pop_index = (np.random.geometric(p=0.25) - 1) % len(original_permutation)
                selected_element = original_permutation.pop(pop_index)
                proposed_permutation.append(str(selected_element))
            return proposed_permutation

        for i in range(self.keep_num):
            self.permu_wrong_dict.append([''.join(permu_init()), 0])
        self.this_round_permu = self.permu_wrong_dict[0][0]

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        self.win_rate = 0
        self.win_preflop = False
        self.win_flop = False
        self.win_turn = False
        self.win_river = False
        my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        # game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        # my_cards = round_state.hands[active]  # your cards
        # big_blind = bool(active)  # True if you are the big blind
        if 2 * my_bankroll + 3 * round_num > 3000:
            self.has_win = True


    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''

        # this function is to generate permutation randomly

        def permu():
            original_permutation = [2, 3, 4, 5, 6, 7, 8, 9, 'T', 'J', 'Q', 'K', 'A']
            proposed_permutation = []
            for i in range(13):
                pop_index = (np.random.geometric(p=0.25) - 1) % len(original_permutation)
                selected_element = original_permutation.pop(pop_index)
                proposed_permutation.append(str(selected_element))
            return proposed_permutation

        # decide if the showndown meet the this permutation
        def rule_pass(this_permu, my_cards, opp_cards, my_delta):
            permu_dict = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10,
                          'K': 11, 'A': 12}
            my_cards_real = [this_permu[permu_dict[each_card[0]]] + each_card[1] for each_card in my_cards]
            opp_cards_real = [this_permu[permu_dict[each_card[0]]] + each_card[1] for each_card in opp_cards]
            my_cards_eval = [eval7.Card(s) for s in my_cards_real]
            opp_cards_eval = [eval7.Card(s) for s in opp_cards_real]
            my_eval = eval7.evaluate(my_cards_eval)
            opp_eval = eval7.evaluate(opp_cards_eval)
            if my_eval > opp_eval and my_delta > 0:
                return True
            if my_eval < opp_eval and my_delta < 0:
                return True
            if my_eval == opp_eval and my_delta == 0:
                return True
            return False

        my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        my_cards = previous_state.hands[active]  # your cards
        opp_cards = previous_state.hands[1 - active]  # opponent's cards or [] if not revealed

        if opp_cards != []:
            my_cards = my_cards + previous_state.deck[:street]
            opp_cards = opp_cards + previous_state.deck[:street]
            self.each_round_showdown_a.append(my_cards)
            self.each_round_showdown_b.append(opp_cards)
            self.each_round_delta.append(my_delta)
            self.total_showdown += 1
            print(self.total_showdown)
            if self.total_showdown <= self.total_showdown_crit:
                for i in range(self.keep_num):
                    if not rule_pass(self.permu_wrong_dict[i][0], my_cards, opp_cards, my_delta):
                        self.permu_wrong_dict[i][1] = self.permu_wrong_dict[i][1] + 1
                for i in range(self.mc_num):
                    wrong_num = 0
                    this_permu = ''.join(permu())
                    for j in range(self.total_showdown):
                        if not rule_pass(this_permu, self.each_round_showdown_a[j], self.each_round_showdown_b[j],
                                         self.each_round_delta[j]):
                            wrong_num += 1
                    self.permu_wrong_dict.append([this_permu, wrong_num])
                self.permu_wrong_dict = sorted(self.permu_wrong_dict, key=lambda x: x[1])
                self.permu_wrong_dict = self.permu_wrong_dict[:self.keep_num]
                self.this_round_permu = list(self.permu_wrong_dict[0][0])
                print(self.this_round_permu)

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''

        def mc_win_rate(my_cards, common_cards):
            simu_num = 800
            my_win = 0
            total_round = 0
            for i in range(simu_num):
                slices = random.sample(self.card_li, 7 - len(common_cards))
                if len(set(my_cards + common_cards + slices)) == 9:
                    total_round += 1
                    my_cards_eval = [eval7.Card(s) for s in my_cards + common_cards + slices[:5 - len(common_cards)]]
                    opp_cards_eval = [eval7.Card(s) for s in common_cards + slices]
                    if eval7.evaluate(my_cards_eval) > eval7.evaluate(opp_cards_eval):
                        my_win += 1
            return my_win / total_round

        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, river, or turn respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot

        my_real_cards = [self.this_round_permu[self.inverse_dict[each_card[0]]-2] + each_card[1] for each_card in my_cards]
        board_real_cards = [self.this_round_permu[self.inverse_dict[each_card[0]]-2] + each_card[1] for each_card in board_cards]
        if street == 0 and self.win_preflop == False:
            self.win_rate = mc_win_rate(my_real_cards, board_real_cards)
            self.win_preflop = True
        if street == 3 and self.win_flop == False:
            self.win_rate = mc_win_rate(my_real_cards, board_real_cards)
            self.win_flop = True
        if street == 4 and self.win_turn == False:
            self.win_rate = mc_win_rate(my_real_cards, board_real_cards)
            self.win_turn = True
        if street == 5 and self.win_river == False:
            self.win_rate = mc_win_rate(my_real_cards, board_real_cards)
            self.win_river = True

        if self.has_win and (FoldAction in legal_actions):
            return FoldAction()
        if self.has_win and (CheckAction in legal_actions):
            return CheckAction()

        if legal_actions == {CheckAction}:
            return CheckAction()

        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()  # the smallest and largest numbers of chips for a legal bet/raise
            if self.win_rate == 1:
                raiseAmount = max_raise
            else:
                raiseAmount = int(self.win_rate / (1-self.win_rate) * opp_contribution)
            raiseAmount = min(max_raise, raiseAmount)
            if raiseAmount >= min_raise:
                return RaiseAction(raiseAmount)
            else:
                if self.win_rate > continue_cost / (continue_cost + my_contribution + opp_contribution):
                    if CheckAction in legal_actions:
                        return CheckAction()
                    else:
                        return CallAction()
                else:
                    return FoldAction()

        if CheckAction in legal_actions:  # check-call
            return CheckAction()
        return CallAction()


if __name__ == '__main__':
    run_bot(Player(), parse_args())
