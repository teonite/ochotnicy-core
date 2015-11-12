# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

import django_filters
from .models import Offer, Application, Organization
from .helpers import ListFilter
from django_filters import ModelChoiceFilter, NumberFilter


class OfferListFilter(django_filters.FilterSet):
    category = ListFilter('category')

    class Meta:
        model = Offer
        fields = ('category',)


class OfferAdminListFilter(django_filters.FilterSet):
    publishing_organization = ListFilter('publishing_organization__fullname')
    status = ListFilter('status')

    class Meta:
        model = Offer
        fields = ('publishing_organization', 'status')


class OrganizationListFilter(django_filters.FilterSet):
    fullname = ListFilter('fullname')

    class Meta:
        model = Organization
        fields = ('fullname',)


class OrganizationOfferListFilter(django_filters.FilterSet):
    status = ListFilter('status')

    class Meta:
        model = Offer
        fields = ('status',)


class ApplicationListFilter(django_filters.FilterSet):
    status = ListFilter('status')

    class Meta:
        model = Application
        fields = ('status',)