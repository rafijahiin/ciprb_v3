from django.utils.translation import gettext_lazy as _
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
_allowed = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = _allowed.split(',') if _allowed else []
ALLOWED_HOSTS += ['localhost', '127.0.0.1']
# Accept all Railway and Render subdomains
ALLOWED_HOSTS += ['.railway.app', '.onrender.com', '.up.railway.app']
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
_allowed = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = _allowed.split(',') if _allowed else []
ALLOWED_HOSTS += ['localhost', '127.0.0.1']
# Accept all Railway and Render subdomains
ALLOWED_HOSTS += ['.railway.app', '.onrender.com', '.up.railway.app']

CSRF_TRUSTED_ORIGINS = [
    'https://ciprbv3-production.up.railway.app',
    'https://ciprb-v3.onrender.com',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'baseline',
    'tracker',
    'mpdsr',
    'reports',
    'dashboard',
    'activities',
    'training',
    'accounts',
]

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ciprb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ciprb.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('en', _('English')),
    ('bn', _('Bangla')),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
