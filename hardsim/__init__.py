from otree.api import *
import random

doc = """
Hard Simultaneous Stag Hunt
Both players choose simultaneously without seeing the other's action.
Played for 10 rounds; one round selected at random for payment.
"""

class C(BaseConstants):
    NAME_IN_URL = 'hardsim'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10

    # Payoff matrix (in points)
    HARE_HARE   = 6
    HARE_STAG   = 7
    STAG_HARE   = 0
    STAG_STAG   =8


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    comp1_correct = models.BooleanField(initial=False)
    comp2_correct = models.BooleanField(initial=False)
    comp3_correct = models.BooleanField(initial=False)
    choice = models.StringField(
        choices=['A', 'B'],
        label='Your choice:',
        widget=widgets.RadioSelect,
    )
    confidence = models.IntegerField(min=0, max=100, initial=50, label='')
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
        label='True or false: you will not see the other player\'s choice before making your own decision.',
        widget=widgets.RadioSelect,
        choices=[[True, 'True'], [False, 'False']],
    )

    thought_process = models.LongStringField(
    label='What was your thought process in making your decision?'
    )
    major = models.StringField(
        label='What is your major?',
        choices=[
            'Accounting',
            'Biology',
            'Business Administration',
            'Chemistry',
            'Communications',
            'Computer Science',
            'Economics',
            'Education',
            'Engineering',
            'English',
            'Finance',
            'History',
            'Information Systems',
            'Marketing',
            'Mathematics',
            'Nursing',
            'Philosophy',
            'Physics',
            'Political Science',
            'Psychology',
            'Sociology',
            'Statistics',
            'Other',
        ],
    )
    strategy_update = models.LongStringField(
        label='Did you update your strategy throughout the session?'
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
            ])
            game_earnings = p.in_round(payment_round).payoff
            p.participant.payoff = comp_earnings + game_earnings
# ——— Pages ———

class Instructions(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1


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
            player.participant.payoff += 1
        if player.comp2 == 0:
            player.comp2_correct = True
            player.participant.payoff += 1
        if player.comp3 == True:
            player.comp3_correct = True
            player.participant.payoff += 1

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

class Game(Page):
    form_model = 'player'
    form_fields = ['choice']


class Confidence(Page):
    form_model = 'player'
    form_fields = ['confidence']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(choice=player.choice)


class WaitForEveryone(WaitPage):
    wait_for_all_groups = True
    body_text = 'Waiting for all participants to finish the round...'

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
        return dict(payoff=player.participant.payoff_in_real_world_currency)

page_sequence = [
    Instructions,
    ComprehensionCheck,
    ComprehensionResults,
    Game,
    Confidence,
    ResultsWaitPage,
    Results,
    WaitForEveryone,
    Survey,
    ThankYou
]
