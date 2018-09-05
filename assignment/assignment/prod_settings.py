import dj_database_url
import os

from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'smsapi1.herokuapp.com'
]

DATABASES['default'] = dj_database_url.config(os.environ['DATABASE_URL'])
