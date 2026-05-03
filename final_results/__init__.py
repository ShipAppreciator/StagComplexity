from otree.api import *

doc = """
Final results page combining payoffs from stag hunt, BRET, and CRT.
Includes exit survey.
"""

class C(BaseConstants):
    NAME_IN_URL = 'final_results'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    thought_process = models.LongStringField(
        label='What was your thought process in making your decisions?'
    )
    strategy_update = models.LongStringField(
        label='Did you update your strategy throughout the session?'
    )
    uncertain_why = models.LongStringField(
        label='In rounds where you were uncertain, what made you uncertain?'
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
    age = models.IntegerField(label='What is your age?', min=18, max=100)
    gender = models.StringField(
        label='What is your gender?',
        choices=['Male', 'Female', 'Non-binary', 'Prefer not to say'],
    )


# ——— Pages ———

class Survey(Page):
    form_model = 'player'
    form_fields = ['thought_process', 'strategy_update', 'uncertain_why', 'major', 'age', 'gender']


class ThankYou(Page):
    @staticmethod
    def vars_for_template(player: Player):
        pp = player.participant
        stag_payoff = pp.vars.get('stag_payoff', cu(0))
        bret_payoff = pp.vars.get('bret_payoff', cu(0))
        crt_payoff = pp.vars.get('crt_payoff', cu(0))
        total = stag_payoff + bret_payoff + crt_payoff
        return dict(
            stag_payoff=stag_payoff,
            bret_payoff=bret_payoff,
            crt_payoff=crt_payoff,
            total=total,
        )


page_sequence = [Survey, ThankYou]
