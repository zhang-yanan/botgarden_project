import os
import logging
# ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
ENVIRONMENT_DIR = os.path.dirname(PROJECT_DIR)
ENVIRONMENT = os.path.basename(ENVIRONMENT_DIR)


configs = {
    'dev': 'settings-dev',
    'prod': 'settings-prod',
    'qa': 'settings-qa',
}

# Default config to dev
if not configs.get(ENVIRONMENT):
    CONFIG = 'settings-dev'
else:
    CONFIG = configs[ENVIRONMENT]

# Import the configuration settings file - REPLACE projectname with your project
config_module = __import__('%s' % CONFIG, globals(), locals(), 'botgarden_project')

# Load the config settings properties into the local scope.
for setting in dir(config_module):
    if setting == setting.upper():
        locals()[setting] = getattr(config_module, setting)
    





#
# Log things from this file only to a separate "settings.log" file.
#
# logging.basicConfig(filename=LOGS_DIR + os.sep + 'settings.log', level=logging.DEBUG)
# logging.debug('Settings log file started.')

#
# If the application's WSGI setup script added an environment variable to tell us
# the WSGI mount point path then we should use it; otherwise, we'll assume that
# the application was mounted at the root of the current server
#
# WSGI_BASE = os.environ.get(__package__ + ".WSGI_BASE")
# if WSGI_BASE is not None:
#     logging.debug('WSGI_BASE was found in environment variable: ' + __package__ + ".WSGI_BASE")
# else:
#     logging.debug('WSGI_BASE was not set.')
#     WSGI_BASE = ''
# 
# logging.debug('WSGI_BASE =' + WSGI_BASE)
# LOGIN_URL = WSGI_BASE + '/accounts/login'
