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

    if 'payment_round' not in group.session.vars:
        group.session.vars['payment_round'] = random.randint(1, C.NUM_ROUNDS)

    payment_round = group.session.vars['payment_round']
    if group.round_number == payment_round:
        for p in [p1, p2]:
            p.is_payment_round = True
            p.participant.payoff = p.payoff
    else:
        for p in [p1, p2]:
            p.payoff = 0


# ——— Pages ———

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
    def error_message(player, values):
        errors = {}
        if values['comp1'] != False:
            errors['comp1'] = 'Incorrect. You will only be paid for one randomly selected round.'
        if values['comp2'] != 0:
            errors['comp2'] = 'Incorrect. If you pick B and the other player picks A, you earn 0 points.'
        if values['comp3'] != False:
            errors['comp3'] = 'Incorrect. Player 2 will see Player 1\'s choice before deciding.'
        return errors


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
        payment_round = player.session.vars['payment_round']
        return dict(
            p1_choice=p1.choice,
            p2_choice=p2.choice,
            round_number=player.round_number,
            payment_round=payment_round,
            is_payment_round=player.is_payment_round,
            payoff=player.participant.payoff if player.is_payment_round else None,
        )

page_sequence = [
    Instructions,
    ComprehensionCheck,
    RoleAssignment,
    P1Decision,
    P1Confidence,
    WaitForP1,
    P2Decision,
    P2Confidence,
    ResultsWaitPage,
    Results,
]
