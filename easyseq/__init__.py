from otree.api import *
import random

doc = """
Easy Sequential Stag Hunt
Player 1 moves first, then Player 2 sees Player 1's choice before deciding.
Played for 10 rounds; one round selected at random for payment.
Players are randomly rematched each round.
"""

class C(BaseConstants):
    NAME_IN_URL = 'easyseq'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10

    # Payoff matrix (in points)
    HARE_HARE   = 6
    HARE_STAG   = 7
    STAG_HARE   = 0
    STAG_STAG   = 16


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    round_payoff = models.CurrencyField(initial=0)
    comp1_correct = models.BooleanField(initial=False)
    comp2_correct = models.BooleanField(initial=False)
    comp3_correct = models.BooleanField(initial=False)
    role_this_round = models.StringField()
    choice = models.StringField(
        choices=['A', 'B'],
        label='Your choice:',
        widget=widgets.RadioSelect,
    )
    confidence = models.IntegerField(min=0, max=100, label='')
    is_payment_round = models.BooleanField(initial=False)
    comp1 = models.BooleanField(
        label='True or false: you will be paid for your performance in each round.',
        widget=widgets.RadioSelect,
        choices=[[True, 'True'], [False, 'False']],
    )
    comp2 = models.IntegerField(
        label='If you pick B and the other player picks A, how much will you earn if this round is selected?',
    )
    comp3 = models.BooleanField(
        label='True or false: if you are selected to be Player 2, you will not see your opponent\'s action.',
        widget=widgets.RadioSelect,
        choices=[[True, 'True'], [False, 'False']],
    )




# ——— Functions ———

def creating_session(subsession: Subsession):
    subsession.group_randomly()
    if subsession.round_number == 1:
        payment_round = random.randint(1, C.NUM_ROUNDS)
        subsession.session.vars['payment_round'] = payment_round
    for player in subsession.get_players():
        player.role_this_round = 'P1' if player.id_in_group == 1 else 'P2'

def set_payoffs(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)

    p1c = p1.choice
    p2c = p2.choice

    if p1c == 'A' and p2c == 'A':
        p1.payoff, p2.payoff = C.HARE_HARE, C.HARE_HARE
    elif p1c == 'A' and p2c == 'B':
        p1.payoff, p2.payoff = C.HARE_STAG, C.STAG_HARE
    elif p1c == 'B' and p2c == 'A':
        p1.payoff, p2.payoff = C.STAG_HARE, C.HARE_STAG
    else:
        p1.payoff, p2.payoff = C.STAG_STAG, C.STAG_STAG

    # Store round_payoff BEFORE any zeroing
    for p in [p1, p2]:
        p.round_payoff = p.payoff

    if 'payment_round' not in group.session.vars:
        group.session.vars['payment_round'] = random.randint(1, C.NUM_ROUNDS)

    payment_round = group.session.vars['payment_round']

    for p in [p1, p2]:
        if group.round_number == payment_round:
            p.is_payment_round = True
        else:
            p.payoff = 0

    if group.round_number == C.NUM_ROUNDS:
        for p in [p1, p2]:
            p_round1 = p.in_round(1)
            comp_earnings = sum([
                p_round1.comp1_correct,
                p_round1.comp2_correct,
                p_round1.comp3_correct,
            ]) * 0.50
            game_earnings = p.in_round(payment_round).payoff
            p.participant.payoff = comp_earnings + game_earnings
            p.participant.vars['stag_payoff'] = cu(comp_earnings + game_earnings)
# ——— Pages ———
class WaitForEveryone(WaitPage):
    wait_for_all_groups = True
    body_text = 'Waiting for all participants to finish the round...'

class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class RoleAssignment(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(role=player.id_in_group)
class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['comp1', 'comp2', 'comp3']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.comp1 == False:
            player.comp1_correct = True
        if player.comp2 == 0:
            player.comp2_correct = True
        if player.comp3 == False:
            player.comp3_correct = True

class ComprehensionResults(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            comp1_correct=player.comp1_correct,
            comp2_correct=player.comp2_correct,
            comp3_correct=player.comp3_correct,
            total=sum([player.comp1_correct, player.comp2_correct, player.comp3_correct]),
        )

class P1Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1


class WaitForP1(WaitPage):
    pass


class P2Decision(Page):
    form_model = 'player'
    form_fields = ['choice']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        p1 = player.group.get_player_by_id(1)
        return dict(p1_choice=p1.choice)


class P1Confidence(Page):
    form_model = 'player'
    form_fields = ['confidence']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 1

    @staticmethod
    def vars_for_template(player: Player):
        return dict(choice=player.choice)


class P2Confidence(Page):
    form_model = 'player'
    form_fields = ['confidence']

    @staticmethod
    def is_displayed(player: Player):
        return player.id_in_group == 2

    @staticmethod
    def vars_for_template(player: Player):
        return dict(choice=player.choice)


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        p1 = player.group.get_player_by_id(1)
        p2 = player.group.get_player_by_id(2)
        other = p2 if player.id_in_group == 1 else p1
        return dict(
            your_choice=player.choice,
            other_choice=other.choice,
            round_payoff=player.round_payoff,
        )
class Survey(Page):
    form_model = 'player'
    form_fields = ['thought_process', 'major', 'strategy_update']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

class ThankYou(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        payment_round = player.session.vars['payment_round']
        p_payment_round = player.in_round(payment_round)
        partner = p_payment_round.group.get_player_by_id(
            2 if p_payment_round.id_in_group == 1 else 1
        )
        comp_earnings = sum([
            player.in_round(1).comp1_correct,
            player.in_round(1).comp2_correct,
            player.in_round(1).comp3_correct,
        ])
        game_earnings = cu(p_payment_round.payoff)
        return dict(
            payment_round=payment_round,
            your_choice=p_payment_round.choice,
            other_choice=partner.choice,
            comp_earnings=comp_earnings,
            game_earnings=game_earnings,
        )
page_sequence = [
    Instructions,
    ComprehensionCheck,
    ComprehensionResults,
    RoleAssignment,
    P1Decision,
    P1Confidence,
    WaitForP1,
    P2Decision,
    P2Confidence,
    ResultsWaitPage,
    Results,
    WaitForEveryone,
]
