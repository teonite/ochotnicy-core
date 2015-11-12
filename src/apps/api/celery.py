# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from __future__ import absolute_import
from datetime import timedelta
from celery.schedules import crontab
import os
import sys
import platform
from celery import Celery
from django.conf import settings

from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))

host_name = platform.node()
if '.' in host_name:
    new_host_name = host_name.replace('.', '-')
    print "Host name {0} contains dots (.) replacing by (-) and looking for conf.{1}-localsettings".format(
        host_name, new_host_name)
    host_name = new_host_name

config_file = "conf.{}-localsettings".format(host_name)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', config_file)

app = Celery('apps.api.celery')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)