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


class ApplicationState():
    @abstractmethod
    def assert_can_change_state(self, next_state, offer, user):
        pass

    @abstractmethod
    def perform_actions_after_changing_status(self, next_state, request):
        pass

    @abstractmethod
    def get_applications_for_offer(self, offer_pk):
        pass


class PendingToReviewApplicationState(ApplicationState):
    def assert_can_change_state(self, next_state, application, user):
        if next_state == ApplicationStateFactory.ACCEPTED or \
                next_state == ApplicationStateFactory.REJECTED:
            self.assert_has_permissions_to_change_state_my_application(application, user)

    def get_applications_for_offer(self, offer_pk):
        from .models import Application

        return Application.objects.filter(status=ApplicationStateFactory.PENDING_TO_REVIEW, offer=offer_pk)


class AcceptedApplicationState(ApplicationState):
    def assert_can_change_state(self, next_state, application, user):
        if next_state == ApplicationStateFactory.PENDING_TO_REVIEW or \
                next_state == ApplicationStateFactory.REJECTED:
            self.assert_has_permissions_to_change_state_my_application(application, user)

    def get_applications_for_offer(self, offer_pk):
        from .models import Application

        return Application.objects.filter(status=ApplicationStateFactory.ACCEPTED, offer=offer_pk)


class RejectedApplicationState(ApplicationState):
    def assert_can_change_state(self, next_state, application, user):
        if next_state == ApplicationStateFactory.ACCEPTED or \
                next_state == ApplicationStateFactory.PENDING_TO_REVIEW:
            self.assert_has_permissions_to_change_state_my_application(application, user)

    def get_applications_for_offer(self, offer_pk):
        from .models import Application

        return Application.objects.filter(status=ApplicationStateFactory.REJECTED, offer=offer_pk)


class ApplicationStateFactory:
    PENDING_TO_REVIEW = 0
    ACCEPTED = 1
    REJECTED = 2

    available_statuses = (
        (PENDING_TO_REVIEW, 'pending to review'),
        (ACCEPTED, 'accepted'),
        (REJECTED, 'rejected'),
    )

    products = (
        (PENDING_TO_REVIEW, PendingToReviewApplicationState),
        (ACCEPTED, AcceptedApplicationState),
        (REJECTED, RejectedApplicationState),
    )

    products_codes = (
        ('pending', PendingToReviewApplicationState),
        ('accepted', AcceptedApplicationState),
        ('rejected', RejectedApplicationState),
    )

    @classmethod
    def get_statuses_choice_list(cls):
        return cls.available_statuses

    @classmethod
    def make(cls, id):
        for product in cls.products:
            if product[0] == id:
                return product[1]()

    @classmethod
    def make_for_code(cls, code):
        for product in cls.products_codes:
            if product[0] == code:
                return product[1]()
        raise KeyError('No such application key')