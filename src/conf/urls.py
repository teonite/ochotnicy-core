# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from apps.api.helpers import instance_url
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework import routers
from rest_framework_nested.routers import NestedSimpleRouter

from apps.api import views
from apps.api.views import VolunteerProfileViewSet, OrganizationViewSet, OrganizationSignatoryViewSet, \
    AgreementTaskViewSet, AgreementTemplateViewSet, OfferAgreementTemplateViewSet, OrganizationAgreementTemplateViewSet, \
    VolunteerAbilityViewSet, OrgAbilityViewSet, RatingViewSet, CertificateViewSet, CertificateTemplateViewSet, \
    OfferCertificateTemplateViewSet, OrganizationCertificateTemplateViewSet, NewsViewSet, NewsThumbnailViewSet, \
    MetricsViewSet, VolunteerRatingViewSet, OrganizationRatingViewSet, OfferAgreementViewSet, AdminOfferViewSet, OfferRatingViewSet, \
    VolunteerThumbnailViewSet, OfferBulkViewSet, OfferCertificateViewSet
from apps.api.views import OfferViewSet
from apps.api.views import OrganizationThumbnailViewSet, OfferThumbnailViewSet
from apps.api.views import UserViewSet
from apps.api.views import AbilityViewSet
from apps.api.views import PromotedOfferViewSet
from apps.api.views import EducationViewSet, CategoryViewSet
from apps.api.views import OfferApplicationViewSet
from apps.api.views import OrganizationTypeViewSet
from apps.api.views import VolunteerApplicationViewSet
from apps.api.views import ApplicationViewSet
from apps.api.views import SessionViewSet
from apps.api.views import ObtainAuthToken
from apps.api.views import OrganizationOffersViewSet
from apps.api.views import SettingsViewSet
from apps.api.views import CategorySubscriptionViewSet
from apps.api.views import AgreementViewSet
from apps.api.routers import DocumentRouter, ApplicationRouter, DocumentTemplateRouter, AgreementTaskRouter, \
    RatingRouter, BulkRouter
from apps.crawlers.views import CrawlerView

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'v1/api/volunteers', VolunteerProfileViewSet, base_name='volunteer_profile')
router.register(r'v1/api/organizations', OrganizationViewSet, base_name='organization')
router.register(r'v1/api/offers', OfferViewSet, base_name='offers')
router.register(r'v1/api/admin-offers', AdminOfferViewSet, base_name='admin-offers')
router.register(r'v1/api/promoted-offers', PromotedOfferViewSet, base_name='promoted-offers')
router.register(r'v1/api/session', SessionViewSet, base_name='sessions')
router.register(r'v1/api/users', UserViewSet, base_name='users')
router.register(r'v1/api/abilities', AbilityViewSet, base_name='abilites')
router.register(r'v1/api/organization-abilities', OrgAbilityViewSet, base_name='orgabilites')
router.register(r'v1/api/education', EducationViewSet, base_name='education')
router.register(r'v1/api/organization-types', OrganizationTypeViewSet, base_name='organization-type')
router.register(r'v1/api/categories', CategoryViewSet, base_name='categories')
router.register(r'v1/api/settings', SettingsViewSet, base_name='settings')
router.register(r'v1/api/category-subscriptions', CategorySubscriptionViewSet, base_name='category-subscriptions')
router.register(r'v1/api/news', NewsViewSet, base_name='news')
router.register(r'v1/api/metrics', MetricsViewSet, base_name='metrics')

bulk_router = BulkRouter()
bulk_router.register(r'v1/api/offers-bulk', OfferBulkViewSet, base_name='offers-bulk')

rating_router = RatingRouter()
rating_router.register(r'v1/api/ratings', RatingViewSet, base_name='ratings')

document_template_router = DocumentTemplateRouter()
document_template_router.register(r'v1/api/agreement-templates', AgreementTemplateViewSet, base_name='agreement-templates')
document_template_router.register(r'v1/api/certificate-templates', CertificateTemplateViewSet, base_name='certificate-templates')

applications_router = ApplicationRouter()
applications_router.register(r'v1/api/applications', ApplicationViewSet, base_name='applications')

document_router = DocumentRouter()
document_router.register(r'v1/api/agreements', AgreementViewSet, base_name='agreements')
document_router.register(r'v1/api/certificates', CertificateViewSet, base_name='certificates')

agreement_task_router = AgreementTaskRouter()
agreement_task_router.register(r'v1/api/agreement-tasks', AgreementTaskViewSet, base_name='agreement-tasks')

offers_router = NestedSimpleRouter(router, 'v1/api/offers', lookup='offer')
offers_router.register(r'thumbnail', OfferThumbnailViewSet, base_name='offers-thumbnails')
offers_router.register(r'applications', OfferApplicationViewSet, base_name='offers-applications')
offers_router.register(r'agreements', OfferAgreementViewSet, base_name='offers-agreements')
offers_router.register(r'certificates', OfferCertificateViewSet, base_name='offers-certificates')
offers_router.register(r'agreement-template', OfferAgreementTemplateViewSet, base_name='offers-agreements-templates')
offers_router.register(r'certificate-template', OfferCertificateTemplateViewSet, base_name='offers-certificates-templates')
offers_router.register(r'ratings', OfferRatingViewSet, base_name='offers-ratings')

news_router = NestedSimpleRouter(router, 'v1/api/news', lookup='news')
news_router.register(r'thumbnail', NewsThumbnailViewSet, base_name='news-thumbnails')

volunteers_router = NestedSimpleRouter(router, 'v1/api/volunteers', lookup='volunteer')
volunteers_router.register(r'thumbnail', VolunteerThumbnailViewSet, base_name='volunteers-thumbnails')
volunteers_router.register(r'applications', VolunteerApplicationViewSet, base_name='volunteers-applications')
volunteers_router.register(r'abilities', VolunteerAbilityViewSet, base_name='volunteers-abilities')
volunteers_router.register(r'ratings', VolunteerRatingViewSet, base_name='volunteers-ratings')

orgs_router = NestedSimpleRouter(router, 'v1/api/organizations', lookup='org')
orgs_router.register(r'thumbnail', OrganizationThumbnailViewSet, base_name='organizations-thumbnails')
orgs_router.register(r'offers', OrganizationOffersViewSet, base_name='organizations-offers')
orgs_router.register(r'signatories', OrganizationSignatoryViewSet, base_name='organizations-signatories')
orgs_router.register(r'agreement-template', OrganizationAgreementTemplateViewSet, base_name='organizations-agreements-templates')
orgs_router.register(r'certificate-template', OrganizationCertificateTemplateViewSet, base_name='organizations-agreements-templates')
orgs_router.register(r'ratings', OrganizationRatingViewSet, base_name='organizations-ratings')

urlpatterns = patterns('',
    url(r'^v1/api/users/activate/(?P<activation_key>\w+)/$', UserViewSet.activate, name='registration_activate'),
    url(r'^v1/api/users/logout/$', UserViewSet.logout, name='api_logout'),
    url(r'^v1/api/offers/search/(?P<phrase>.+)/$', OfferViewSet.search, name='offer_search'),

    url(r'^', include(router.urls)),

    url(r'^', include(offers_router.urls)),
    url(r'^', include(volunteers_router.urls)),
    url(r'^', include(news_router.urls)),
    url(r'^', include(orgs_router.urls)),
    url(r'^', include(document_router.urls)),
    url(r'^', include(applications_router.urls)),
    url(r'^', include(document_template_router.urls)),
    url(r'^', include(agreement_task_router.urls)),
    url(r'^', include(rating_router.urls)),
    url(r'^', include(bulk_router.urls)),

    url(r'^v1/api/api-token-auth/', ObtainAuthToken.as_view()),
    url(r'^v1/api/check-auth/', views.CheckAuthView.as_view()),
    url(r'^v1/api/countries/', views.CountryListView.as_view()),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': instance_url() + '/#/'}),
    url(r'^accounts/profile/', 'apps.api.views.create_userprofile', name='userprofile'),
    url(r'^accounts/', include('allauth.urls')),

    #url(r'^v1/api/category-subscriptions/notify/$', CategorySubscriptionViewSet.notify, name='category_subscription_notify'),
    url(r'^crawlers(?P<url>.*)/$', CrawlerView.as_view())
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
