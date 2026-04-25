from os import environ

SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=1, participation_fee=5)

SESSION_CONFIGS = [
    dict(
        name='easyseq',
        display_name='Easy Sequential',
        num_demo_participants=None,
        app_sequence=['easyseq'],
        treatment='easyseq',
    ),
    dict(
        name='easysim',
        display_name='Easy Simultaneous',
        num_demo_participants=None,
        app_sequence=['easysim'],
        treatment='easysim',
    ),
    dict(
        name='hardseq',
        display_name='Hard Sequential',
        num_demo_participants=None,
        app_sequence=['hardseq'],
        treatment='hardseq',
    ),
    dict(
        name='hardsim',
        display_name='Hard Simultaneous',
        num_demo_participants=None,
        app_sequence=['hardsim'],
        treatment='hardsim',
    ),
]

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = []
SESSION_FIELDS = ['treatment']
ROOMS = [
    dict(
        name='my_lab',
        display_name='My Lab',
        participant_label_file='participant_labels.txt',
    ),
]
ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
SECRET_KEY = 'blahblah'
# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']
