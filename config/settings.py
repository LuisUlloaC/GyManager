from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-c*v_v0%)rld3-o2l@hn7h(90woa9366d0-tcs*ne5lh4=*p8wh'

DEBUG = True

INSTALLED_APPS = ['data']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MEDIA_ROOT = 'media/'
MEDIA_URL = '/media/'