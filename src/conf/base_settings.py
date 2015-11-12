# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

"""
Base settings - imported from localsettings.
Do NOT use this file as server config - use localsettings
"""
from datetime import timedelta

import os
import sys

PROJECT_NAME = 'PROJECT_NAME'
VERSION = '1.0'

try:
    from .loggersettings import *
except ImportError:
    print 'FATAL: Cannot find logger configuration'
    sys.exit()

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
PATH_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/static/static.lawrence.com/static/"
MEDIA_ROOT = os.path.join(PATH_ROOT, 'media')

# URL that handles the static served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://static.lawrence.com/static/", "http://example.com/static/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/static/static.lawrence.com/static/"
STATIC_ROOT = os.path.join(PATH_ROOT, 'static')

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PATH_ROOT, 'templates/static'),
    MEDIA_ROOT
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'apps.api.middleware.HeaderMiddleware',
    'reversion.middleware.RevisionMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
)

ROOT_URLCONF = 'conf.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PATH_ROOT, 'templates'),
)

TEMPLATE_DIR = TEMPLATE_DIRS[0]

FIXTURE_DIRS = (
    os.path.join(PROJECT_DIR, 'fixtures'),
)

INSTALLED_APPS = (

    # admin tools
    'suit',

    # django components
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.twitter',

    'django_filters',
    'django_countries',
    'rest_framework',
    'corsheaders',
    'rest_framework.authtoken',
    'registration_api',
    'south',
    'easy_thumbnails',
    'apps.api',
    'import_export',
    'notification',
    'django_hstore',
    'reversion',
    'haystack',
    'app_metrics',
    'raven.contrib.django.raven_compat'
)

ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_API_ACTIVATION_SUCCESS_URL = '/'

LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
LOGIN_REDIRECT_URL = '/accounts/profile/'

THUMBNAIL_DIR = 'original-images'

DATETIME_FORMAT = 'Y/m/d H:i:s,u'

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'}
    },
    'facebook': {
        'SCOPE': ['public_profile', 'email', 'publish_actions'],
        'METHOD': 'oauth2',
        'VERIFIED_EMAIL': True
    },
    'twitter': {
        'SCOPE': ['r_emailaddress'],
    },
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ),

    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),

    # pagination
    'PAGINATE_BY': 10,
    'PAGINATE_BY_PARAM': 'limit',
    'MAX_PAGINATE_BY': 100
}

BROKER_URL = 'amqp://guest@localhost//'

CELERY_TIMEZONE = 'Europe/Warsaw'

CELERYBEAT_SCHEDULE = {
    'notify': {
        'task': 'apps.api.tasks.notification',
        'schedule': timedelta(minutes=1),
        'args': ()
    },
    'metrics': {
        'task': 'apps.api.tasks.metrics',
        'schedule': timedelta(minutes=5),
        'args': ()
    },
}

CSRF_COOKIE_NAME = 'csrftoken'
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = ['x-requested-with', 'content-type', 'accept', 'origin', 'authorization', 'x-csrftoken', 'content-disposition']
CORS_EXPOSE_HEADERS = ['X-Backend-Version']

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'