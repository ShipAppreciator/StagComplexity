from os import environ

SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=5)

PARTICIPANT_FIELDS = ['bret_payoff', 'stag_payoff', 'crt_payoff']

SESSION_CONFIGS = [
    dict(
        name='easyseq',
        display_name='Easy Sequential',
        num_demo_participants=2,
        app_sequence=['easyseq', 'bret', 'crt', 'final_results'],
        treatment='easyseq',
    ),
    dict(
        name='easysim',
        display_name='Easy Simultaneous',
        num_demo_participants=2,
        app_sequence=['easysim', 'bret', 'crt', 'final_results'],
        treatment='easysim',
    ),
    dict(
        name='hardseq',
        display_name='Hard Sequential',
        num_demo_participants=2,
        app_sequence=['hardseq', 'bret', 'crt', 'final_results'],
        treatment='hardseq',
    ),
    dict(
        name='hardsim',
        display_name='Hard Simultaneous',
        num_demo_participants=2,
        app_sequence=['hardsim', 'bret', 'crt', 'final_results'],
        treatment='hardsim',
    ),
]

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False
DEMO_PAGE_INTRO_HTML = ''
SESSION_FIELDS = ['treatment']
ROOMS = [
    dict(
        name='my_lab',
        display_name='My Lab',
        participant_label_file='participant_labels.txt',
    ),
]
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
SECRET_KEY = 'blahblah'
INSTALLED_APPS = ['otree']
