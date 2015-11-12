# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

import copy
import datetime
import sys
import zipfile
import StringIO
import unicodedata
from app_metrics.models import Gauge
from apps.api.certificates_states import CertificateStateFactory
from conf.certificate_keywords import certificate_get_keywords
from django.template.loader import render_to_string
from haystack.backends import SQ
from registration_api.utils import atomic_decorator, create_profile, get_settings
from .search_indexes import OfferIndex
from haystack.query import SearchQuerySet
from haystack import indexes
import os
from time import strptime
from django.conf import settings
from django.contrib.auth import get_user, logout as auth_logout
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Q, Avg
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User, Permission
from django.template import Template, Context
from django_countries import countries

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from notification import notify
from notification.models import NotificationTarget
from registration_api.models import RegistrationProfile
from rest_framework import generics
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes, detail_route, list_route
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from django.http import HttpResponseRedirect, Http404
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Count

from rest_framework.views import APIView
from rest_framework import status
from rest_framework import parsers
from rest_framework import renderers
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes as permission_decorator
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from registration_api import utils
from serializers import UserSerializer, UserWritableSerializer, AbilityReadableSerializer, \
    PromotedThumbnailOfferWritableSerializer, PromotedOfferListSerializer, EducationReadableSerializer, \
    CategoryReadableSerializer, ApplicationWritableSerializer, OrganizationTypeReadableSerializer, \
    ApplicationListSerializer, CheckAuthUserSerializer, SettingsListSerializer, OrganizationOffersListSerializer, \
    CategorySubscriptionSerializer, AgreementSerializer, SignedResourceSerializer, ApplicationDetailSerializer, \
    OrganizationSignatoryWritableSerializer, ApplicationsForOfferReadableSerializer, AgreementTaskSerializer, \
    AgreementTemplateSerializer, OrgAbilityReadableSerializer, TestimonialWritableSerializer, RatingWritableSerializer, \
    OrgTestimonialWritableSerializer, OrgRatingWritableSerializer, CertificateSerializer, CertificateTemplateSerializer, \
    ThumbnailNewsWritableSerializer, NewsWritableSerializer, NewsReadableSerializer, GaugeReadableSerializer, \
    VolunteerProfileListSerializer, OrganizationListSerializer, ThumbnailVolunteerProfileWritableSerializer, \
    OriginalThumbnailVolunteerProfileWritableSerializer, AdminOfferListSerializer

from .models import Organization, VolunteerProfile, UserProfile, Offer, LargeOfferThumbnail, OrganizationThumbnail, \
    OrganizationType, Ability, ResourceMetadata, Education, Category, Application, Settings, CategorySubscription, \
    Agreement, AgreementTemplate, SmallOfferThumbnail, OrganizationSignatory, AgreementTask, OrgAbility, Rating, \
    OrgRating, Certificate, CertificateTemplate, News, Testimonial, OrgTestimonial
from .serializers import OrganizationWritableSerializer, VolunteerProfileWritableSerializer, \
    VolunteerProfileReadableSerializer, OrganizationReadableSerializer, OfferListSerializer, \
    LargeThumbnailOfferReadableSerializer, SmallThumbnailOfferReadableSerializer,\
    LargeThumbnailOfferWritableSerializer, \
    SmallThumbnailOfferWritableSerializer, OfferDetailSerializer,\
    OriginalThumbnailOfferWritableSerializer, OfferGenericReadableSerializer, \
    OfferWritableSerializer, OriginalThumbnailOrganizationWritableSerializer, ThumbnailOrganizationWritableSerializer, \
    UserSerializer
from .helpers import PermissionHelperMixin, WrongRequestException, ThumbnailCreateAPIView, QuerySetChain, \
    ProfileNotExtendedException, NotFoundException, instance_url
from .filters import OfferListFilter, ApplicationListFilter, OrganizationOfferListFilter, OrganizationListFilter, \
    OfferAdminListFilter
from .field_packages import FieldPackageSetFactory, FieldPackage, ModelChecker
from .application_states import ApplicationStateFactory
from .agreements_states import AgreementStateFactory
from conf.agreement_keywords import agreement_get_keywords
from .offer_states import OfferStateFactory
from . import helpers
import logging
from weasyprint import HTML, CSS

log = logging.getLogger('apps')


class OrganizationViewSet(helpers.FieldPackageHelperMixin, helpers.OrganizationProfilePermissionHelperMixin,
        helpers.PermissionHelperMixin, helpers.UpdateAPIView, helpers.CreateAPIView, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationWritableSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )
    lookup_value_regex = '[0-9a-z]+'

    def list(self, request):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310
            assert request.user.has_perm('api.view_organization_list'), "You cannot view organization list"

            queryset = Organization.objects.all()
            filter = OrganizationListFilter(request.GET, queryset=queryset)
            serializer = OrganizationListSerializer(filter.qs, many=True)

            response = Response(serializer.data, status=status_code)
            self.debug_response(serializer.data, status_code)

            return response
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if pk == 'my':
                try:
                    if request.user.is_anonymous():
                        raise Http404('Anonymous user cannot manage organization')

                    assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                        "You are not a member of any organization"

                    pk = UserProfile.objects.get(user=request.user).organization_member.id
                except UserProfile.DoesNotExist:
                    raise Http404('User profile not found')

            queryset = Organization.objects.all()
            organization = get_object_or_404(queryset, pk=pk)

            serializer = OrganizationReadableSerializer(organization)

            self.debug_response(serializer.data, status_code)
            return Response(serializer.data, status=status_code)
        except Http404 as e:
            self.debug_response_error(404)
            raise e

    def create(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            user_profiles = UserProfile.objects.filter(user=request.user)

            assert not user_profiles or user_profiles[0].organization_member is None, "You already have an organization"

            self.assert_given_krs_nip(request)

            coordinator_id = request.user.id

            request.DATA['is_active'] = True
            request.DATA['coordinator'] = coordinator_id

            response, serializer = self.make_creation(request, self.serializer_class)

            if response.status_code in (status.HTTP_201_CREATED, 310):
                log.info("Created organization id={}".format(self.object.id))

                response.status_code = status.HTTP_201_CREATED

                self.relate_org_with_user_profile(serializer, user_profiles)
                log.info("Related organization id={} with user profile id={}".format(self.object.id, user_profiles[0]))
                self.add_permission_to_coordinator(coordinator_id)
                log.info("Added permission to coordinator id={}".format(coordinator_id))
                self.add_permission_to_logged_user(request,
                    ('create_offer', 'edit_my_offer', 'deactivate_my_offer', 'publish_my_offer',
                     'deactivate_my_organization_profile', 'edit_my_organization_profile',))
                log.info("Added permission to logged user id={}".format(request.user.id))

            self.debug_response(response.data, response.status_code)
            return response
        except WrongRequestException as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)

    #private
    def relate_org_with_user_profile(self, serializer, user_profiles):
        org = Organization.objects.get(pk=serializer.data['id'])
        user_profiles[0].organization_member = org
        user_profiles[0].save()

    #private
    def add_permission_to_coordinator(self, coordinator_id):
        permission = Permission.objects.get(codename='accept_application')
        coordinator = User.objects.get(pk=coordinator_id)
        coordinator.user_permissions.add(permission)
        coordinator.save()

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            if kwargs['pk'] == 'my':
                assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                    "You are not a member of any organization"

                kwargs['pk'] = UserProfile.objects.get(user=request.user).organization_member.id
                self.kwargs = kwargs

            self.debug_MY_id_translated_to(kwargs['pk'])

            class DataChange(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    serializer = OrganizationWritableSerializer
                    profile = Organization.objects.get(pk=kwargs['pk'])

                    viewset.assert_has_permissions_to_edit_my_organization_profile(profile, request.user)
                    viewset.assert_given_krs_nip(request)

                    self.change_accept_application_permission_owner(profile, request)

                    response = viewset.make_update(kwargs, serializer, request)
                    log.info("Updated organization id={}".format(kwargs['pk']))

                    viewset.debug_response(response.data, response.status_code)

                    return response

                #private
                def change_accept_application_permission_owner(self, profile, request):
                    permission = Permission.objects.get(codename='accept_application')
                    previous_coordinator = profile.coordinator
                    previous_coordinator.user_permissions.remove(permission)
                    previous_coordinator.save()
                    next_coordinator = User.objects.get(pk=request.DATA['coordinator'])
                    next_coordinator.user_permissions.add(permission)
                    next_coordinator.save()

                    log.info("Changed owner of ACCEPT APPLICATION permission from user name={} to user name={}".format(
                        previous_coordinator,
                        next_coordinator
                    ))

            class StatusChange(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    serializer = OrganizationWritableSerializer
                    profile = Organization.objects.get(pk=kwargs['pk'])

                    viewset.assert_has_permissions_to_deactivate_my_organization_profile(profile, request.user)

                    response = viewset.make_update(kwargs, serializer, request)
                    log.info("Updated organization status for id={}".format(kwargs['pk']))

                    viewset.debug_response(response.data, response.status_code)

                    return response

            class AutoSkipGrant(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    user = Organization.objects.get(pk=kwargs['pk']).coordinator

                    assert request.user.has_perm('api.review_any_offer'), "You don't have such permission to grant this organization"

                    if request.DATA['can_autoskip'] is True and not user.has_perm('api.skip_review'):
                        permission = Permission.objects.get(codename='skip_review')
                        user.user_permissions.add(permission)
                        user.save()
                    elif request.DATA['can_autoskip'] is False and user.has_perm('api.skip_review'):
                        permission = Permission.objects.get(codename='skip_review')
                        user.user_permissions.remove(permission)
                        user.save()
                    else:
                        raise AssertionError("Invalid operation")

                    return Response({'can_autoskip': request.DATA['can_autoskip']})


            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': DataChange,
                        'required': ('type', 'coordinator', 'fullname', 'shortname', 'street', 'house_number',
                            'zipcode',  'city',  'country',),
                        'allowed_not_required': ('nip', 'krs', 'apartment_number', 'district', 'province',
                            'phonenumber', 'description',)
                    },
                    {
                        'class': StatusChange,
                        'required': ('is_active',),
                        'allowed_not_required': ()
                    },
                    {
                        'class': AutoSkipGrant,
                        'required': ('can_autoskip',),
                        'allowed_not_required': ()
                    }
                )
            packages = RequiredPackageSet.make()
            fitting_field_package = self.get_fitting_field_package(packages, request.DATA)
            log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
            return fitting_field_package.update(self, request, args, kwargs)
        except ValidationError as err:
            self.debug_response_error(400)
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': "Bad credentials"}, status=status.HTTP_403_FORBIDDEN)
        except WrongRequestException as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    #private
    def assert_given_krs_nip(self, request):
        type = OrganizationType.objects.get(pk=request.DATA['type'])
        if type.is_krs_required is True and 'krs' not in request.DATA:
            raise WrongRequestException("KRS required")
        if type.is_nip_required is True and 'nip' not in request.DATA:
            raise WrongRequestException("NIP required")

    def destroy(self, request, *args, **kwargs):
        serializer = OrganizationWritableSerializer

        try:
            self.debug_request(request)

            kwargs['partial'] = True
            profile = Organization.objects.get(pk=kwargs['pk'])

            self.prevent_modifying_any_field(request)

            self.assert_has_permissions_to_deactivate_my_organization_profile(profile, request.user)

            request.DATA['is_active'] = False

            response = self.make_update(kwargs, serializer, request)
            log.info("Destroyed organization id={}".format(kwargs['pk']))

            self.debug_response(response.data, response.status_code)

            return response
        except ValidationError as err:
            self.debug_response_error(400)
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': "Bad credentials"}, status=status.HTTP_403_FORBIDDEN)
        except WrongRequestException:
            self.debug_response_error(400)
            return Response({'detail': "Wrong request data"}, status=status.HTTP_400_BAD_REQUEST)


class OrganizationSignatoryViewSet(helpers.FieldPackageHelperMixin, helpers.CreateAPIView, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = OrganizationSignatory.objects.all()
    serializer_class = OrganizationSignatoryWritableSerializer

    def create(self, request, *args, **kwargs):
        self.debug_request(request)

        org_pk = kwargs['org_pk']
        if org_pk == 'my':
            assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                "You are not a member of any organization"

            org_pk = UserProfile.objects.get(user=request.user).organization_member.id
            self.debug_MY_id_translated_to(org_pk)

        request.POST = request.POST.copy()
        request.DATA['organization'] = org_pk

        response = super(OrganizationSignatoryViewSet, self).create(request, *args, **kwargs)
        if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
            log.info("Created organization signatory id={} for org id={}".format(self.object.id, org_pk))
        self.debug_response(response.data, response.status_code)
        return response

    def list(self, request, org_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if org_pk == 'my':
                assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                    "You are not a member of any organization"

                org_pk = UserProfile.objects.get(user=request.user).organization_member.id
                self.debug_MY_id_translated_to(org_pk)

            queryset = OrganizationSignatory.objects.filter(organization=org_pk)
            serializer = self.serializer_class(queryset, many=True)

            response = Response(serializer.data, status=status_code)
            self.debug_response(serializer.data, status_code)

            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Bad credentials"}, status=status.HTTP_404_NOT_FOUND)


class AgreementTaskViewSet(helpers.FieldPackageHelperMixin, helpers.UpdateAPIView, helpers.CreateAPIView,
        helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = AgreementTask.objects.all()
    serializer_class = AgreementTaskSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer_class = AgreementTaskSerializer
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            offer_id = kwargs['lookup_one_value']
            volunteer_id = kwargs['lookup_two_value']

            task = AgreementTask.objects.get(offer=offer_id, volunteer_id=volunteer_id)
            serializer = serializer_class(task)

            self.debug_response(serializer.data, status_code)
            return Response(serializer.data, status=status_code)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Agreement task doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FieldPackage,
                        'required': ('offer', 'body',),
                        'allowed_not_required': ('volunteer',)
                    },
                )
            assert RequiredPackageSet.make()[0].fits_to(request.DATA), "Invalid package set"

            volunteer = request.DATA['volunteer'] if 'volunteer' in request.DATA else None
            task = AgreementTask.objects.get(offer=request.DATA['offer'], volunteer=volunteer)
            self.kwargs['pk'] = task.id

            response = self.make_update(kwargs, self.serializer_class, request)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Updated agreement tasks for offer id={} volunteer id={}".format(
                    self.object.offer,
                    self.object.volunteer if self.object.volunteer is not None else "None"
                ))
            self.debug_response(response.data, response.status_code)
            return response
        except AssertionError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Given offer or volunteer doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FieldPackage,
                        'required': ('offer', 'body',),
                        'allowed_not_required': ('volunteer',)
                    },
                )
            assert RequiredPackageSet.make()[0].fits_to(request.DATA), "Invalid package set"

            volunteer = request.DATA['volunteer'] if 'volunteer' in request.DATA else None
            assert not AgreementTask.objects.filter(offer=request.DATA['offer'], volunteer=volunteer)\
                .exists(), "Given record exists"

            response, serializer = self.make_creation(request, self.serializer_class)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Created agreement tasks for offer id={} volunteer id={}".format(
                    self.object.offer,
                    self.object.volunteer if self.object.volunteer is not None else "None"
                ))
            self.debug_response(response.data, response.status_code)
            return response
        except AssertionError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Given offer or volunteer doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


class OfferAgreementViewSet(helpers.FieldPackageHelperMixin, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer

    def list(self, request, offer_pk=None):
        self.debug_request(request)

        status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

        queryset = Agreement.objects.filter(offer=offer_pk)
        serializer = self.serializer_class(queryset, many=True)

        response = Response(serializer.data, status=status_code)
        self.debug_response(serializer.data, status_code)

        return response


class OfferCertificateViewSet(helpers.FieldPackageHelperMixin, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def list(self, request, offer_pk=None):
        self.debug_request(request)

        status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

        queryset = Certificate.objects.filter(offer=offer_pk)
        serializer = self.serializer_class(queryset, many=True)

        response = Response(serializer.data, status=status_code)
        self.debug_response(serializer.data, status_code)

        return response


class OfferApplicationViewSet(helpers.FieldPackageHelperMixin, helpers.CreateAPIView, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationWritableSerializer
    lookup_value_regex = '[0-9a-z]+'

    def retrieve(self, request, pk=None, offer_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            state = ApplicationStateFactory.make_for_code(pk)
            apps = state.get_applications_for_offer(offer_pk)

            serializer = ApplicationsForOfferReadableSerializer(apps, many=True)

            self.debug_response(serializer.data, status_code)
            return Response(serializer.data, status=status_code)
        except KeyError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Http404 as e:
            self.debug_response_error(404)
            raise e

    def create(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            request.POST = request.POST.copy()

            self.prevent_modifying_any_field(request)
            self.assert_has_extended_volunteer_profile(request)

            offer_pk = kwargs['offer_pk']

            volunteer = VolunteerProfile.objects.get(user=request.user.id)
            volunteer_pk = volunteer.id

            request.DATA['offer'] = offer_pk
            request.DATA['volunteer'] = volunteer_pk
            request.DATA['message'] = ""
            request.DATA['status'] = ApplicationStateFactory.PENDING_TO_REVIEW

            response, serializer = self.make_creation(request, self.serializer_class)

            if response.status_code in (status.HTTP_201_CREATED, 310):
                log.info("Created application id={} for offer id={} for volunteer id={}".format(
                    self.object.id,
                    offer_pk,
                    volunteer_pk
                ))

                setts = Settings.objects.get(settings__contains=['instance_url'])

                data = {
                    'offer_id': offer_pk,
                    'offer_title': Offer.objects.get(pk=offer_pk).title,
                    'first_name': Offer.objects.get(pk=offer_pk).publishing_organization.coordinator.first_name,
                    'last_name': Offer.objects.get(pk=offer_pk).publishing_organization.coordinator.last_name,
                    'application_id': self.object.id,
                    'volunteer_id': volunteer_pk,
                    'volunteer_first_name': request.user.first_name,
                    'volunteer_last_name': request.user.last_name,
                    'volunteer_email': request.user.email,
                    'volunteer_age': int(volunteer.age().days // 365.25),
                    'volunteer_phone_number': volunteer.phonenumber,
                    'volunteer_about': volunteer.about,
                    'volunteer_abilities': [ability.name for ability in volunteer.abilities.all()],
                    'instance_url': instance_url(),
                    'instance_name': setts.settings['instance_name']
                }

                coordinator = Offer.objects.get(pk=offer_pk).publishing_organization.coordinator
                notify('application_new', data, coordinator)
                log.info("Notified coordinator id={}".format(coordinator))

            self.debug_response(response.data, response.status_code)
            return response
        except ProfileNotExtendedException:
            self.debug_response_error(440)
            return Response({'detail': "Extend your volunteer profile"}, 440)

    @list_route()
    def check(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return Response({'message': 'User is anonymous'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            offer_pk = kwargs['offer_pk']
            volunteer_pk = VolunteerProfile.objects.get(user=request.user.id).id
            application = Application.objects.get(volunteer_id=volunteer_pk, offer_id=offer_pk)

            return Response({'application': True}, status=status.HTTP_200_OK)
        except Application.DoesNotExist:
            return Response({'application': False}, status=status.HTTP_200_OK)
        except VolunteerProfile.DoesNotExist:
            return Response({'message': 'User is not a volunteer'}, status=status.HTTP_400_BAD_REQUEST)

    @list_route()
    def count(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310
            offer_pk = kwargs['offer_pk']

            apps = Application.objects.filter(offer_id=offer_pk).values('status').annotate(count=Count('status'))
            stats = {s[0]: s[1] for s in ApplicationStateFactory.get_statuses_choice_list()}
            log.debug(stats)
            log.debug(type(stats))
            response = {value: 0 for value in stats.itervalues()}

            for app in apps:
                response[stats[app['status']]] = app['count']

            self.debug_response(response, status_code)
            return Response(response, status=status_code)
        except KeyError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Http404 as e:
            self.debug_response_error(404)
            raise e


class ApplicationViewSet(helpers.ApplicationPermissionHelperMixin, helpers.FieldPackageHelperMixin,
        helpers.UpdateAPIView, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Application.objects.all()
    serializer = ApplicationWritableSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer_class = ApplicationDetailSerializer
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            offer_id = kwargs['lookup_one_value']
            volunteer_id = kwargs['lookup_two_value']

            application = Application.objects.get(offer=offer_id, volunteer_id=volunteer_id)
            serializer = serializer_class(application)

            self.debug_response(serializer.data, status_code)
            return Response(serializer.data, status=status_code)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Application doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        self.debug_request(request)

        class StatusChange(FieldPackage):
            def update(self, viewset, request, args, kwargs):
                serializer = ApplicationWritableSerializer
                kwargs['partial'] = True

                assert type(request.DATA['id']) is list, "Provide list of ids"
                responses = {}
                status_code = status.HTTP_201_CREATED

                ids = request.DATA['id']
                del request.DATA['id']
                for id in ids:
                    try:
                        application = Application.objects.get(pk=id)
                        viewset.kwargs['pk'] = id
                        kwargs['partial'] = True

                        viewset.assert_has_permissions_to_accept_my_application(application, request.user)

                        if request.DATA['status'] is ApplicationStateFactory.ACCEPTED:
                            notify('application_accept', {
                                'offer_id': application.offer.id,
                                'message': request.DATA['message'] if 'message' in request.DATA else "",
                                'instance_url': instance_url()
                            }, application.volunteer.user)
                            log.info("Notified accepted user id={}".format(application.volunteer.user))
                        elif request.DATA['status'] is ApplicationStateFactory.REJECTED:
                            assert 'message' in request.DATA, "Provide message"
                            notify('application_reject', {
                                'offer_id': application.offer.id,
                                'message': request.DATA['message'],
                                'instance_url': instance_url()
                            }, application.volunteer.user)
                            log.info("Notified rejected user id={}".format(application.volunteer.user))

                        request.DATA['last_modified_at'] = datetime.datetime.now()

                        response = viewset.make_update(kwargs, serializer, request)
                        if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                            log.info("Status of application id={} changed to {}".format(viewset.kwargs['pk'], request.DATA['status']))

                        if response.status_code is not status.HTTP_201_CREATED:
                            status_code = response.status_code

                        responses[id] = response.data
                    except ValidationError as e:
                        viewset.debug_response_error(400)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': e.message, 'code': status.HTTP_400_BAD_REQUEST}
                    except PermissionHelperMixin.AccessDeniedException:
                        viewset.debug_response_error(403)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': "Bad credentials", 'code': status.HTTP_403_FORBIDDEN}
                    except AssertionError as e:
                        viewset.debug_response_error(400)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': e.message, 'code': status.HTTP_400_BAD_REQUEST}
                    except ObjectDoesNotExist as e:
                        viewset.debug_response_error(404)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': e.message, 'code': status.HTTP_404_NOT_FOUND}
                    except WrongRequestException as e:
                        viewset.debug_response_error(400)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': e.message, 'code': status.HTTP_400_BAD_REQUEST}

                viewset.debug_response(responses, status_code)
                return Response(responses, status_code)

        class RequiredPackageSet(FieldPackageSetFactory):
            packages_having_regard_to_order = (
                {
                    'class': StatusChange,
                    'required': ('status', 'id'),
                    'allowed_not_required': ('message',)
                },
            )
        packages = RequiredPackageSet.make()
        fitting_field_package = self.get_fitting_field_package(packages, request.DATA)
        log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
        return fitting_field_package.update(self, request, args, kwargs)


class RatingViewSet(helpers.FieldPackageHelperMixin, helpers.CreateAPIView, helpers.UpdateAPIView, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialWritableSerializer

    def create(self, request, *args, **kwargs):
        transaction.set_autocommit(False)

        try:
            self.debug_request(request)

            class RatingFieldPackage(FieldPackage):
                def create(self, viewset, request, *args, **kwargs):
                    status_code = status.HTTP_201_CREATED if viewset.has_created_org_or_volunteer_profile(request) else 310

                    self.assert_proper_request(request)
                    self.assert_has_permissions(request)
                    self.assert_rating_does_not_exist(request)
                    self.assert_rating_in_range(request)
                    # self.assert_generated_agreement(request)

                    request.DATA['created_by'] = request.user.id

                    abilities = request.DATA['abilities']
                    del request.DATA['abilities']

                    can_create_testimonial = False
                    if 'testimonial' in request.DATA:
                        testimonial = request.DATA['testimonial']
                        del request.DATA['testimonial']
                        can_create_testimonial = True

                    response = self.create_ratings(viewset, abilities, request)
                    del response.data['ability'], response.data['rating']

                    if can_create_testimonial:
                        response = self.create_testimonial(viewset, request, testimonial)
                        response.data['testimonial'] = response.data['body']
                        del response.data['body']

                    transaction.commit()
                    self.log_creation(request)

                    response.data['abilities'] = abilities

                    viewset.debug_response(response.data, status_code)
                    return response

                #private
                def create_ratings(self, viewset, abilities, request):
                    for ability in abilities:
                        request.DATA['ability'] = ability['id']
                        request.DATA['rating'] = ability['rating']

                        response, serializer = viewset.make_creation(request, self.rating_serializer_class)
                        if response.status_code not in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                            raise IntegrityError("Error while creating rating volunteer={} ability={}".format(
                                request.DATA['volunteer'],
                                request.DATA['ability']
                            ))

                    return response

                #private
                def assert_proper_request(self, request):
                    assert type(request.DATA['abilities']) is list, "Invalid package set"
                    assert len(request.DATA['abilities']) > 0, "Invalid package set"

                    class NestedPackageSet(FieldPackageSetFactory):
                        packages_having_regard_to_order = (
                            {
                                'class': FieldPackage,
                                'required': ('id', 'rating',),
                                'allowed_not_required': ()
                            },
                        )

                    for ability in request.DATA['abilities']:
                        assert type(ability) is dict, "Invalid package set"
                        assert NestedPackageSet.make()[0].fits_to(ability), "Invalid package set"

                #private
                def assert_rating_in_range(self, request):
                    settings = Settings.objects.get(settings__contains=['rating_treshold'])
                    treshold = settings.settings['rating_treshold']
                    for ability in request.DATA['abilities']:
                        assert 0 < ability['rating'] <= int(treshold), "Rating should be in range of 1.." + treshold

                #private
                def create_testimonial(self, viewset, request, testimonial):
                    del request.DATA['ability'], request.DATA['rating']
                    request.DATA['body'] = testimonial
                    request.DATA['is_public'] = False
                    response, serializer = viewset.make_creation(request, self.testimonial_serializer_class)
                    if response.status_code not in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.debug(response.data)
                        raise IntegrityError("Error while creating testimonial: " + response.data['detail'])
                    return response

            class VolunteerRating(RatingFieldPackage):
                def __init__(self, *args, **kwargs):
                    super(RatingFieldPackage, self).__init__(*args, **kwargs)
                    self.testimonial_serializer_class = TestimonialWritableSerializer
                    self.rating_serializer_class = RatingWritableSerializer

                #private
                def assert_rating_does_not_exist(self, request):
                    assert len(Rating.objects.filter(volunteer=request.DATA['volunteer'], offer=request.DATA['offer'])) is 0, \
                        "Rating exists"

                #private
                def assert_generated_agreement(self, request):
                    assert Agreement.objects.filter(volunteer=request.DATA['volunteer'], offer=request.DATA['offer']).exists(), \
                        "You haven't even generated agreement!"

                #private
                def assert_has_permissions(self, request):
                    apps = Application.objects.filter(volunteer=request.DATA['volunteer'], offer=request.DATA['offer'],
                        status=ApplicationStateFactory.ACCEPTED)
                    assert apps.exists(), "You cannot rate volunteer if they hadn't applied to this offer"

                    offer = Offer.objects.get(pk=request.DATA['offer'])
                    assert offer.publishing_organization.coordinator.id == request.user.id, "Only coordinator can rate volunteers"

                #private
                def log_creation(self, request):
                    log.info("Created rating for offer id={} for volunteer id={}".format(
                        request.DATA['offer'],
                        request.DATA['volunteer']
                    ))

            class OrganizationRating(RatingFieldPackage):
                def __init__(self, *args, **kwargs):
                    super(RatingFieldPackage, self).__init__(*args, **kwargs)
                    self.testimonial_serializer_class = OrgTestimonialWritableSerializer
                    self.rating_serializer_class = OrgRatingWritableSerializer

                #private
                def assert_rating_does_not_exist(self, request):
                    assert len(OrgRating.objects.filter(organization=request.DATA['organization'], offer=request.DATA['offer'])) is 0, \
                        "Rating exists"

                #private
                def assert_generated_agreement(self, request):
                    volunteer = VolunteerProfile.objects.get(user=request.user)
                    offer = Offer.objects.get(pk=request.DATA['offer'])
                    assert offer.publishing_organization.id is request.DATA['organization'], \
                        "Given organization is not a publisher of this offer"

                    assert Agreement.objects.filter(volunteer=volunteer, offer=request.DATA['offer']).exists(), \
                        "You haven't even generated agreement!"

                #private
                def log_creation(self, request):
                    log.info("Created rating for offer id={} for organization id={}".format(
                        request.DATA['offer'],
                        request.DATA['organization']
                    ))

                #private
                def assert_has_permissions(self, request):
                    apps = Application.objects.filter(volunteer=VolunteerProfile.objects.get(user=request.user.id).id,
                        offer=request.DATA['offer'], status=ApplicationStateFactory.ACCEPTED)
                    assert apps.exists(), "You cannot rate organization if you hadn't applied to this offer"

                    offer = Offer.objects.get(pk=request.DATA['offer'])
                    assert offer.publishing_organization.id == request.DATA['organization'], "This organization is not owner of this offer"

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': VolunteerRating,
                        'required': ('volunteer', 'offer', 'abilities',),
                        'allowed_not_required': ('testimonial',)
                    },
                    {
                        'class': OrganizationRating,
                        'required': ('organization', 'offer', 'abilities',),
                        'allowed_not_required': ('testimonial',)
                    },
                )

            packages = RequiredPackageSet.make()
            fitting_field_package = self.get_fitting_field_package(packages, request.DATA)
            log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
            return fitting_field_package.create(self, request, *args, **kwargs)
        except AssertionError as e:
            transaction.rollback()
            log.error("Rollback in RatingViewSet.create")
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except IntegrityError as e:
            transaction.rollback()
            log.error("Rollback in RatingViewSet.create")
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            transaction.rollback()
            return Response({'detail': 'Uncaught error! Message: ' + e.message}, status=status.HTTP_417_EXPECTATION_FAILED)
        finally:
            transaction.set_autocommit(True)

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class PrivacyChange(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    viewset.queryset = self.queryset
                    kwargs['partial'] = True

                    testimonial = self.get_testimonial()
                    viewset.kwargs['pk'] = testimonial.id

                    self.assert_is_ratee(request, testimonial)

                    if request.DATA['is_public'] is True:
                        request.DATA['published_at'] = datetime.datetime.now()
                    else:
                        request.DATA['depublished_at'] = datetime.datetime.now()

                    response = viewset.make_update(kwargs, self.testimonial_serializer_class, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        self.log_creation(request)

                    viewset.debug_response(response.data, response.status_code)
                    return response

            class VolPrivacyChange(PrivacyChange):
                testimonial_serializer_class = TestimonialWritableSerializer
                queryset = Testimonial.objects.all()

                def get_testimonial(self):
                    return Testimonial.objects.get(volunteer=request.DATA['volunteer'], offer=request.DATA['offer'])

                def assert_is_ratee(self, request, testimonial):
                    assert request.user.id is testimonial.volunteer.user.id, "You are not a target in this rating"

                def log_creation(self, request):
                    log.info("Status of testimonial volunteer={} offer={} changed to {}" \
                            .format(request.DATA['volunteer'], request.DATA['offer'], request.DATA['is_public']))

            class OrgPrivacyChange(PrivacyChange):
                testimonial_serializer_class = OrgTestimonialWritableSerializer
                queryset = OrgTestimonial.objects.all()

                def get_testimonial(self):
                    return OrgTestimonial.objects.get(organization=request.DATA['organization'], offer=request.DATA['offer'])

                def assert_is_ratee(self, request, testimonial):
                    assert request.user.id is testimonial.organization.coordinator.id, "You are not a target in this rating"

                def log_creation(self, request):
                    log.info("Status of testimonial organization={} offer={} changed to {}" \
                            .format(request.DATA['organization'], request.DATA['offer'], request.DATA['is_public']))

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': VolPrivacyChange,
                        'required': ('volunteer', 'offer', 'is_public',),
                        'allowed_not_required': ()
                    },
                    {
                        'class': OrgPrivacyChange,
                        'required': ('organization', 'offer', 'is_public',),
                        'allowed_not_required': ()
                    },
                )
            packages = RequiredPackageSet.make()
            fitting_field_package = self.get_fitting_field_package(packages, request.DATA)
            log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
            return fitting_field_package.update(self, request, args, kwargs)
        except WrongRequestException as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Given rating doesn't exist"}, status=status.HTTP_404_NOT_FOUND)


class VolunteerApplicationViewSet(helpers.FieldPackageHelperMixin, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationListSerializer

    def list(self, request, volunteer_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if volunteer_pk == 'my':
                volunteer_pk = VolunteerProfile.objects.get(user=request.user).id
                self.debug_MY_id_translated_to(volunteer_pk)

            queryset = Application.objects.filter(volunteer=volunteer_pk)
            filter = ApplicationListFilter(request.GET, queryset=queryset)

            serializer = self.serializer_class(filter.qs, many=True)

            response = Response(serializer.data, status=status_code)
            self.debug_response(serializer.data, status_code)

            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Bad credentials"}, status=status.HTTP_404_NOT_FOUND)

    @list_route()
    def count(self, request, volunteer_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310
            if volunteer_pk == 'my':
                volunteer_pk = VolunteerProfile.objects.get(user=request.user).id
                self.debug_MY_id_translated_to(volunteer_pk)

            apps = Application.objects.filter(volunteer=volunteer_pk).values('status').annotate(count=Count('status'))
            stats = {s[0]: s[1] for s in ApplicationStateFactory.get_statuses_choice_list()}
            log.debug(stats)
            log.debug(type(stats))
            response = {value: 0 for value in stats.itervalues()}

            for app in apps:
                response[stats[app['status']]] = app['count']

            self.debug_response(response, status_code)
            return Response(response, status=status_code)
        except KeyError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Http404 as e:
            self.debug_response_error(404)
            raise e


class VolunteerRatingViewSet(helpers.FieldPackageHelperMixin, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Rating.objects.all()

    def list(self, request, volunteer_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if volunteer_pk == 'my':
                volunteer = VolunteerProfile.objects.get(user=request.user)
                self.debug_MY_id_translated_to(volunteer_pk)
            else:
                volunteer = VolunteerProfile.objects.get(pk=volunteer_pk)

            ratings = Rating.objects.filter(volunteer=volunteer)\
                .values('volunteer', 'offer', 'created_by', 'offer__publishing_organization__fullname',
                        'offer__publishing_organization__id').annotate(rating=Avg('rating'))
            ratings = list(ratings)

            for rating in ratings:
                testimonials = Testimonial.objects \
                    .filter(volunteer=rating['volunteer'], offer=rating['offer'], created_by=rating['created_by'])
                rating['testimonial'] = testimonials.first().body if testimonials.exists() else None
                rating['is_public'] = testimonials.first().is_public if testimonials.exists() else None
                rating['organization_fullname'] = rating['offer__publishing_organization__fullname']
                rating['organization_id'] = rating['offer__publishing_organization__id']
                del rating['offer__publishing_organization__fullname']
                del rating['offer__publishing_organization__id']

            response = Response(ratings, status=status_code)
            self.debug_response(ratings, status_code)

            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Not found"}, status=status.HTTP_404_NOT_FOUND)


class VolunteerAbilityViewSet(helpers.FieldPackageHelperMixin, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Ability.objects.all()
    serializer_class = AbilityReadableSerializer

    def list(self, request, volunteer_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if volunteer_pk == 'my':
                volunteer = VolunteerProfile.objects.get(user=request.user)
                self.debug_MY_id_translated_to(volunteer_pk)
            else:
                volunteer = VolunteerProfile.objects.get(pk=volunteer_pk)

            all = Ability.objects.all()
            choosen = volunteer.abilities.all()
            serializer = self.serializer_class(all, many=True)
            data = serializer.data

            for entry in data:
                entry['choosen'] = False

            for entry_choosen in choosen:
                for entry_all in data:
                    if entry_all['id'] is entry_choosen.id:
                        entry_all['choosen'] = True

            response = Response(data, status=status_code)
            self.debug_response(data, status_code)

            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Not found"}, status=status.HTTP_404_NOT_FOUND)


class VolunteerProfileViewSet(helpers.FieldPackageHelperMixin, helpers.VolunteerProfilePermissionHelperMixin,
        helpers.PermissionHelperMixin, helpers.UpdateAPIView, helpers.CreateAPIView, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = VolunteerProfile.objects.all()
    serializer_class = VolunteerProfileListSerializer
    lookup_value_regex = '[0-9a-z]+'

    def list(self, request):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310
            assert request.user.has_perm('api.view_volunteer_list'), "You cannot view volunteer list"

            queryset = VolunteerProfile.objects.all()
            serializer = self.serializer_class(queryset, many=True)

            response = Response(serializer.data, status=status_code)
            self.debug_response(serializer.data, status_code)

            return response
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)

    def create(self, request, *args, **kwargs):
        try:
            class PrimaryProfile(FieldPackage):
                def create(self, viewset, request, *args, **kwargs):
                    viewset.debug_request(request)

                    self.assert_has_not_profile_yet(request)
                    self.assert_is_older_than_13(request)

                    request.POST = request.POST.copy()
                    request.DATA['user'] = request.user.id
                    response, serializer = viewset.make_creation(request, VolunteerProfileWritableSerializer)
                    if response.status_code == 310:
                        response.status_code = 210

                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Volunteer profile created for user id={}".format(request.user.id))

                    return response

                #private
                def assert_has_not_profile_yet(self, request):
                    volunteer_profile = VolunteerProfile.objects.filter(user=request.user)
                    assert len(volunteer_profile) is 0, "You already have a volunteer profile"

                #private
                def assert_is_older_than_13(self, request):
                    delta = datetime.datetime.now() - datetime.datetime.strptime(request.DATA['birthday'], '%Y-%m-%d')
                    years = delta.days / 365.25
                    assert years >= 13, "You must have 13 years old or greater"


            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': PrimaryProfile,
                        'required': ('birthday', 'about', 'abilities', 'education',),
                        'allowed_not_required': ('gender', 'phonenumber', 'abilities_description', )
                    },
                )

            packages = RequiredPackageSet.make()
            fitting_field_package = self.get_fitting_field_package(packages, request.DATA)
            log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
            return fitting_field_package.create(self, request, *args, **kwargs)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if pk == 'my':
                pk = VolunteerProfile.objects.get(user=request.user).id

            queryset = VolunteerProfile.objects.all()
            user = get_object_or_404(queryset, pk=pk)
            serializer = VolunteerProfileReadableSerializer(user)
            response = Response(serializer.data, status=status_code)

            self.debug_response(serializer.data, status_code)
            return response
        except Http404 as e:
            self.debug_response_error(404)
            raise e

    def update(self, request, *args, **kwargs):
        serializer = VolunteerProfileWritableSerializer

        try:
            self.debug_request(request)

            class Profile(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    if kwargs['pk'] == 'my':
                        kwargs['pk'] = VolunteerProfile.objects.get(user=request.user).id
                        viewset.kwargs = kwargs
                        viewset.debug_MY_id_translated_to(kwargs['pk'])

                    profile = VolunteerProfile.objects.get(pk=kwargs['pk'])

                    viewset.assert_has_permissions_to_edit_my_volunteer_profile(profile, request.user)
                    self.perform_assertions(request, profile)

                    response = viewset.make_update(kwargs, serializer, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Updated volunteer profile id={}".format(kwargs['pk']))
                    viewset.debug_response(response.data, response.status_code)

                    return response

            class PrimaryProfile(Profile):
                #private
                def perform_assertions(self, request, profile):
                    pass

            class ExtendedProfile(Profile):
                #private
                def perform_assertions(self, request, profile):
                    self.assert_given_proof_number(request, profile)

                #private
                def assert_given_proof_number(self, request, profile):
                    if profile.is_older_or_equal_to(18):
                        assert 'proof_number' in request.DATA, "Provide proof number"

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': PrimaryProfile,
                        'required': ('birthday', 'about', 'abilities', 'education',),
                        'allowed_not_required': ('gender', 'phonenumber', 'abilities_description', )
                    },
                    {
                        'class': ExtendedProfile,
                        'required': ('pesel', 'street', 'house_number', 'apartment_number', 'zipcode', 'city', 'country',),
                        'allowed_not_required': ('proof_number', 'proof_type',)
                    }
                )

            self.packages = RequiredPackageSet.make()
            fitting_field_package = self.get_fitting_field_package(self.packages, request.DATA)
            log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
            return fitting_field_package.update(self, request, args, kwargs)
        except ValidationError as e:
            self.debug_response_error(400)
            return Response(e.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': "Bad credentials"}, status=status.HTTP_403_FORBIDDEN)
        except AssertionError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except WrongRequestException:
            self.debug_response_error(400)
            return Response({'detail': "Wrong request data"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route()
    def agreements(self, request, pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if pk == 'my':
                profile = VolunteerProfile.objects.get(user=request.user)
            else:
                profile = VolunteerProfile.objects.get(pk=pk)
                if not profile.user == request.user:
                    raise PermissionHelperMixin.AccessDeniedException()

            queryset = Agreement.objects.filter(volunteer=profile)
            serializer = AgreementSerializer(queryset, many=True)
            response = Response(serializer.data, status=status_code)
            self.debug_response(serializer.data, status_code)
            return response
        except Http404 as e:
            self.debug_response_error(404)
            raise e

    @detail_route()
    def certificates(self, request, pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if pk == 'my':
                profile = VolunteerProfile.objects.get(user=request.user)
            else:
                profile = VolunteerProfile.objects.get(pk=pk)
                if not profile.user == request.user:
                    raise PermissionHelperMixin.AccessDeniedException()

            queryset = Certificate.objects.filter(volunteer=profile)
            serializer = CertificateSerializer(queryset, many=True)
            response = Response(serializer.data, status=status_code)
            self.debug_response(serializer.data, status_code)
            return response
        except Http404 as e:
            self.debug_response_error(404)
            raise e

class MetricsViewSet(helpers.FieldPackageHelperMixin, helpers.CreateAPIView, helpers.UpdateAPIView,  helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Gauge.objects.all()
    serializer_class = GaugeReadableSerializer

    def list(self, request, volunteer_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310
            assert request.user.has_perm('api.read_metrics'), "You cannot read metrics"

            queryset = Gauge.objects.all()
            serializer = self.serializer_class(queryset, many=True)

            response = Response(serializer.data, status=status_code)
            self.debug_response(serializer.data, status_code)

            return response
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)


class NewsViewSet(helpers.FieldPackageHelperMixin, helpers.CreateAPIView, helpers.UpdateAPIView,  helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = News.objects.all()
    serializer_class = NewsWritableSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, volunteer_pk=None):
        self.debug_request(request)

        status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

        queryset = News.objects.all()
        serializer = NewsReadableSerializer(queryset, many=True)

        response = Response(serializer.data, status=status_code)
        self.debug_response(serializer.data, status_code)

        return response

    def retrieve(self, request, pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            queryset = News.objects.all()
            news = get_object_or_404(queryset, pk=pk)

            serializer = NewsReadableSerializer(news)

            self.debug_response(serializer.data, status_code)
            return Response(serializer.data, status=status_code)
        except Http404 as e:
            self.debug_response_error(404)
            raise e

    def create(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FieldPackage,
                        'required': ('title', 'body',),
                        'allowed_not_required': ()
                    },
                )
            assert RequiredPackageSet.make()[0].fits_to(request.DATA), "Invalid package set"

            assert request.user.has_perm('api.create_news'), "You cannot create news"

            status_code = status.HTTP_201_CREATED if self.has_created_org_or_volunteer_profile(request) else 310

            request.DATA['created_by'] = request.user.id
            request.DATA['created_at'] = datetime.datetime.now()

            response, serializer = self.make_creation(request, self.serializer_class)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Created news id={} by user={}".format(self.object.id, request.user.id))

            self.debug_response(response.data, status_code)
            return response
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FieldPackage,
                        'required': ('title', 'body',),
                        'allowed_not_required': ()
                    },
                )
            assert RequiredPackageSet.make()[0].fits_to(request.DATA), "Invalid package set"

            assert request.user.has_perm('api.edit_news'), "You cannot edit news"

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            request.DATA['last_modified_by'] = request.user.id
            request.DATA['last_modified_at'] = datetime.datetime.now()

            response = self.make_update(kwargs, self.serializer_class, request)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Edited news id={} by user={}".format(self.object.id, request.user.id))

            self.debug_response(response.data, status_code)
            return response
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class NewsThumbnailViewSet(ThumbnailCreateAPIView, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    serializer_class = ThumbnailNewsWritableSerializer
    thumbnail_classes = {'thumbnail': ThumbnailNewsWritableSerializer}
    keyword = 'news'

    def create(self, request, *args, **kwargs):
        self.debug_request(request)

        news_pk = kwargs['news_pk']

        request.POST = request.POST.copy()
        request.DATA['news'] = news_pk

        response = super(NewsThumbnailViewSet, self).create(request, *args, **kwargs)
        if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
            log.info("Created news thumbnail id={} for org id={}".format(self.object.id, news_pk))
        self.debug_response(response.data, response.status_code)
        return response


class OrganizationThumbnailViewSet(ThumbnailCreateAPIView, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    serializer_class = ThumbnailOrganizationWritableSerializer
    thumbnail_classes = {'thumbnail': ThumbnailOrganizationWritableSerializer,
                         'original': OriginalThumbnailOrganizationWritableSerializer}
    keyword = 'organization'

    def create(self, request, *args, **kwargs):
        self.debug_request(request)

        org_pk = kwargs['org_pk']
        if org_pk == 'my':
            assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                "You are not a member of any organization"

            org_pk = UserProfile.objects.get(user=request.user).organization_member.id
            self.debug_MY_id_translated_to(org_pk)

        request.POST = request.POST.copy()
        request.DATA['organization'] = org_pk

        response = super(OrganizationThumbnailViewSet, self).create(request, *args, **kwargs)
        if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
            log.info("Created organization thumbnail id={} for org id={}".format(self.object.id, org_pk))
        self.debug_response(response.data, response.status_code)
        return response

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            org_pk = kwargs['org_pk']
            if org_pk == 'my':
                assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                    "You are not a member of any organization"

                org_pk = UserProfile.objects.get(user=request.user).organization_member.id
                self.debug_MY_id_translated_to(org_pk)

            request.POST = request.POST.copy()
            request.DATA['organization'] = org_pk

            response = super(OrganizationThumbnailViewSet, self).update(request, *args, **kwargs)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Updated organization thumbnail id={} for org id={}".format(self.object.id, org_pk))
            self.debug_response(response.data, response.status_code)
            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class VolunteerThumbnailViewSet(ThumbnailCreateAPIView, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    serializer_class = ThumbnailVolunteerProfileWritableSerializer
    thumbnail_classes = {'thumbnail': ThumbnailVolunteerProfileWritableSerializer,
                         'original': OriginalThumbnailVolunteerProfileWritableSerializer}
    keyword = 'volunteer'

    def create(self, request, *args, **kwargs):
        self.debug_request(request)

        vol_pk = kwargs['volunteer_pk']
        if vol_pk == 'my':
            vol_pk = VolunteerProfile.objects.get(user=request.user).id
            self.debug_MY_id_translated_to(vol_pk)

        request.POST = request.POST.copy()
        request.DATA['volunteer'] = vol_pk

        response = super(VolunteerThumbnailViewSet, self).create(request, *args, **kwargs)
        if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
            log.info("Created volunteer thumbnail id={} for user id={}".format(self.object.id, request.user.id))
        self.debug_response(response.data, response.status_code)
        return response

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            vol_pk = kwargs['volunteer_pk']
            if vol_pk == 'my':
                vol_pk = VolunteerProfile.objects.get(user=request.user).id
                self.debug_MY_id_translated_to(vol_pk)

            request.POST = request.POST.copy()
            request.DATA['volunteer'] = vol_pk

            response = super(VolunteerThumbnailViewSet, self).update(request, *args, **kwargs)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Updated volunteer thumbnail id={} for org id={}".format(self.object.id, vol_pk))
            self.debug_response(response.data, response.status_code)
            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class OrganizationOffersViewSet(helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def list(self, request, org_pk=None):
        self.debug_request(request)
        is_my = False

        if org_pk == 'my':
            try:
                if request.user.is_anonymous():
                    raise Http404('Anonymous user cannot manage organization')

                assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                    "You are not a member of any organization"
                org_pk = UserProfile.objects.get(user=request.user).organization_member.id
                is_my = True
            except UserProfile.DoesNotExist:
                raise Http404('User profile not found')

        status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

        offers = Offer.objects.filter(publishing_organization=org_pk)

        status_tbl = request.GET.get('status', '')
        try:
            status_tbl = [int(s) for s in status_tbl.split(',')]
        except ValueError:
            status_tbl = []

        forbidden = [OfferStateFactory.DRAFT, OfferStateFactory.IN_REVIEW,
                     OfferStateFactory.DEPUBLISHED, OfferStateFactory.REJECTED, OfferStateFactory.REMOVED]

        if not is_my and any(s in status_tbl for s in forbidden):
            raise PermissionDenied

        filter = OrganizationOfferListFilter(request.GET, queryset=offers)

        serializer = OrganizationOffersListSerializer(filter.qs, many=True)

        self.debug_response(serializer.data, status_code)
        return Response(serializer.data, status=status_code)

    @list_route()
    def count(self, request, org_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310
            if org_pk == 'my':
                try:
                    if request.user.is_anonymous():
                        raise Http404('Anonymous user cannot manage organization')

                    assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                        "You are not a member of any organization"
                    org_pk = UserProfile.objects.get(user=request.user).organization_member.id
                    is_my = True
                except UserProfile.DoesNotExist:
                    raise Http404('User profile not found')

            offers = Offer.objects.filter(publishing_organization=org_pk).values('status').annotate(count=Count('status'))
            stats = {s[0]: s[1] for s in OfferStateFactory.get_statuses_choice_list()}
            log.debug(stats)
            log.debug(type(stats))
            response = {value: 0 for value in stats.itervalues()}

            for offer in offers:
                response[stats[offer['status']]] = offer['count']

            self.debug_response(response, status_code)
            return Response(response, status=status_code)
        except KeyError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Http404 as e:
            self.debug_response_error(404)
            raise e


class OfferThumbnailViewSet(ThumbnailCreateAPIView, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    serializer_class = LargeThumbnailOfferWritableSerializer
    thumbnail_classes = {'large': LargeThumbnailOfferWritableSerializer,
                         'small': SmallThumbnailOfferWritableSerializer,
                         'promoted': PromotedThumbnailOfferWritableSerializer,
                         'original': OriginalThumbnailOfferWritableSerializer}
    keyword = 'offer'

    def create(self, request, *args, **kwargs):
        self.debug_request(request)

        offer_pk = kwargs['offer_pk']

        request.POST = request.POST.copy()
        request.DATA['offer'] = offer_pk

        response = super(OfferThumbnailViewSet, self).create(request, *args, **kwargs)
        if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
            log.info("Created offer thumbnail id={} for org id={}".format(self.object.id, offer_pk))
        self.debug_response(response.data, response.status_code)
        return response

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            offer_pk = kwargs['offer_pk']

            request.POST = request.POST.copy()
            request.DATA['offer'] = offer_pk

            response = super(OfferThumbnailViewSet, self).update(request, *args, **kwargs)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Updated organization thumbnail id={} for org id={}".format(self.object.id, offer_pk))
            self.debug_response(response.data, response.status_code)
            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class PromotedOfferViewSet(helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Offer.objects.filter(is_promoted=True)
    serializer_class = PromotedOfferListSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def list(self, request):
        self.debug_request(request)

        status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

        promoted_offers = Offer.objects.filter(
            Q(status=OfferStateFactory.PUBLISHED) | Q(status=OfferStateFactory.PUBLISHED_EDITED), is_promoted=True,
            publish_from__lt=datetime.datetime.now(), publish_to__gt=datetime.datetime.now()).order_by('-publish_from')[:4]

        length = len(promoted_offers)
        if length < 4:
            offers = Offer.objects.filter(
                Q(status=OfferStateFactory.PUBLISHED) | Q(status=OfferStateFactory.PUBLISHED_EDITED), is_promoted=False,
                publish_from__lt=datetime.datetime.now(), publish_to__gt=datetime.datetime.now()) \
                .order_by('-publish_from')[:4-length]
            promoted_offers = QuerySetChain(promoted_offers, offers)

        serializer = PromotedOfferListSerializer(promoted_offers, many=True)

        self.debug_response(serializer.data, status_code)
        return Response(serializer.data, status=status_code)


class AdminOfferViewSet(helpers.FieldPackageHelperMixin, helpers.OfferPermissionHelperMixin,
        helpers.PermissionHelperMixin, helpers.CreateAPIView, helpers.UpdateAPIView, generics.DestroyAPIView,
        helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferWritableSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310
            assert request.user.has_perm('api.view_admin_offer_list'), "You cannot view offer list"

            offers_filtered = Offer.objects.all()
            filter = OfferAdminListFilter(request.GET, queryset=offers_filtered)
            serializer = AdminOfferListSerializer(filter.qs, many=True)

            self.debug_response(serializer.data, status_code)
            return Response(serializer.data, status=status_code)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': "Bad credentials"}, status=status.HTTP_403_FORBIDDEN)


class OfferViewSet(helpers.FieldPackageHelperMixin, helpers.OfferPermissionHelperMixin,
        helpers.PermissionHelperMixin, helpers.CreateAPIView, helpers.UpdateAPIView, generics.DestroyAPIView,
        helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferWritableSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        self.debug_request(request)

        status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

        offers_filtered = Offer.objects.filter(
            Q(status=OfferStateFactory.PUBLISHED) | Q(status=OfferStateFactory.PUBLISHED_EDITED),
            publish_from__lt=datetime.datetime.now(), publish_to__gt=datetime.datetime.now())
        filter = OfferListFilter(request.GET, queryset=offers_filtered)

        serializer = OfferListSerializer(filter.qs, many=True)

        self.debug_response(serializer.data, status_code)
        return Response(serializer.data, status=status_code)

    def retrieve(self, request, pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            queryset = Offer.objects.all()
            offer = get_object_or_404(queryset, pk=pk)

            assert request.user.has_perm('api.view_any_offer') or \
                offer.status is OfferStateFactory.PUBLISHED or offer.status is OfferStateFactory.PUBLISHED_EDITED or \
                (UserProfile.objects.get(user=request.user).organization_member is not None and
                    offer.publishing_organization.id == UserProfile.objects.get(user=request.user).organization_member.id), \
                "You cannot see this offer"

            if request.user.is_anonymous():
                offer.views_count_guests += 1
            elif VolunteerProfile.objects.filter(user=request.user).exists():
                offer.views_count_volunteers += 1
            offer.save()

            serializer = OfferDetailSerializer(offer)

            self.debug_response(serializer.data, status_code)
            return Response(serializer.data, status=status_code)

        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except Http404 as e:
            self.debug_response_error(404)
            raise e

    def create(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class FirstStep(FieldPackage):
                def create(self, viewset, request, *args, **kwargs):
                    serializer = OfferWritableSerializer
                    viewset.assert_logged_user_has_permissions(request, ('api.create_offer',))

                    resource = ResourceMetadata(created_by=request.user, last_modified_by=request.user)
                    resource.save()

                    assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                        "You are not a member of any organization"

                    organization = Organization.objects.get(
                        pk=UserProfile.objects.get(user=request.user).organization_member.id
                    )

                    request.DATA['step_1'] = resource.id
                    request.DATA['publishing_organization'] = organization.id
                    request.DATA['is_promoted'] = False
                    request.DATA['status'] = OfferStateFactory.DRAFT

                    response, serializer = viewset.make_creation(request, serializer)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Created first step of offer id={} for user={}".format(viewset.object.id, request.user.id))

                    viewset.debug_response(response.data, response.status_code)
                    return response

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FirstStep,
                        'required': ('title', 'publish_from', 'publish_to', 'volunteer_max_count', 'category',
                            'description_quests', 'description_time', 'description_problem', 'description'),
                        'allowed_not_required': ('localization',)
                    },
                )
            packages = RequiredPackageSet.make()
            fitting_field_package = self.get_fitting_field_package(packages, request.DATA)
            log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
            return fitting_field_package.create(self, request, *args, **kwargs)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except PermissionHelperMixin.AccessDeniedException as e:
            self.debug_response_error(403)
            return Response({'detail': "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        except WrongRequestException as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class FirstStep(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    serializer = OfferWritableSerializer
                    pk = kwargs['pk']
                    kwargs['partial'] = True

                    offer = Offer.objects.get(pk=pk)
                    viewset.assert_has_permissions_to_edit_my_offer(offer, request.user)

                    resource = ResourceMetadata.objects.get(pk=offer.step_1.id)
                    resource.last_modified_by = request.user
                    resource.save()

                    state = OfferStateFactory.make(offer.status)
                    state.clean_after_editing_offer(request)

                    response = viewset.make_update(kwargs, serializer, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Updated first step of offer id={}".format(pk))

                    viewset.debug_response(response.data, response.status_code)
                    return response

            class SecondStep(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    pk = kwargs['pk']
                    offer = Offer.objects.get(pk=pk)

                    if offer.description_requirements is u'' or \
                            offer.description_benefits is u'':
                        return self.create_field_package(viewset, request, args, kwargs)
                    else:
                        return self.update_field_package(viewset, request, args, kwargs)

                #private
                def create_field_package(self, viewset, request, args, kwargs):
                    serializer = OfferWritableSerializer
                    pk = kwargs['pk']
                    kwargs['partial'] = True

                    viewset.assert_logged_user_has_permissions(request, ('api.create_offer',))

                    resource = ResourceMetadata(created_by=request.user, last_modified_by=request.user)
                    resource.save()

                    request.DATA['step_2'] = resource.id

                    response = viewset.make_update(kwargs, serializer, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Created second step of offer id={}".format(pk))

                    viewset.debug_response(response.data, response.status_code)
                    return response

                #private
                def update_field_package(self, viewset, request, args, kwargs):
                    serializer = OfferWritableSerializer
                    pk = kwargs['pk']
                    kwargs['partial'] = True

                    offer = Offer.objects.get(pk=pk)
                    viewset.assert_has_permissions_to_edit_my_offer(offer, request.user)

                    resource = ResourceMetadata.objects.get(pk=offer.step_2.id)
                    resource.last_modified_by = request.user
                    resource.save()

                    state = OfferStateFactory.make(offer.status)
                    state.clean_after_editing_offer(request)

                    response = viewset.make_update(kwargs, serializer, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Updated second step of offer id={}".format(pk))
                    viewset.debug_response(response.data, response.status_code)
                    return response

            class StatusChange(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    serializer = OfferWritableSerializer
                    pk = kwargs['pk']
                    offer = Offer.objects.get(pk=pk)

                    two_first_steps = ([viewset.packages[0]] + [viewset.packages[1]])
                    for package in two_first_steps:
                        assert package.is_accomplished(ModelChecker(offer)), "Fill all the steps to change state"

                    if request.DATA['status'] == OfferStateFactory.DEPUBLISHED or \
                            request.DATA['status'] == OfferStateFactory.REJECTED:
                        assert 'status_change_reason' in request.DATA and len(request.DATA['status_change_reason']) > 0, \
                            "Provide reason of status change"

                    state = OfferStateFactory.make(offer.status)
                    state.prepare_request(request, offer)
                    state.assert_can_change_state(request.DATA['status'], offer, request.user)
                    state.perform_actions_after_changing_status(request, offer)
                    response = viewset.make_update(kwargs, serializer, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Updated status of offer id={}".format(pk))
                    viewset.debug_response(response.data, response.status_code)
                    return response

            class AgreementStep(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    serializer = OfferWritableSerializer
                    pk = kwargs['pk']
                    offer = Offer.objects.get(pk=pk)

                    response = viewset.make_update(kwargs, serializer, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Updated agreement data of offer id={}".format(pk))
                    viewset.debug_response(response.data, response.status_code)
                    return response

            class PromotionChange(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    serializer = OfferWritableSerializer
                    pk = kwargs['pk']

                    assert request.user.has_perm('api.promote_offer'), "You cannot promote offers"

                    response = viewset.make_update(kwargs, serializer, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Updated promotion status of offer id={}".format(pk))
                    viewset.debug_response(response.data, response.status_code)
                    return response

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FirstStep,
                        'required': ('title', 'publish_from', 'publish_to', 'volunteer_max_count', 'category',
                            'description_quests', 'description_time', 'description_problem', 'description',),
                        'allowed_not_required': ('localization',)
                    },
                    {
                        'class': SecondStep,
                        'required': ('description_requirements', 'description_benefits'),
                            'allowed_not_required': ('description_additional_requirements',)
                    },
                    {
                        'class': StatusChange,
                        'required': ('status',),
                        'allowed_not_required': ('status_change_reason',)
                    },
                    {
                        'class': AgreementStep,
                        'required': ('agreement_stands_from', 'agreement_stands_to', 'agreement_signatories',),
                        'allowed_not_required': ()
                    },
                    {
                        'class': PromotionChange,
                        'required': ('is_promoted',),
                        'allowed_not_required': ()
                    }
                )
            self.packages = RequiredPackageSet.make()
            fitting_field_package = self.get_fitting_field_package(self.packages, request.DATA)
            log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
            return fitting_field_package.update(self, request, args, kwargs)
        except ValidationError as err:
            self.debug_response_error(400)
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': "Bad credentials"}, status=status.HTTP_403_FORBIDDEN)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except WrongRequestException as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        serializer = OfferWritableSerializer

        try:
            self.debug_request(request)

            kwargs['partial'] = True
            offer = Offer.objects.get(pk=kwargs['pk'])

            self.prevent_modifying_any_field(request)

            state = OfferStateFactory.make(offer.status)
            state.assert_can_change_state(OfferStateFactory.DEPUBLISHED, offer, request.user)

            request.DATA['status'] = OfferStateFactory.DEPUBLISHED

            response = self.make_update(kwargs, serializer, request)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Destroyed offer id={}".format(kwargs['pk']))
            self.debug_response(response.data, response.status_code)
            return response
        except ValidationError as err:
            self.debug_response_error(400)
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': "Bad credentials"}, status=status.HTTP_403_FORBIDDEN)
        except WrongRequestException:
            self.debug_response_error(400)
            return Response({'detail': "Wrong request data"}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    @api_view(['POST'])
    @permission_decorator((AllowAny,))
    def search(request, phrase=''):
        log.debug(u"Request OfferViewSet.search with phrase={}".format(phrase))

        def get_attributes_for_class(cls):
            return set([i for i in cls.__dict__.keys() if i[:1] != '_'])

        attributes = get_attributes_for_class(OfferIndex) \
            - get_attributes_for_class(indexes.SearchIndex) \
            - get_attributes_for_class(indexes.Indexable)

        queries = reduce(lambda x, y: x | y, [SQ(**{attr + "__startswith": phrase}) for attr in attributes \
            if attr in OfferIndex.Meta.search_within])

        offers = SearchQuerySet().filter(SQ(publish_from__lt=datetime.datetime.now()) &
            SQ(SQ(status=OfferStateFactory.PUBLISHED) | SQ(status=OfferStateFactory.PUBLISHED_EDITED))
            & SQ(publish_to__gt=datetime.datetime.now())).filter(queries)

        offers = [OfferListSerializer(it.object).data for it in offers]

        log.debug("Response OfferViewSet.search code={} data={}".format(status.HTTP_200_OK, offers))
        return Response(offers, status=status.HTTP_200_OK)


class UserViewSet(helpers.PermissionHelperMixin, helpers.UpdateAPIView, helpers.CreateAPIView, helpers.LoggingHelperMixin,
        viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        self.debug_request(request)

        serialized = UserSerializer(data=request.DATA)
        if serialized.is_valid():
            user_data = utils.get_user_data(request.DATA)
            user = self.create_inactive_user(**user_data)

            user_profile = UserProfile(user=user, organization_member=None)
            user_profile.save()

            target = NotificationTarget(user=user, target=user.email, backend=1, active=True)
            target.save()
            log.info("Sent confirmation email to {}".format(user.email))

            response = Response({'id': user.id}, status=status.HTTP_201_CREATED)
            log.info("Created user id={}".format(user.id))
            self.debug_response(response.data, response.status_code)

            return response
        else:
            self.debug_response_error(400)
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)

    @atomic_decorator
    def create_inactive_user(self, username=None, email=None, password=None):
        user_model = get_user_model()
        if username is not None:
            new_user = user_model.objects.create_user(username, email, password)
        else:
            new_user = user_model.objects.create_user(email=email, password=password)
        new_user.is_active = False
        new_user.save()
        create_profile(new_user)
        site = Site.objects.get_current()
        self.send_activation_email(new_user, site)
        return new_user

    def send_activation_email(self, user, site):
        setts = Settings.objects.get(settings__contains=['instance_url'])

        ctx_dict = {'activation_key': user.api_registration_profile.activation_key,
                    'expiration_days': get_settings('REGISTRATION_API_ACCOUNT_ACTIVATION_DAYS'),
                    'site': site,
                    'name': user.username,
                    'contact_email': setts.settings['contact_email'],
                    'instance_url': instance_url(),
                    'instance_name': setts.settings['instance_name']}
        subject = render_to_string('registration_api/activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        message = render_to_string('registration_api/activation_email.txt',
                                   ctx_dict)
        user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)

    def update(self, request, *args, **kwargs):
        self.debug_request(request)

        serializer = UserSerializer

        try:
            assert int(kwargs['pk']) is int(request.user.id), "You cannot edit another user model than yours"

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FieldPackage,
                        'required': ('first_name', 'last_name',),
                        'allowed_not_required': ()
                    },
                )
            assert RequiredPackageSet.make()[0].fits_to(request.DATA), "Invalid package set"

            kwargs['partial'] = True
            response = self.make_update(kwargs, serializer, request)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Updated user data for user id={}".format(kwargs['pk']))
            self.debug_response(response.data, response.status_code)
            return response
        except ValidationError as err:
            self.debug_response_error(400)
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)

    @staticmethod
    @api_view(['GET'])
    @permission_decorator((AllowAny,))
    def activate(request, activation_key=None):
        log.debug("Request UserProfile.activate with activation key={}".format(activation_key))

        try:
            profile = RegistrationProfile.objects.get(activation_key=activation_key)
            is_activated = utils.activate_user(activation_key)
        except RegistrationProfile.DoesNotExist:
            is_activated = False
            log.info("Tried to activate with non-existing key: %s" % activation_key)

        # if not activated
        if is_activated:
            response = Response({'detail': 'User has been activated'}, status=status.HTTP_200_OK)
            log.info("User id={} has been activated".format(profile.user.id))
            log.debug("Response UserProfile.activate with code={}".format(response.status_code))
            return response
        else:
            log.error("Response UserProfile.activate failed with code 400")
            return Response({'detail': 'Activation failed'}, status=status.HTTP_400_BAD_REQUEST)
        # success_url = utils.get_settings('REGISTRATION_API_ACTIVATION_SUCCESS_URL')
        # if success_url is not None:
        #     return HttpResponseRedirect(success_url)

    @staticmethod
    @api_view(['GET'])
    @permission_decorator((AllowAny,))
    def logout(request):
        auth_logout(request)
        return Response({'detail': 'User logged out.'}, status=status.HTTP_200_OK)


class AbilityViewSet(mixins.ListModelMixin, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Ability.objects.all()
    serializer_class = AbilityReadableSerializer

    def list(self, request, *args, **kwargs):
        self.debug_request(request)

        serializer = self.serializer_class(self.queryset, many=True)

        response = Response(serializer.data)
        self.debug_response(response.data, response.status_code)
        return response


class OrgAbilityViewSet(mixins.ListModelMixin, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = OrgAbility.objects.all()
    serializer_class = OrgAbilityReadableSerializer

    def list(self, request, *args, **kwargs):
        self.debug_request(request)

        serializer = self.serializer_class(self.queryset, many=True)

        response = Response(serializer.data)
        self.debug_response(response.data, response.status_code)
        return response


class OrganizationTypeViewSet(helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = OrganizationType.objects.all()
    serializer_class = OrganizationTypeReadableSerializer

    def list(self, request):
        self.debug_request(request)

        serializer = self.serializer_class(self.queryset, many=True)

        response = Response(serializer.data)
        self.debug_response(response.data, response.status_code)
        return response


class EducationViewSet(mixins.ListModelMixin, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationReadableSerializer

    def list(self, request, *args, **kwargs):
        self.debug_request(request)

        serializer = self.serializer_class(self.queryset, many=True)

        response = Response(serializer.data)
        self.debug_response(response.data, response.status_code)
        return response


class CategoryViewSet(helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryReadableSerializer

    def list(self, request):
        self.debug_request(request)

        serializer = self.serializer_class(self.queryset, many=True)

        response = Response(serializer.data)
        self.debug_response(response.data, response.status_code)
        return response


class CountryListView(helpers.LoggingHelperMixin, generics.views.APIView):
    def get(self, request, *args, **kwargs):
        self.debug_request(request)

        ret = []
        countries_dict = dict(countries)
        for key, value in countries_dict.iteritems():
            ret.append({"code": key, "name": value})
        response = Response(ret)
        self.debug_response(response.data, response.status_code)
        return response


class SettingsViewSet(helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingsListSerializer
    lookup_value_regex = '[0-9a-z_]+'
    permission_classes = (AllowAny, )

    def list(self, request):
        try:
            self.debug_request(request)

            # if not request.user.has_perm('api.read_any_setting'):
            #     raise PermissionHelperMixin.AccessDeniedException()

            settings = Settings.objects.first()

            serializer = SettingsListSerializer(settings)
            response = Response(serializer.data)
            self.debug_response(response.data, response.status_code)
            return response
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    def retrieve(self, request, pk=None):
        try:
            self.debug_request(request)

            # if not request.user.has_perm('api.read_any_setting'):
            #     raise PermissionHelperMixin.AccessDeniedException()

            settings = Settings.objects.get(settings__contains=[pk])

            response = Response({'key': pk,'value': settings.settings[pk]}, status=status.HTTP_200_OK)
            self.debug_response(response.data, response.status_code)
            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': 'Setting not found'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, pk=None):
        try:
            self.debug_request(request)

            if not request.user.has_perm('api.write_any_setting'):
                raise PermissionHelperMixin.AccessDeniedException()

            settings = Settings.objects.filter(settings__contains=[pk])
            settings = Settings.objects.first() if len(settings) is 0 else settings.first()

            settings.settings[pk] = request.DATA['value']
            settings.save()

            response = Response({'key': pk,'value': settings.settings[pk]}, status=status.HTTP_201_CREATED)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Updated setting key={} with value={}".format(pk, request.DATA['value']))
            self.debug_response(response.data, response.status_code)
            return response
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)


class OfferDocumentTemplateViewSet(helpers.DocumentTemplateHelper, helpers.FieldPackageHelperMixin,
        helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    def list(self, request, offer_pk=None):
        try:
            self.debug_request(request)

            offer = Offer.objects.get(pk=offer_pk)
            template, is_specific = self.find_template_for_offer(offer)

            serializer = self.serializer_class(template)
            response = Response(serializer.data)
            dict = response.data
            dict['is_specific'] = is_specific
            self.debug_response(dict, response.status_code)
            return response
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)


class OfferAgreementTemplateViewSet(OfferDocumentTemplateViewSet):
    queryset = AgreementTemplate.objects.all()
    serializer_class = AgreementTemplateSerializer
    template_class = AgreementTemplate


class OfferCertificateTemplateViewSet(OfferDocumentTemplateViewSet):
    queryset = CertificateTemplate.objects.all()
    serializer_class = CertificateTemplateSerializer
    template_class = CertificateTemplate


class OfferBulkViewSet(helpers.FieldPackageHelperMixin, helpers.UpdateAPIView, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Offer.objects.all()

    def update(self, request, *args, **kwargs):
        self.debug_request(request)

        class StatusChange(FieldPackage):
            def update(self, viewset, request, args, kwargs):
                serializer = OfferWritableSerializer

                assert type(request.DATA['ids']) is list, "Provide list of ids"
                responses = {}

                for id in request.DATA['ids']:
                    try:
                        offer = Offer.objects.get(pk=id)
                        viewset.kwargs['pk'] = id
                        kwargs['partial'] = True

                        class StepsPackageSet(FieldPackageSetFactory):
                            packages_having_regard_to_order = (
                                {
                                    'class': FieldPackage,
                                    'required': ('title', 'publish_from', 'publish_to', 'volunteer_max_count', 'category',
                                        'description_quests', 'description_time', 'description_problem', 'description',),
                                    'allowed_not_required': ('localization',)
                                },
                                {
                                    'class': FieldPackage,
                                    'required': ('description_requirements', 'description_benefits'),
                                        'allowed_not_required': ('description_additional_requirements',)
                                },
                            )
                        for package in StepsPackageSet.make():
                            assert package.is_accomplished(ModelChecker(offer)), "Fill all the steps to change state"

                        state = OfferStateFactory.make(offer.status)
                        state.prepare_request(request, offer)
                        state.assert_can_change_state(request.DATA['status'], offer, request.user)
                        state.perform_actions_after_changing_status(request, offer)
                        response = viewset.make_update(kwargs, serializer, request)
                        if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                            log.info("Updated status of offer id={}".format(id))
                        viewset.debug_response(response.data, response.status_code)

                        if response.status_code is not status.HTTP_201_CREATED:
                            status_code = response.status_code

                        responses[id] = response.data
                    except ValidationError as e:
                        viewset.debug_response_error(400)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': e.message, 'code': status.HTTP_400_BAD_REQUEST}
                    except PermissionHelperMixin.AccessDeniedException:
                        viewset.debug_response_error(403)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': "Bad credentials", 'code': status.HTTP_403_FORBIDDEN}
                    except AssertionError as e:
                        viewset.debug_response_error(400)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': e.message, 'code': status.HTTP_400_BAD_REQUEST}
                    except ObjectDoesNotExist as e:
                        viewset.debug_response_error(404)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': e.message, 'code': status.HTTP_404_NOT_FOUND}
                    except WrongRequestException as e:
                        viewset.debug_response_error(400)
                        status_code = status.HTTP_409_CONFLICT
                        responses[id] = {'detail': e.message, 'code': status.HTTP_400_BAD_REQUEST}

                viewset.debug_response(responses, status_code)
                return Response(responses, status_code)

        class RequiredPackageSet(FieldPackageSetFactory):
            packages_having_regard_to_order = (
                {
                    'class': StatusChange,
                    'required': ('status', 'ids'),
                    'allowed_not_required': ()
                },
            )
        self.packages = RequiredPackageSet.make()
        fitting_field_package = self.get_fitting_field_package(self.packages, request.DATA)
        log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
        return fitting_field_package.update(self, request, args, kwargs)


class OfferRatingViewSet(helpers.FieldPackageHelperMixin, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = OrgRating.objects.all()

    def list(self, request, offer_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            offer = Offer.objects.get(pk=offer_pk)

            ratings = OrgRating.objects.filter(offer=offer)\
                .values('organization', 'offer', 'created_by', 'created_by__first_name', 'created_by__last_name').annotate(rating=Avg('rating'))
            ratings = list(ratings)

            for rating in ratings:
                testimonials = OrgTestimonial.objects \
                    .filter(organization=rating['organization'], offer=rating['offer'], created_by=rating['created_by'])
                rating['testimonial'] = testimonials.first().body if testimonials.exists() else None
                rating['is_public'] = testimonials.first().is_public if testimonials.exists() else None
                rating['volunteer_first_name'] = rating['created_by__first_name']
                rating['volunteer_last_name'] = rating['created_by__last_name']
                rating['volunteer'] = VolunteerProfile.objects.get(user_id=rating['created_by']).pk
                rating['created_at'] = OrgRating.objects.filter(offer=offer).first().created_at

                for toDel in ['created_by__first_name', 'created_by__last_name']:
                    del rating[toDel]

            vol_ratings = Rating.objects.filter(offer=offer)\
                .values('volunteer', 'offer', 'created_by', 'offer__publishing_organization__fullname',
                        'offer__publishing_organization__id').annotate(rating=Avg('rating'))
            vol_ratings = list(vol_ratings)

            for rating in vol_ratings:
                testimonials = Testimonial.objects \
                    .filter(volunteer=rating['volunteer'], offer=rating['offer'], created_by=rating['created_by'])
                rating['testimonial'] = testimonials.first().body if testimonials.exists() else None
                rating['is_public'] = testimonials.first().is_public if testimonials.exists() else None
                rating['created_at'] = testimonials.first().created_at if testimonials.exists() else None
                rating['organization_fullname'] = rating['offer__publishing_organization__fullname']
                rating['organization_id'] = rating['offer__publishing_organization__id']
                rating['created_at'] = Rating.objects.filter(offer=offer).first().created_at

                for toDel in ['offer__publishing_organization__fullname', 'offer__publishing_organization__id']:
                    del rating[toDel]

            data = {
                'organization': ratings,
                'volunteer': vol_ratings,
            }

            response = Response(data, status=status_code)
            self.debug_response(data, status_code)

            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Not found"}, status=status.HTTP_404_NOT_FOUND)


class OrganizationDocumentTemplateViewSet(helpers.DocumentTemplateHelper, helpers.FieldPackageHelperMixin,
        helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = AgreementTemplate.objects.all()
    serializer_class = AgreementTemplateSerializer
    template_class = AgreementTemplate

    def list(self, request, org_pk=None):
        try:
            self.debug_request(request)

            if org_pk == 'my':
                try:
                    if request.user.is_anonymous():
                        raise Http404('Anonymous user cannot manage organization')

                    assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                        "You are not a member of any organization"

                    org_pk = UserProfile.objects.get(user=request.user).organization_member.id
                except UserProfile.DoesNotExist:
                    raise Http404('User profile not found')

            org = Organization.objects.get(pk=org_pk)
            template, is_specific = self.find_template_for_org(org)

            serializer = self.serializer_class(template)
            response = Response(serializer.data)
            dict = response.data
            dict['is_specific'] = is_specific
            self.debug_response(dict, response.status_code)
            return response
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)


class OrganizationAgreementTemplateViewSet(OrganizationDocumentTemplateViewSet):
    queryset = AgreementTemplate.objects.all()
    serializer_class = AgreementTemplateSerializer
    template_class = AgreementTemplate


class OrganizationCertificateTemplateViewSet(OrganizationDocumentTemplateViewSet):
    queryset = CertificateTemplate.objects.all()
    serializer_class = CertificateTemplateSerializer
    template_class = CertificateTemplate


class OrganizationRatingViewSet(helpers.FieldPackageHelperMixin, helpers.ProfileAssertion,
        helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = OrgRating.objects.all()

    def list(self, request, org_pk=None):
        try:
            self.debug_request(request)

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if org_pk == 'my':
                assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                    "You are not a member of any organization"

                org_pk = UserProfile.objects.get(user=request.user).organization_member.id
                self.debug_MY_id_translated_to(org_pk)

            ratings = OrgRating.objects.filter(organization=org_pk)\
                .values('organization', 'offer', 'created_by', 'created_by__first_name', 'created_by__last_name').annotate(rating=Avg('rating'))
            ratings = list(ratings)

            for rating in ratings:
                testimonials = OrgTestimonial.objects \
                    .filter(organization=rating['organization'], offer=rating['offer'], created_by=rating['created_by'])
                rating['testimonial'] = testimonials.first().body if testimonials.exists() else None
                rating['is_public'] = testimonials.first().is_public if testimonials.exists() else None
                rating['volunteer_first_name'] = rating['created_by__first_name']
                rating['volunteer_last_name'] = rating['created_by__last_name']
                rating['volunteer'] = VolunteerProfile.objects.get(user_id=rating['created_by']).pk
                del rating['created_by__first_name']
                del rating['created_by__last_name']

            response = Response(ratings, status=status_code)
            self.debug_response(ratings, status_code)

            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Not found"}, status=status.HTTP_404_NOT_FOUND)


class DocumentTemplateViewSet(helpers.FieldPackageHelperMixin, helpers.CreateAPIView, helpers.UpdateAPIView,
        helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FieldPackage,
                        'required': ('body',),
                        'allowed_not_required': ('offer',)
                    },
                )
            assert RequiredPackageSet.make()[0].fits_to(request.DATA), "Invalid package set"

            assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                "You are not a member of any organization"

            org = UserProfile.objects.get(user=request.user).organization_member.id

            offer = request.DATA['offer'] if 'offer' in request.DATA else None
            assert not self.document_class.objects.filter(organization=org, offer=offer).exists(), \
                "Template already exists"

            request.POST = request.POST.copy()
            request.DATA['is_general'] = False
            request.DATA['organization'] = org

            response = super(DocumentTemplateViewSet, self).create(request, *args, **kwargs)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Created {} template id={} for org id={}".format(self.document_string, self.object.id, org))
            self.debug_response(response.data, response.status_code)
            return response
        except ValidationError as err:
            self.debug_response_error(400)
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FieldPackage,
                        'required': ('body',),
                        'allowed_not_required': ('offer',)
                    },
                )
            assert RequiredPackageSet.make()[0].fits_to(request.DATA), "Invalid package set"

            kwargs['partial'] = True

            assert UserProfile.objects.get(user=request.user).organization_member is not None, \
                        "You are not a member of any organization"

            org = UserProfile.objects.get(user=request.user).organization_member.id
            offer = request.DATA['offer'] if 'offer' in request.DATA else None
            template = self.document_class.objects.get(offer=offer, organization=org)

            self.kwargs['pk'] = template.id

            response = self.make_update(kwargs, self.serializer_class, request)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Updated {} template id={}".format(self.document_string, self.object.id))
            self.debug_response(response.data, response.status_code)
            return response
        except ValidationError as err:
            self.debug_response_error(400)
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist as e:
            self.debug_response_error(404)
            return Response({'detail': e.message}, status=status.HTTP_404_NOT_FOUND)


class DocumentViewSet(helpers.DocumentTemplateHelper, helpers.FieldPackageHelperMixin, helpers.CreateAPIView,
        helpers.UpdateAPIView, helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    def retrieve(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            offer_id = kwargs['lookup_one_value']
            volunteer_id = kwargs['lookup_two_value']
            document = self.document_class.objects.get(offer=offer_id, volunteer=volunteer_id)
            serializer = self.serializer_class(document)

            response = Response(serializer.data, status=status.HTTP_200_OK)
            self.debug_response(response.data, response.status_code)
            return response
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': self.document_string + ' not found'}, status=status.HTTP_404_NOT_FOUND)
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    def create_bulk(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': FieldPackage,
                        'required': ('offer',),
                        'allowed_not_required': ('volunteers',)
                    },
                )
            assert RequiredPackageSet.make()[0].fits_to(request.DATA), "Invalid package set"

            offer_id = request.DATA['offer']

            if 'volunteers' not in request.DATA or len(request.DATA['volunteers']) is 0:
                volunteer_ids = [application.volunteer.id for application in Application.objects.filter(offer=offer_id,
                    status=ApplicationStateFactory.ACCEPTED)]
            else:
                volunteer_ids = request.DATA['volunteers']
                del request.DATA['volunteers']

            pdfs = []
            offer = Offer.objects.get(pk=offer_id)
            for volunteer_id in volunteer_ids:
                volunteer = VolunteerProfile.objects.get(pk=volunteer_id)
                organization = Organization.objects.get(pk=offer.publishing_organization.id)
                org_thumbnails = OrganizationThumbnail.objects.filter(organization=organization)
                offer_thumbnails = SmallOfferThumbnail.objects.filter(offer=offer)
                volunteer_user = User.objects.get(pk=volunteer.user.id)
                tasks = self.find_tasks(offer, volunteer_id)
                signatories = OrganizationSignatory.objects.filter(organization=organization)
                created_at = datetime.datetime.now()

                self.assert_can_generate_document(offer)

                documents = self.document_class.objects.filter(volunteer=volunteer, offer=offer)
                document_exists = documents.exists()

                template_object, is_specific = self.find_template_for_offer(offer)
                pdf = self.generate_pdf(template_object=template_object, offer=offer, organization=organization,
                    volunteer=volunteer, volunteer_user=volunteer_user, org_thumbnails=org_thumbnails,
                    offer_thumbnails=offer_thumbnails, tasks=tasks, signatories=signatories, created_at=created_at)
                pdfs.append(pdf)
                media_path = os.path.join(pdf['path'], pdf['filename'])

                request.DATA['offer'] = offer_id
                request.DATA['volunteer'] = volunteer_id
                request.DATA['template'] = template_object.id
                request.DATA['status'] = self.document_state_factory.NOT_SIGNED
                request.DATA['not_signed_resource'] = media_path
                request.DATA['created_at'] = created_at

                if document_exists:
                    self.kwargs['pk'] = documents[0].id
                    response = self.make_update(kwargs, self.serializer_class, request)
                else:
                    if 'pk' in self.kwargs:
                        del self.kwargs['pk']
                    response, serializer = self.make_creation(request, self.serializer_class)
                if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                    log.info("Created {} id={}".format(self.document_string, self.object.id))
                self.debug_response(response.data, response.status_code)

            zip_path, zip_filename = self.generate_zip(pdfs, created_at=datetime.datetime.now(), offer=offer)
            return Response({'filename': os.path.join(zip_path, zip_filename)})
        except NotFoundException as e:
            self.debug_response_error(404)
            return Response({'detail': e.message}, status=status.HTTP_404_NOT_FOUND)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Given offer or volunteer doesn't exist", 'volunteer_id': volunteer_id},
                status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            request.POST = request.POST.copy()
            self.prevent_modifying_any_field(request)

            offer_id = kwargs['lookup_one_value']
            volunteer_id = kwargs['lookup_two_value']

            offer = Offer.objects.get(pk=offer_id)
            volunteer = VolunteerProfile.objects.get(pk=volunteer_id)
            organization = Organization.objects.get(pk=offer.publishing_organization.id)
            org_thumbnails = OrganizationThumbnail.objects.filter(organization=organization)
            offer_thumbnails = SmallOfferThumbnail.objects.filter(offer=offer)
            volunteer_user = User.objects.get(pk=volunteer.user.id)
            tasks = self.find_tasks(offer, volunteer_id)
            signatories = OrganizationSignatory.objects.filter(organization=organization)
            created_at = datetime.datetime.now()

            self.assert_can_generate_document(offer)

            assert self.document_class.objects.filter(volunteer=volunteer, offer=offer).count() is 0,\
                "You already created an " + self.document_string

            template_object, is_specific = self.find_template_for_offer(offer)
            pdf = self.generate_pdf(template_object=template_object, offer=offer, organization=organization,
                volunteer=volunteer, volunteer_user=volunteer_user, org_thumbnails=org_thumbnails,
                offer_thumbnails=offer_thumbnails, tasks=tasks, signatories=signatories, created_at=created_at)
            media_path = os.path.join(pdf['path'], pdf['filename'])

            request.DATA['offer'] = offer_id
            request.DATA['volunteer'] = volunteer_id
            request.DATA['template'] = template_object.id
            request.DATA['status'] = self.document_state_factory.NOT_SIGNED
            request.DATA['not_signed_resource'] = media_path
            request.DATA['created_at'] = created_at

            response, serializer = self.make_creation(request, self.serializer_class)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Created {} id={}".format(self.document_string, self.object.id))
            self.debug_response(response.data, response.status_code)
            return response
        except NotFoundException as e:
            self.debug_response_error(404)
            return Response({'detail': e.message}, status=status.HTTP_404_NOT_FOUND)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Given offer or volunteer doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            class RegenerateNotSignedResource(FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    offer_id = kwargs['lookup_one_value']
                    volunteer_id = kwargs['lookup_two_value']

                    document = viewset.document_class.objects.get(offer=offer_id, volunteer=volunteer_id)
                    viewset.kwargs['pk'] = document.id

                    offer = Offer.objects.get(pk=offer_id)
                    volunteer = VolunteerProfile.objects.get(pk=volunteer_id)
                    organization = Organization.objects.get(pk=offer.publishing_organization.id)
                    volunteer_user = User.objects.get(pk=volunteer.user.id)
                    org_thumbnails = OrganizationThumbnail.objects.filter(organization=organization)
                    offer_thumbnails = SmallOfferThumbnail.objects.filter(offer=offer)
                    tasks = viewset.find_tasks(offer, volunteer_id)
                    created_at = datetime.datetime.now()
                    signatories = OrganizationSignatory.objects.filter(organization=organization)

                    viewset.assert_can_generate_document(offer)

                    state = viewset.document_state_factory.make(document.status)
                    state.request = request
                    state.assert_can_regenerate_pdf()

                    template_object, is_specific = viewset.find_template_for_offer(offer)
                    pdf = viewset.generate_pdf(template_object=template_object, offer=offer, organization=organization,
                        volunteer=volunteer, volunteer_user=volunteer_user, org_thumbnails=org_thumbnails,
                        offer_thumbnails=offer_thumbnails, tasks=tasks, signatories=signatories, created_at=created_at)
                    media_path = os.path.join(pdf['path'], pdf['filename'])

                    request.DATA['offer'] = offer_id
                    request.DATA['volunteer'] = volunteer_id
                    request.DATA['template'] = template_object.id
                    request.DATA['status'] = viewset.document_state_factory.NOT_SIGNED
                    request.DATA['not_signed_resource'] = media_path
                    request.DATA['created_at'] = created_at

                    response = viewset.make_update(kwargs, viewset.serializer_class, request)
                    if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                        log.info("Regenerated not signed {} resource offer_id={} volunteer_id={}".format(
                            viewset.document_string,
                            offer_id,
                            volunteer_id
                        ))
                    viewset.debug_response(response.data, response.status_code)
                    return response

            class UploadSignedResource(helpers.LoggingHelperMixin, viewsets.GenericViewSet, FieldPackage):
                def update(self, viewset, request, args, kwargs):
                    offer_id = kwargs['lookup_one_value']
                    volunteer_id = kwargs['lookup_two_value']
                    document = viewset.document_class.objects.get(offer=offer_id, volunteer=volunteer_id)
                    kwargs['partial'] = True
                    kwargs['pk'] = document.id
                    viewset.kwargs = kwargs

                    offer = Offer.objects.get(pk=offer_id)
                    volunteer = VolunteerProfile.objects.get(pk=volunteer_id)
                    volunteer_user = User.objects.get(pk=volunteer.user.id)

                    state = viewset.document_state_factory.make(document.status)
                    state.request = request
                    state.assert_can_upload()

                    request.DATA['status'] = state.get_next_state()

                    response = viewset.make_update(kwargs, viewset.serializer_class, request)

                    created_at = datetime.datetime.now()

                    media_path, path = viewset.generate_media_path_for_pdf(created_at, offer, volunteer_user)
                    temp_path = response.data[state.get_uploading_field_value()]
                    file_name, file_ext = os.path.splitext(temp_path)
                    os.rename(os.path.join(settings.MEDIA_ROOT, temp_path), os.path.join(settings.MEDIA_ROOT, '{}{}'.format(
                        path,
                        file_ext
                    )))

                    relative_path_after_move = '{}{}'.format(
                        path,
                        file_ext
                    )

                    response.data[state.get_uploading_field_value()] = relative_path_after_move
                    document = viewset.document_class.objects.get(offer=offer_id, volunteer=volunteer_id)
                    setattr(document, state.get_uploading_field_value(), relative_path_after_move)
                    document.save()

                    log.info("Uploaded signed " +viewset.document_string+ " resource")

                    viewset.debug_response(response.data, response.status_code)
                    return response

            class RequiredPackageSet(FieldPackageSetFactory):
                packages_having_regard_to_order = (
                    {
                        'class': RegenerateNotSignedResource,
                        'required': (),
                        'allowed_not_required': ()
                    },
                    # {
                    #     'class': UploadSignedResource,
                    #     'required': ('volunteer_signed_resource',),
                    #     'allowed_not_required': ()
                    # },
                    # {
                    #     'class': UploadSignedResource,
                    #     'required': ('organization_signed_resource',),
                    #     'allowed_not_required': ()
                    # },
                )

            packages = RequiredPackageSet.make()
            fitting_field_package = self.get_fitting_field_package(packages, request.DATA)
            log.debug("Fitted to package name={}".format(fitting_field_package.__class__.__name__))
            return fitting_field_package.update(self, request, args, kwargs)
        except PermissionHelperMixin.AccessDeniedException:
            self.debug_response_error(403)
            return Response({'detail': "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        except NotFoundException as e:
            self.debug_response_error(404)
            return Response({'detail': e.message}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as err:
            self.debug_response_error(400)
            return Response(err.message_dict, status=status.HTTP_400_BAD_REQUEST)
        except WrongRequestException as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError as e:
            self.debug_response_error(403)
            return Response({'detail': e.message}, status=status.HTTP_403_FORBIDDEN)
        except ObjectDoesNotExist:
            self.debug_response_error(404)
            return Response({'detail': "Given " +self.document_string+ " doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

    #private
    def assert_can_generate_document(self, offer):
        class RequiredPackageSet(FieldPackageSetFactory):
            packages_having_regard_to_order = (
                {
                    'class': FieldPackage,
                    'required': ('title', 'publish_from', 'publish_to', 'volunteer_max_count', 'category',
                        'description_quests', 'description_time', 'description_problem', 'description',
                        'description_requirements', 'description_benefits', 'status', 'agreement_stands_from',
                        'agreement_stands_to', 'agreement_signatories',),
                    'allowed_not_required': ('localization', 'description_additional_requirements',)
                },
            )

        assert RequiredPackageSet.make()[0].is_accomplished(ModelChecker(offer)), "Fill all required fields in offer"
        assert offer.status in (OfferStateFactory.PUBLISHED, OfferStateFactory.PUBLISHED_EDITED), "Offer not published"
        assert offer.publish_to < datetime.datetime.now(), "Offer has not ended yet"

    #private
    def find_tasks(self, offer, volunteer):
        tasks = AgreementTask.objects.filter(offer=offer, volunteer=volunteer)
        if len(tasks) > 0:
            return tasks[0]

        tasks = AgreementTask.objects.filter(offer=offer)
        if len(tasks) > 0:
            return tasks[0]

        raise NotFoundException("Couldn't find any tasks assigned to this " +self.document_string)

    #private
    def generate_pdf(self, *args, **kwargs):
        template = Template('<div id="header">{}</div><div id="footer">{}</div>{}'.format(
            "{% include '" + self.document_static_directory + "/header.html' %}",
            "{% include '" + self.document_static_directory + "/footer.html' %}",
            kwargs['template_object'].body.encode('utf8'),
        ))

        context = Context(self.document_generate_method(*args, **kwargs))
        pdf_path, pdf_filename = self.generate_media_path_for_pdf(kwargs['created_at'], kwargs['offer'],
            kwargs['volunteer_user'])

        self.write_pdf(context, os.path.join(settings.MEDIA_ROOT, pdf_path, pdf_filename), template)
        pdf_filename += '.pdf'

        return {'path': pdf_path, 'filename': pdf_filename}

    #private
    def generate_media_path_for_pdf(self, created_at, offer, volunteer_user):
        filename = u'{}_{}_{}_{}_{}'.format(offer.publishing_organization.fullname.replace(' ', '_'),
            volunteer_user.first_name, volunteer_user.last_name,
            offer.title,
            unicode(self.chop_microseconds(created_at))).replace(' ', '_')
        filename = unicodedata.normalize('NFD', filename).encode('ascii', 'ignore')
        path = self.document_static_directory + '/{}/{}'.format(offer.publishing_organization.shortname, offer.id)

        dirname = os.path.join(settings.MEDIA_ROOT, path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        return path, filename

    #private
    def generate_zip(self, pdfs, **kwargs):
        zip_path, zip_filename = self.generate_media_path_for_zip(kwargs['created_at'], kwargs['offer'])
        zip_filename += '.zip'

        files = [{
            'file': open(os.path.join(settings.MEDIA_ROOT, pdf['path'], pdf['filename'])),
            'path': pdf['path'],
            'filename': pdf['filename']
        } for pdf in pdfs]

        zipped_file = StringIO.StringIO()
        with zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, zip_path, zip_filename), 'w') as zip:
            for i, file in enumerate(files):
                file['file'].seek(0)
                zip.writestr(file['filename'], file['file'].read())

        zipped_file.seek(0)

        return zip_path, zip_filename

    #private
    def generate_media_path_for_zip(self, created_at, offer):
        path = self.document_static_directory + '/{}/{}'.format(offer.publishing_organization.shortname, offer.id)
        filename = u'{}_{}'.format(offer.title,
            str(self.chop_microseconds(created_at)).replace(' ', '_'))
        filename = unicodedata.normalize('NFD', filename).encode('ascii', 'ignore')

        dirname = os.path.dirname(os.path.join(settings.MEDIA_ROOT, path))
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        media_path = os.path.join(settings.MEDIA_ROOT, path)
        return path, filename

    #private
    def chop_microseconds(self, delta):
        return delta - datetime.timedelta(microseconds=delta.microsecond)

    #private
    def write_pdf(self, context, media_path, template):
        HTML(string=template.render(context), base_url=settings.MEDIA_ROOT) \
            .render(stylesheets=[CSS(filename=os.path.join(settings.TEMPLATE_DIR, self.document_static_directory, 'style.css'))]) \
            .write_pdf(u"{}{}".format(media_path, '.pdf'))


class AgreementTemplateViewSet(DocumentTemplateViewSet):
    queryset = AgreementTemplate.objects.all()
    serializer_class = AgreementTemplateSerializer

    document_class = AgreementTemplate
    document_string = 'AgreementTemplate'


class AgreementViewSet(DocumentViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer

    document_class = Agreement
    document_string = 'Agreement'
    document_state_factory = AgreementStateFactory
    document_static_directory = 'agreements'
    template_class = AgreementTemplate
    document_generate_method = agreement_get_keywords


class CertificateTemplateViewSet(DocumentTemplateViewSet):
    queryset = CertificateTemplate.objects.all()
    serializer_class = CertificateTemplateSerializer

    document_class = CertificateTemplate
    document_string = 'CertificateTemplate'


class CertificateViewSet(DocumentViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    document_class = Certificate
    document_string = 'Certificate'
    document_state_factory = CertificateStateFactory
    document_static_directory = 'certificates'
    template_class = CertificateTemplate
    document_generate_method = certificate_get_keywords


class CategorySubscriptionViewSet(helpers.CreateAPIView, helpers.UpdateAPIView, generics.DestroyAPIView,
        helpers.ProfileAssertion, helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    queryset = Settings.objects.all()
    serializer_class = CategorySubscriptionSerializer

    def retrieve(self, request, pk=None):
        try:
            self.debug_request(request)

            assert pk == 'my'
            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            subscriptions = CategorySubscription.objects.filter(user=request.user)

            serializer = CategorySubscriptionSerializer(subscriptions, many=True)

            response = Response(serializer.data, status=status_code)
            self.debug_response(response.data, response.status_code)
            return response
        except Http404 as e:
            self.debug_response_error(404)
            raise e
        except AssertionError:
            self.debug_response_error(400)
            return Response({'detail': "Wrong request data"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            assert not CategorySubscription.objects.filter(user=request.user), "You already have a subscription"

            request.DATA['user'] = request.user.id
            categories = request.DATA['category']

            assert isinstance(categories, (list, tuple)) and len(categories) > 0, "List cannot be empty"

            data = []
            for category in categories:
                request.DATA['category'] = category
                response, serializer = self.make_creation(request, self.serializer_class)
                data.append(response.data)

            response = Response(data, status=response.status_code)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Created category subscription for user id={}".format(request.user.id))
            self.debug_response(response.data, response.status_code)
            return response
        except AssertionError as e:
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        transaction.set_autocommit(False)

        try:
            self.debug_request(request)

            assert kwargs['pk'] == 'my'

            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            subscriptions = CategorySubscription.objects.filter(user=request.user)
            for subscription in subscriptions:
                subscription.delete()

            request.DATA['user'] = request.user.id
            categories = request.DATA['category']

            assert isinstance(categories, (list, tuple)) and len(categories) > 0, "List cannot be empty"

            data = []
            for category in categories:
                request.DATA['category'] = category
                self.kwargs['pk'] = 0
                response, serializer = self.make_creation(request, self.serializer_class)
                data.append(response.data)

                if response.status_code not in (status.HTTP_200_OK, 310):
                    raise IntegrityError("Creating subscription of category id {} failed".format(request.DATA['category']))

            transaction.commit()
            response = Response(data, status=status.HTTP_201_CREATED)
            log.info("Updated category subscription for user id={}".format(request.user.id))
            self.debug_response(response.data, response.status_code)
            return response
        except IntegrityError as e:
            transaction.rollback()
            log.error("Rollback in CategorySubscriptionViewSet.update")
            self.debug_response_error(400)
            return Response({'detail': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except AssertionError:
            self.debug_response_error(400)
            return Response({'detail': "Wrong request data"}, status=status.HTTP_400_BAD_REQUEST)
        finally:
            transaction.set_autocommit(True)

    def destroy(self, request, *args, **kwargs):
        try:
            self.debug_request(request)

            assert kwargs['pk'] == 'my'
            status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

            if 'category' in request.DATA:
                categories = request.DATA['category']

                subscriptions = CategorySubscription.objects.filter(user=request.user, category__in=categories)
            else:
                subscriptions = CategorySubscription.objects.filter(user=request.user)

            for subscription in subscriptions:
                subscription.delete()

            response = Response({'detail': 'Success'}, status=status_code)
            if response.status_code in (status.HTTP_201_CREATED, status.HTTP_200_OK, 310):
                log.info("Destroyed category subscription for user id={}".format(request.user.id))
            self.debug_response(response.data, response.status_code)
            return response
        except AssertionError:
            self.debug_response_error(400)
            return Response({'detail': "Wrong request data"}, status=status.HTTP_400_BAD_REQUEST)


class SessionViewSet(helpers.LoggingHelperMixin, viewsets.GenericViewSet):
    throttle_classes = ()
    permission_classes = (AllowAny,)
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = AuthTokenSerializer
    model = Token

    def list(self, request):
        self.debug_request(request)

        if request.user.is_anonymous():
            response = Response({'detail': 'You are not logged in.'}, status=status.HTTP_404_NOT_FOUND)
            self.debug_response(response.data, response.status_code)
            return response

        status_code = status.HTTP_200_OK
        response = Response(CheckAuthUserSerializer(request.user).data, status=status_code)
        return response

    def create(self, request):
        from .models import VolunteerProfile, UserProfile

        self.debug_request(request)

        serializer = self.serializer_class(data=request.DATA)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(user=serializer.object['user'])

            volunteer_profile = VolunteerProfile.objects.filter(user=serializer.object['user'])
            user_profiles = UserProfile.objects.filter(user=serializer.object['user'])

            is_volunteer = len(volunteer_profile) is not 0
            is_organization = user_profiles and user_profiles[0].organization_member is not None

            response = Response({
                'token': token.key,
                'is_organization': is_organization,
                'is_volunteer': is_volunteer,
                'volunteer_id': volunteer_profile[0].id if is_volunteer else None,
                'organization_id': user_profiles[0].organization_member.id if is_organization else None,
            }, status=status.HTTP_201_CREATED)
            log.info("Logged in user id={}".format(serializer.object['user']))
            self.debug_response(response.data, response.status_code)
            return response

        response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.debug_response(response.data, response.status_code)
        return response


class CheckAuthView(helpers.ProfileAssertion, helpers.LoggingHelperMixin, generics.views.APIView):
    def get(self, request, *args, **kwargs):
        response = SessionViewSet.as_view({'get': 'list'})(request, *args, **kwargs)
        return response


class ObtainAuthToken(helpers.LoggingHelperMixin, APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        response = SessionViewSet.as_view({'post': 'create'})(request, *args, **kwargs)
        return response


def create_userprofile(request):
    log.debug("Request create user profile for user id={}".format(request.user.id))
    url = instance_url() + "/#/"
    response = HttpResponseRedirect(url)

    if request.user.is_anonymous():
        return response

    if request.user.is_authenticated():
        token, created = Token.objects.get_or_create(user=request.user)
        response.set_cookie('token', token)

    existing_profile = UserProfile.objects.filter(user=request.user)

    if existing_profile:
        return response

    user_profile = UserProfile(user=request.user, organization_member=None)
    user_profile.save()

    target = NotificationTarget(user=request.user, target=request.user.email, backend=1, active=True)
    target.save()

    log.info("Created user profile")

    return response
