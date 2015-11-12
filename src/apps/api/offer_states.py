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
from django.contrib.auth.models import Permission
from .helpers import PermissionHelperMixin, WrongRequestException, OfferPermissionHelperMixin


class OfferState(PermissionHelperMixin):
    @abstractmethod
    def assert_can_change_state(self, next_state, offer, user):
        pass

    @abstractmethod
    def clean_after_editing_offer(self, request):
        pass

    @abstractmethod
    def perform_actions_after_changing_status(self, request, offer):
        pass

    @abstractmethod
    def prepare_request(self, request, offer):
        pass

    #private
    def changing_status_to_publish_implementation(self, next_state, request, offer):
        if next_state == OfferStateFactory.PUBLISHED:
            request.DATA['published_by'] = request.user.id
            request.DATA['published_at'] = datetime.datetime.now()

    #private
    def changing_status_to_depublish_implementation(self, next_state, request):
        if next_state == OfferStateFactory.DEPUBLISHED:
            request.DATA['depublished_by'] = request.user.id
            request.DATA['depublished_at'] = datetime.datetime.now()

    #private
    def provide_proper_publish_from_time(self, offer, request):
        if offer.publish_from < datetime.datetime.now():
            request.DATA['publish_from'] = datetime.datetime.now()


class NewOfferAbstractState(OfferPermissionHelperMixin, OfferState):
    def prepare_request(self, request, offer):
        if request.DATA['status'] == OfferStateFactory.PUBLISHED:
            if not request.user.has_perm('api.skip_review'):
                request.DATA['status'] = OfferStateFactory.IN_REVIEW

    def perform_actions_after_changing_status(self, request, offer):
        self.changing_status_to_publish_implementation(request.DATA['status'], request, offer)
        self.provide_proper_publish_from_time(offer, request)


class DraftOfferState(NewOfferAbstractState):
    def assert_can_change_state(self, next_state, offer, user):
        if next_state == OfferStateFactory.PUBLISHED:
            self.assert_has_permissions_to_publish_my_offer(offer, user)
        elif next_state in (OfferStateFactory.PUBLISHED_EDITED, OfferStateFactory.DEPUBLISHED, OfferStateFactory.REJECTED):
            raise WrongRequestException()
        elif next_state == OfferStateFactory.REMOVED:
            self.assert_has_permissions_to_remove_any_offer(offer, user)
        elif next_state == OfferStateFactory.IN_REVIEW:
            pass


class PublishedOfferState(OfferPermissionHelperMixin, OfferState):
    def assert_can_change_state(self, next_state, offer, user):
        if next_state in (OfferStateFactory.PUBLISHED_EDITED, OfferStateFactory.IN_REVIEW,
                OfferStateFactory.REJECTED, OfferStateFactory.DRAFT):
            raise WrongRequestException()
        elif next_state == OfferStateFactory.DEPUBLISHED:
            self.assert_has_permissions_to_publish_my_offer(offer, user)
        elif next_state == OfferStateFactory.REMOVED:
            self.assert_has_permissions_to_remove_any_offer(offer, user)


    def clean_after_editing_offer(self, request):
        request.DATA['status'] = OfferStateFactory.PUBLISHED_EDITED

    def perform_actions_after_changing_status(self, request, offer):
        self.changing_status_to_depublish_implementation(request.DATA['status'], request)


class PublishedEditedOfferState(OfferPermissionHelperMixin, OfferState):
    def assert_can_change_state(self, next_state, offer, user):
        if next_state in (OfferStateFactory.PUBLISHED, OfferStateFactory.DRAFT, OfferStateFactory.IN_REVIEW,
                OfferStateFactory.REJECTED):
            raise WrongRequestException()
        elif next_state == OfferStateFactory.DEPUBLISHED:
            self.assert_has_permissions_to_publish_my_offer(offer, user)
        elif next_state == OfferStateFactory.REMOVED:
            self.assert_has_permissions_to_remove_any_offer(offer, user)

    def perform_actions_after_changing_status(self, request, offer):
        self.changing_status_to_depublish_implementation(request.DATA['status'], request)


class DepublishedOfferState(OfferPermissionHelperMixin, OfferState):
    def assert_can_change_state(self, next_state, offer, user):
        if next_state == OfferStateFactory.PUBLISHED:
            self.assert_has_permissions_to_publish_my_offer(offer, user)
        elif next_state in (OfferStateFactory.PUBLISHED_EDITED, OfferStateFactory.DRAFT, OfferStateFactory.IN_REVIEW,
                OfferStateFactory.REJECTED):
            raise WrongRequestException()
        elif next_state == OfferStateFactory.REMOVED:
            self.assert_has_permissions_to_remove_any_offer(offer, user)

    def perform_actions_after_changing_status(self, request, offer):
        self.changing_status_to_publish_implementation(request.DATA['status'], request, offer)


class RemovedOfferState(OfferState):
    def assert_can_change_state(self, next_state, offer, user):
        raise WrongRequestException()
        '''if next_state != OfferStateFactory.REMOVED:
            self.assert_has_permissions_to_remove_any_offer(offer, user)'''

    def perform_actions_after_changing_status(self, request, offer):
        self.changing_status_to_publish_implementation(request.DATA['status'], request, offer)


class RejectedOfferState(NewOfferAbstractState):
    def assert_can_change_state(self, next_state, offer, user):
        if next_state == OfferStateFactory.PUBLISHED:
            self.assert_has_permissions_to_publish_my_offer(offer, user)
        elif next_state in (OfferStateFactory.PUBLISHED_EDITED, OfferStateFactory.DEPUBLISHED, OfferStateFactory.DRAFT,
                OfferStateFactory.IN_REVIEW):
            raise WrongRequestException()
        elif next_state == OfferStateFactory.REMOVED:
            self.assert_has_permissions_to_remove_any_offer(offer, user)


class InReviewOfferState(OfferPermissionHelperMixin, OfferState):
    def assert_can_change_state(self, next_state, offer, user):
        if next_state in (OfferStateFactory.PUBLISHED, OfferStateFactory.REJECTED):
            self.assert_has_permissions_to_review_my_offer(offer, user)
        elif next_state in (OfferStateFactory.PUBLISHED_EDITED, OfferStateFactory.DRAFT, OfferStateFactory.DEPUBLISHED,
                OfferStateFactory.REMOVED):
            raise WrongRequestException()

    def perform_actions_after_changing_status(self, request, offer):
        from apps.api.models import Review

        self.changing_status_to_publish_implementation(request.DATA['status'], request, offer)

        if request.DATA['status'] == OfferStateFactory.PUBLISHED:
            Review(organization=offer.publishing_organization, offer=offer).save()

            count = Review.objects.filter(organization=offer.publishing_organization).count()
            if count > 3:
                permission = Permission.objects.get(codename='skip_review')
                coordinator = offer.publishing_organization.coordinator
                coordinator.user_permissions.add(permission)
                coordinator.save()


class OfferStateFactory:
    DRAFT = 0
    IN_REVIEW = 1
    PUBLISHED = 2
    PUBLISHED_EDITED = 3
    DEPUBLISHED = 4
    REJECTED = 5
    REMOVED = 6

    available_statuses = (
        (DRAFT, 'draft'),
        (IN_REVIEW, 'in_review'),
        (PUBLISHED, 'published'),
        (PUBLISHED_EDITED, 'published_edited'),
        (DEPUBLISHED, 'unpublished'),
        (REJECTED, 'rejected'),
        (REMOVED, 'removed'),
    )

    products = (
        (DRAFT, DraftOfferState),
        (IN_REVIEW, InReviewOfferState),
        (PUBLISHED, PublishedOfferState),
        (PUBLISHED_EDITED, PublishedEditedOfferState),
        (DEPUBLISHED, DepublishedOfferState),
        (REJECTED, RejectedOfferState),
        (REMOVED, RemovedOfferState),
    )

    @classmethod
    def get_statuses_choice_list(cls):
        return cls.available_statuses

    @classmethod
    def make(cls, id):
        for product in cls.products:
            if product[0] == id:
                return product[1]()