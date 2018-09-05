import dj_database_url

from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'smsapi1.herokuapp.com'
]


DATABASES['default'] = dj_database_url.config()
