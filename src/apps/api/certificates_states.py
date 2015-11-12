# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

import datetime

from abc import abstractmethod
from .helpers import PermissionHelperMixin, WrongRequestException, OfferPermissionHelperMixin


class CertificateState():
    @abstractmethod
    def assert_can_upload(self):
        pass

    @abstractmethod
    def get_next_state(self):
        pass

    @abstractmethod
    def assert_can_regenerate_pdf(self):
        pass

    @abstractmethod
    def get_uploading_field_value(self):
        pass


class NotSignedCertificateState(CertificateState):
    def assert_can_upload(self):
        if not 'volunteer_signed_resource' in self.request.DATA and \
                not self.request.DATA['organization_signed_resource']:
            raise WrongRequestException("You have not given resource")

    def get_next_state(self):
        if 'organization_signed_resource' in self.request.DATA:
            return CertificateStateFactory.SIGNED_BY_ORGANIZATION
        elif 'volunteer_signed_resource' in self.request.DATA:
            return CertificateStateFactory.SIGNED_BY_VOLUNTEER
        raise WrongRequestException("You have not given resource")

    def assert_can_regenerate_pdf(self):
        pass

    def get_uploading_field_value(self):
        return 'organization_signed_resource' if self.get_next_state() is CertificateStateFactory.SIGNED_BY_ORGANIZATION \
            else 'volunteer_signed_resource'


class SignedByOrganizationCertificateState(CertificateState):
    def assert_can_upload(self):
        if 'organization_signed_resource' in self.request.DATA:
            raise WrongRequestException("Already signed by organization")
        if not 'volunteer_signed_resource' in self.request.DATA:
            raise WrongRequestException("You have not given resource")

    def get_next_state(self):
        if 'volunteer_signed_resource' in self.request.DATA:
            return CertificateStateFactory.SIGNED_BY_BOTH
        raise WrongRequestException("You have not given resource")

    def assert_can_regenerate_pdf(self):
        raise WrongRequestException("Cannot regenerate pdf because organization has already signed it")

    def get_uploading_field_value(self):
        return 'volunteer_signed_resource'


class SignedByVolunteerCertificateState(CertificateState):
    def assert_can_upload(self):
        if 'volunteer_signed_resource' in self.request.DATA:
            raise WrongRequestException("Already signed by volunteer")
        if not self.request.DATA['organization_signed_resource']:
            raise WrongRequestException("You have not given resource")

    def get_next_state(self):
        if 'organization_signed_resource' in self.request.DATA:
            return CertificateStateFactory.SIGNED_BY_BOTH
        raise WrongRequestException("You have not given resource")

    def assert_can_regenerate_pdf(self):
        raise WrongRequestException("Cannot regenerate pdf because volunteer has already signed it")

    def get_uploading_field_value(self):
        return 'organization_signed_resource'


class SignedByBothCertificateState(CertificateState):
    def assert_can_upload(self):
        raise WrongRequestException("Resource already signed by both sides")

    def get_next_state(self):
        raise WrongRequestException("Resource already signed by both sides")

    def assert_can_regenerate_pdf(self):
        raise WrongRequestException("Cannot regenerate pdf because both sides have already signed it")

    def get_uploading_field_value(self):
        raise WrongRequestException("Resource already signed by both sides")


class CertificateStateFactory:
    NOT_SIGNED = 0
    SIGNED_BY_ORGANIZATION = 1
    SIGNED_BY_VOLUNTEER = 2
    SIGNED_BY_BOTH = 3

    available_statuses = (
        (NOT_SIGNED, 'not signed'),
        (SIGNED_BY_ORGANIZATION, 'signed by organization'),
        (SIGNED_BY_VOLUNTEER, 'signed by volunteer'),
        (SIGNED_BY_BOTH, 'signed by both organization and volunteer')
    )

    products = (
        (NOT_SIGNED, NotSignedCertificateState),
        (SIGNED_BY_ORGANIZATION, SignedByOrganizationCertificateState),
        (SIGNED_BY_VOLUNTEER, SignedByVolunteerCertificateState),
        (SIGNED_BY_BOTH, SignedByBothCertificateState)
    )

    @classmethod
    def get_statuses_choice_list(cls):
        return cls.available_statuses

    @classmethod
    def make(cls, id):
        for product in cls.products:
            if product[0] == id:
                return product[1]()