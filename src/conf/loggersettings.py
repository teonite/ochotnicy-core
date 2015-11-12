# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

import sys
from django.core.exceptions import ImproperlyConfigured

try:
    from django.conf import settings
    if settings.GRAYLOG_CONF:
        GRAYLOG_CONFIGURED = True
except (ImportError, AttributeError, ImproperlyConfigured):
    GRAYLOG_CONFIGURED = False

try:
    from django.conf import settings
    if settings.RAVEN_CONFIG:
        SENTRY_CONFIGURED = True
except (ImportError, AttributeError, ImproperlyConfigured):
    SENTRY_CONFIGURED = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'ERROR',
        'handlers': ['console', 'file'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d: %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s] %(asctime)s %(module)s: %(message)s'
        },
        'colored': {
            'format': '[%(levelname)1.1s %(asctime)s] %(message)s'
        }
    },
    'handlers': {
        'file':{
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/debug.log',
            'formatter': 'colored'
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },

    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'INFO',
        },
        'apps': {
            'handlers':['console', 'file'],
            'propagate': False,
            'level':'DEBUG',
        }
    }
}

# add graylog handler if graylog config variables 
# are present in localsettings
if GRAYLOG_CONFIGURED:
    graypy_handler =  {
        'level': 'DEBUG',
        'class': 'graypy.GELFHandler',
        'host': GRAYLOG_CONF['host'],
        'port': GRAYLOG_CONF['port'],
        'localname': GRAYLOG_CONF['localname']
    }
    
    LOGGING['handlers']['graypy'] = graypy_handler
    LOGGING['loggers']['apps'].append('graypy')

# add sentry handler if sentry config variables 
# are present in localsettings
if SENTRY_CONFIGURED:
    sentry_handler =  {
        'level': 'ERROR',
        'class': 'raven.contrib.django.handlers.SentryHandler',
    }

    LOGGING['handlers']['sentry'] = sentry_handler
    LOGGING['loggers']['apps'].append('sentry')
