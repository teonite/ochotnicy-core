# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

import urlparse
from apps.api.helpers import instance_url

from django.views.generic.base import TemplateView
from django.conf import settings

from apps.api.models import *

__author__ = 'kkrzysztofik'


class CrawlerView(TemplateView):
    template_name = 'crawler.html'

    def get_context_data(self, **kwargs):
        context = super(CrawlerView, self).get_context_data(**kwargs)
        settings_obj = Settings.objects.get(settings__contains=['instance_name'])
        url_parts = self.kwargs['url'].split("/")
        default_img = urlparse.urljoin(instance_url(), "/img/banner-bg.jpg")

        context['instanceName'] = settings_obj.settings['instance_name']
        context['title'] = u"Strona główna"
        context['siteUrl'] = instance_url()
        context['description'] = u"Łączymy wolontariuszy z najlepszymi inicjatywami! Znajdź projekt, który odpowiada " \
                                 u"Twoim przekonaniom i wesprzyj cel swoim działaniem."
        context['imgUrl'] = default_img

        if len(url_parts) > 2:
            if url_parts[1] == 'tag':
                tag_id = url_parts[2]

                try:
                    tag = Category.objects.get(id=tag_id)
                except Category.DoesNotExist:
                    return context

                context['title'] = tag.name
                context['description'] = u"Wyświetl oferty z kategorii: %s" % tag.name
                context['siteUrl'] = urlparse.urljoin(instance_url(), self.kwargs['url'])
            elif url_parts[1] == 'offer':
                offer_id = url_parts[2]

                try:
                    offer = Offer.objects.get(id=offer_id)
                except Offer.DoesNotExist:
                    return context

                try:
                    thumbnail_obj = LargeOfferThumbnail.objects.get(offer=offer)
                    context['imgUrl'] = urlparse.urljoin(instance_url(), thumbnail_obj.filename.url)
                except LargeOfferThumbnail.DoesNotExist:
                    context['imgUrl'] = default_img

                context['title'] = offer.title
                context['description'] = offer.description
                context['siteUrl'] = urlparse.urljoin(instance_url(), self.kwargs['url'])
            elif url_parts[1] == 'organization':
                org_id = url_parts[2]

                try:
                    organization = Organization.objects.get(id=org_id)
                except Organization.DoesNotExist:
                    return context

                try:
                    thumbnail_obj = OrganizationThumbnail.objects.get(organization=organization)
                    context['imgUrl'] = urlparse.urljoin(instance_url(), thumbnail_obj.filename.url)
                except OrganizationThumbnail.DoesNotExist:
                    context['imgUrl'] = default_img

                context['title'] = organization.fullname
                context['description'] = organization.description
                context['siteUrl'] = urlparse.urljoin(instance_url(), self.kwargs['url'])
        return context