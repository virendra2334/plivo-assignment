import django_heroku
import os

from .settings import *

DEBUG = False

ALLOWED_HOSTS = [
    'smsapi1.herokuapp.com'
]

django_heroku.settings(locals())
