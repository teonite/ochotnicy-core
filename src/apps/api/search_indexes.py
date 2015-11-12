# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

import datetime
from django.db.models import Q
from haystack import indexes
from haystack.backends import SQ
from .models import Offer


class OfferIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, model_attr='title')

    description = indexes.CharField(model_attr='description')
    description_time = indexes.CharField(model_attr='description_time')
    description_problem = indexes.CharField(model_attr='description_problem')
    description_requirements = indexes.CharField(model_attr='description_requirements')
    description_quests = indexes.CharField(model_attr='description_quests')
    description_benefits = indexes.CharField(model_attr='description_benefits')
    description_additional_requirements = indexes.CharField(model_attr='description_additional_requirements')

    organization_fullname = indexes.CharField(model_attr='publishing_organization__fullname')
    organization_shortname = indexes.CharField(model_attr='publishing_organization__shortname')
    organization_description = indexes.CharField(model_attr='publishing_organization__description')
    organization_city = indexes.CharField(model_attr='publishing_organization__city')
    organization_province = indexes.CharField(model_attr='publishing_organization__province')
    organization_district = indexes.CharField(model_attr='publishing_organization__district')
    organization_street = indexes.CharField(model_attr='publishing_organization__street')

    publish_to = indexes.DateTimeField(model_attr='publish_to')
    publish_from = indexes.DateTimeField(model_attr='publish_from')
    status = indexes.IntegerField(model_attr='status')

    def get_model(self):
        return Offer

    def index_queryset(self, using=None):
        return self.get_model().objects.filter()

    class Meta:
        search_within = ('text', 'organization_fullname', 'organization_shortname', 'description', 'description_time',
            'description_problem', 'description_requirements', 'description_quests', 'description_benefits',
            'description_additional_requirements', 'organization_description', 'organization_city', 'organization_province',
            'organization_district', 'organization_street',)