# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from rest_framework import serializers


class SmartPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def from_native(self, data):
        if isinstance(data, dict):
            data = data['id']
        return super(SmartPrimaryKeyRelatedField, self).from_native(data)

    def to_native(self, pk):
        if pk:
            if isinstance(pk, int):
                return super(SmartPrimaryKeyRelatedField, self).to_native(pk)
            else:
                ids = [ob.id for ob in pk.all()]
                return super(SmartPrimaryKeyRelatedField, self).to_native(ids)