# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from django.conf import settings


class HeaderMiddleware:
    def process_response(self, request, response):
        response['X-Backend-Version'] = settings.BACKEND_VERSION

        return response