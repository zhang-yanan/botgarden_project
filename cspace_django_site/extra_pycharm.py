import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_PARENT_DIR = os.path.dirname(BASE_DIR)
LOGS_DIR = BASE_PARENT_DIR + os.sep + 'logs'
PROJECT_NAME = os.path.basename(BASE_PARENT_DIR)

CACHES = {
   'default': {
       'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
       'LOCATION': '/tmp/' + PROJECT_NAME + '/images',
       'CULL_FREQUENCY': 100000,
       'OPTIONS': {
           'MAX_ENTRIES': 1000000
       }
   }
}
