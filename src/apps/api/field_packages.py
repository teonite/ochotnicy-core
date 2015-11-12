# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

import logging
from abc import abstractmethod
from .helpers import PermissionHelperMixin, WrongRequestException


class FieldPackage(object):
    def __init__(self, required=[], allowed_not_required=[]):
        self.required = required
        self.allowed_not_required = allowed_not_required

    def fits_to(self, data):
        for req in self.required:
            if req not in data.keys():
                return False

        request_copy = data.copy()
        for key in self.required:
            del request_copy[key]
        for key in self.allowed_not_required:
            if key in request_copy.keys():
                del request_copy[key]
        if request_copy:
            return False

        return True

    def is_accomplished(self, checker):
        is_accomplished = True

        for field in self.required:
            if not checker.is_accomplished(field):
                is_accomplished = False

        return is_accomplished


class FieldPackageSetFactory:
    packages_having_regard_to_order = ()

    @classmethod
    def make(cls):
        return [package['class'](required=package['required'], allowed_not_required=package['allowed_not_required']) \
            for package in cls.packages_having_regard_to_order]


class Checker:
    @abstractmethod
    def is_accomplished(self, field):
        pass


class ModelChecker(Checker):
    def __init__(self, model):
        self.model = model

    def is_accomplished(self, field):
        return getattr(self.model, field) is not self.model._meta.get_field(field).get_default()