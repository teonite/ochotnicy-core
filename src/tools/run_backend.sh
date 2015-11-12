#!/bin/bash
#
# Copyright 2011-2014 (C) TEONITE - http://teonite.com
#
# Author: Robert Olejnik <robert@teonite.com>
#
# Description:
#
#  TEONITE Docker run backend script
#

cd /code/
./tools/django-syncdb -d
#
# REMEMBER FIRST TIME TO:
# 1. create super user
# 2. load: userprofile and settings
python ./tools/manage.py loaddata categories organization_type abilities sites socialaccount certificatetemplate agreementtemplate education notification_types
python ./tools/manage.py collectstatic --noinput
exec uwsgi --ini ./conf/uwsgi.ini