# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

import datetime
import logging
import sys
from django.conf.urls.static import static
import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Permission
import django_filters
from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from itertools import islice, chain


log = logging.getLogger('apps')


class WrongRequestException(Exception):
    pass

class NotFoundException(Exception):
    pass


class PermissionHelperMixin:
    def add_permission_to_logged_user(self, request, codes):
        for code in codes:
            permission = Permission.objects.get(codename=code)
            request.user.user_permissions.add(permission)
        request.user.save()

    def assert_logged_user_has_permissions(self, request, permissions):
        for permission in permissions:
            if not request.user.has_perm(permission):
                raise PermissionHelperMixin.AccessDeniedException()

    class AccessDeniedException(Exception):
        pass


class OfferPermissionHelperMixin:
    #private
    def assert_has_permissions_to_edit_my_offer(self, offer, user):
        if (offer.step_1.created_by.id != user.id or not user.has_perm('api.edit_my_offer')) \
                and not user.has_perm('api.edit_any_offer'):
            raise PermissionHelperMixin.AccessDeniedException()

    #private
    def assert_has_permissions_to_deactivate_my_offer(self, offer, user):
        if (offer.step_1.created_by.id != user.id or not user.has_perm('api.deactivate_my_offer')) \
                and not user.has_perm('api.deactivate_any_offer'):
            raise PermissionHelperMixin.AccessDeniedException()

    #private
    def assert_has_permissions_to_remove_any_offer(self, offer, user):
        if not user.has_perm('api.remove_any_offer'):
            raise PermissionHelperMixin.AccessDeniedException()

    #private
    def assert_has_permissions_to_publish_my_offer(self, offer, user):
        if (offer.step_1.created_by.id != user.id or not user.has_perm('api.deactivate_my_offer')) \
                and not user.has_perm('api.deactivate_any_offer'):
            raise PermissionHelperMixin.AccessDeniedException()

    #private
    def assert_has_permissions_to_review_my_offer(self, offer, user):
        if not user.has_perm('api.review_any_offer'):
            raise PermissionHelperMixin.AccessDeniedException()

class OrganizationProfilePermissionHelperMixin:
    #private
    def assert_has_permissions_to_edit_my_organization_profile(self, profile, user):
        from .models import UserProfile

        if (profile != UserProfile.objects.get(user=user).organization_member
                or not user.has_perm('api.edit_my_organization_profile')) \
                and not user.has_perm('api.edit_any_organization_profile'):
            raise PermissionHelperMixin.AccessDeniedException()

    #private
    def assert_has_permissions_to_deactivate_my_organization_profile(self, profile, user):
        from .models import UserProfile

        if (profile != UserProfile.objects.get(user=user).organization_member
                or not user.has_perm('api.deactivate_my_organization_profile')) \
                and not user.has_perm('api.deactivate_any_organization_profile'):
            raise PermissionHelperMixin.AccessDeniedException()


class VolunteerProfilePermissionHelperMixin:
    #private
    def assert_has_permissions_to_edit_my_volunteer_profile(self, profile, user):
        if profile.user.id != user.id and not user.has_perm('api.edit_any_volunteer_profile'):
            raise PermissionHelperMixin.AccessDeniedException()


class ApplicationPermissionHelperMixin:
    #private
    def assert_has_permissions_to_accept_my_application(self, application, user):
        from .models import UserProfile

        if application.offer.publishing_organization.id is not UserProfile.objects.get(user=user).organization_member.id or \
                not user.has_perm('api.accept_application'):
            raise PermissionHelperMixin.AccessDeniedException()


class ProfileNotExtendedException(Exception):
    pass


class ProfileAssertion:
    def has_created_org_or_volunteer_profile(self, request):
        from .models import VolunteerProfile, UserProfile

        if request.user.is_anonymous() or request.user.is_superuser:
            return True

        volunteer_profile = VolunteerProfile.objects.filter(user=request.user)
        user_profiles = UserProfile.objects.filter(user=request.user)
        return (len(volunteer_profile) is not 0) or \
               (user_profiles and user_profiles[0].organization_member is not None)

    def assert_has_extended_volunteer_profile(self, request):
        from .models import VolunteerProfile
        from .field_packages import FieldPackageSetFactory, FieldPackage, ModelChecker

        class CheckingPackageSet(FieldPackageSetFactory):
            packages_having_regard_to_order = (
                {
                    'class': FieldPackage,
                    'required': ('pesel', 'street', 'house_number', 'zipcode', 'city', 'country',),
                    'allowed_not_required': ('proof_number', 'apartment_number',)
                },
            )

        if request.user.is_anonymous():
            return True

        volunteer_profile = VolunteerProfile.objects.filter(user=request.user)

        if not (len(volunteer_profile) is not 0) or \
                not CheckingPackageSet.make()[0].is_accomplished(ModelChecker(volunteer_profile[0])):
            raise ProfileNotExtendedException()


class UpdateAPIView(ProfileAssertion, generics.UpdateAPIView):
    def make_update(self, kwargs, serializer, request):
        status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

        partial = kwargs.pop('partial', False)
        self.object = self.get_object_or_none()
        serializer = serializer(self.object, data=request.DATA,
            files=request.FILES, partial=partial)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.pre_save(serializer.object)
        if self.object is None:
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            return Response(serializer.data, status=status_code)
        self.object = serializer.save(force_update=True)
        self.post_save(self.object, created=False)
        return Response(serializer.data, status=status_code)

    #private
    def prevent_modifying(self, params, request, model):
        for param in params:
            request.DATA[param] = model.__getattribute__(param)


class CreateAPIView(ProfileAssertion, generics.CreateAPIView):
    def make_creation(self, request, serializer):
        status_code = status.HTTP_201_CREATED if self.has_created_org_or_volunteer_profile(request) else 310

        serializer = serializer(data=request.DATA, files=request.FILES)
        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.object = serializer.save(force_insert=True)
            self.post_save(self.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status_code,
                headers=headers), serializer
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST), serializer


class ListFilter(django_filters.Filter):
    def __init__(self, name=None, label=None, widget=None, action=None,
            lookup_type='exact', required=False, distinct=False, exclude=False, **kwargs):
        super(ListFilter, self).__init__(name=name, label=label, widget=widget, action=action,
            lookup_type='in', required=required, distinct=True, exclude=exclude, **kwargs)

    def filter(self, qs, value):
        if value is None or not len(value):
            return qs
        return super(ListFilter, self).filter(qs, value.split(","))


class ThumbnailCreateAPIView(ProfileAssertion, generics.CreateAPIView, generics.UpdateAPIView):
    def create(self, request, *args, **kwargs):
        status_code = status.HTTP_201_CREATED if self.has_created_org_or_volunteer_profile(request) else 310

        serializers = {}
        for key in self.thumbnail_classes.keys():
            serializers[key] = self.thumbnail_classes[key](data=request.DATA, files=request.FILES)

        for serializer in serializers.values():
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for serializer in serializers.values():
            headers = self.upload_file(serializer)
            self.change_to_absolute_path(serializer)

        response = self.generate_response(serializers)
        return Response(response, status=status_code, headers=headers)

    def update(self, request, *args, **kwargs):
        status_code = status.HTTP_200_OK if self.has_created_org_or_volunteer_profile(request) else 310

        if len(request.FILES):
            self.delete_existing_thumbnails(request)
        else:
            return Response({'filename': u'File not provided'}, status=status.HTTP_400_BAD_REQUEST)

        serializers = {}
        for key in self.thumbnail_classes.keys():
            serializers[key] = self.thumbnail_classes[key](data=request.DATA, files=request.FILES)

        for serializer in serializers.values():
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for serializer in serializers.values():
            headers = self.upload_file(serializer)
            self.change_to_absolute_path(serializer)

        response = self.generate_response(serializers)
        return Response(response, status=status_code, headers=headers)

    #private
    def delete_existing_thumbnails(self, request):
        kwargs = {self.keyword: request.DATA.get(self.keyword)}

        for key in self.thumbnail_classes.keys():
            try:
                existing_thumbnail = self.thumbnail_classes[key].Meta.model.objects.get(**kwargs)
                os.remove('{}/{}'.format(settings.MEDIA_ROOT, existing_thumbnail.filename))
                existing_thumbnail.delete()
            except ObjectDoesNotExist:
                continue

    #private
    def upload_file(self, serializer):
        self.pre_save(serializer.object)
        self.object = serializer.save(force_insert=True)
        self.post_save(self.object, created=True)
        return self.get_success_headers(serializer.data)

    #private
    def change_to_absolute_path(self, serializer):
        serializer.data['filename'] = settings.MEDIA_URL + serializer.data['filename']

    #private
    def generate_response(self, serializers):
        response = {}
        for key in serializers.keys():
            response[key] = serializers[key].data
        return response


class QuerySetChain(object):
    """
    Chains multiple subquerysets (possibly of different models) and behaves as
    one queryset.  Supports minimal methods needed for use with
    django.core.paginator.
    """

    def __init__(self, *subquerysets):
        self.querysets = subquerysets

    def count(self):
        """
        Performs a .count() for all subquerysets and returns the number of
        records as an integer.
        """
        return sum(qs.count() for qs in self.querysets)

    def _clone(self):
        "Returns a clone of this queryset chain"
        return self.__class__(*self.querysets)

    def _all(self):
        "Iterates records in all subquerysets"
        return chain(*self.querysets)

    def __getitem__(self, ndx):
        """
        Retrieves an item or slice from the chained set of results from all
        subquerysets.
        """
        if type(ndx) is slice:
            return list(islice(self._all(), ndx.start, ndx.stop, ndx.step or 1))
        else:
            return islice(self._all(), ndx, ndx+1).next()

    def __iter__(self):
        for item in self._all():
            yield item


class FieldPackageHelperMixin:
    #private
    def get_fitting_field_package(self, packages, data):
        for package in packages:
            if package.fits_to(data):
                return package
        raise WrongRequestException("No fitting field package")

    #private
    def prevent_modifying_any_field(self, request):
        for key in request.DATA.keys():
            del request.DATA[key]


class LoggingHelperMixin:
    def debug_request(self, request):
        cleared_request = request.DATA.copy()
        if 'password' in cleared_request:
            del cleared_request['password']
            
        log.debug("Request {}.{} with params: kwargs={}, request={}".format(
            str(self.__class__.__name__),
            sys._getframe(1).f_code.co_name,
            self.kwargs,
            cleared_request
        ))

    def debug_response(self, data, code):
        log.debug("Response {}.{} with params: code={}, data={}".format(
            str(self.__class__.__name__),
            sys._getframe(1).f_code.co_name,
            code,
            data
        ))

    def debug_response_error(self, code):
        log.error("Response {}.{} with params: code={}".format(
            str(self.__class__.__name__),
            sys._getframe(1).f_code.co_name,
            code
        ))

    def debug_MY_id_translated_to(self, id):
        log.debug("Got 'my' identifier. Translated to id={}".format(id))


class Benchmark:
    @classmethod
    def start(cls):
        self = cls()

        self.start_micro = datetime.datetime.now()
        self.start = self.chop_microseconds(self.start_micro)

        return self

    #private
    def chop_microseconds(self, delta):
        return delta - datetime.timedelta(microseconds=delta.microsecond)

    def stop(self):
        self.end = datetime.datetime.now()

    def duration(self):
        return self.end-self.start_micro


class DocumentTemplateHelper:
    #private
    def find_template_for_offer(self, offer):
        offer_templates = self.template_class.objects.filter(offer=offer)
        if len(offer_templates) > 0:
            return offer_templates[0], True

        organization_templates = self.template_class.objects.filter(organization=offer.publishing_organization, offer=None)
        if len(organization_templates) > 0:
            return organization_templates[0], False

        general_templates = self.template_class.objects.filter(is_general=True)
        if len(general_templates) > 0:
            return general_templates[0], False

        raise NotFoundException("Couldn't find any template to this agreement")

    #private
    def find_template_for_org(self, org):
        organization_templates = self.template_class.objects.filter(organization=org, offer=None)
        if len(organization_templates) > 0:
            return organization_templates[0], True

        general_templates = self.template_class.objects.filter(is_general=True)
        if len(general_templates) > 0:
            return general_templates[0], False

        raise NotFoundException("Couldn't find any template to this agreement")


def instance_url():
    from apps.api.models import Settings

    settings = Settings.objects.get(settings__contains=['instance_url'])
    return settings.settings['instance_url']