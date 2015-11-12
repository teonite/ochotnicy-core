# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from app_metrics.models import Gauge
from django.conf import settings
from django.db.models import Sum
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Organization, VolunteerProfile, UserProfile, Offer, Category, LargeOfferThumbnail, \
    SmallOfferThumbnail, OrganizationThumbnail, OriginalOfferThumbnail, OriginalOrganizationThumbnail, Ability, \
    PromotedOfferThumbnail, Education, Application, OrganizationType, Settings, CategorySubscription, Agreement, \
    OrganizationSignatory, AgreementTask, AgreementTemplate, OrgAbility, Rating, Testimonial, OrgRating, OrgTestimonial, \
    Certificate, CertificateTemplate, NewsThumbnail, News, VolunteerProfileThumbnail, OriginalVolunteerProfileThumbnail
from .fields import SmartPrimaryKeyRelatedField
from rest_framework.fields import IntegerField
from rest_framework_hstore.fields import HStoreField
from rest_framework_hstore.serializers import HStoreSerializer


class OriginalThumbnailOrganizationWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    organization = SmartPrimaryKeyRelatedField()

    class Meta:
        model = OriginalOrganizationThumbnail


class OriginalThumbnailVolunteerProfileWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    volunteer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = OriginalVolunteerProfileThumbnail


class ThumbnailOrganizationReadableSerializer(serializers.ModelSerializer):
    filename = serializers.Field('filename.url')

    class Meta:
        model = OrganizationThumbnail
        fields = ('filename', 'id',)


class ThumbnailOrganizationWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    organization = SmartPrimaryKeyRelatedField()

    class Meta:
        model = OrganizationThumbnail


class ThumbnailVolunteerProfileReadableSerializer(serializers.ModelSerializer):
    filename = serializers.Field('filename.url')

    class Meta:
        model = VolunteerProfileThumbnail
        fields = ('filename', 'id',)


class ThumbnailVolunteerProfileWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    volunteer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = VolunteerProfileThumbnail


class ThumbnailNewsWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    news = SmartPrimaryKeyRelatedField()

    class Meta:
        model = NewsThumbnail


class ThumbnailNewsReadableSerializer(serializers.ModelSerializer):
    filename = serializers.Field('filename.url')

    class Meta:
        model = NewsThumbnail


class OrganizationThumbnailReadableSerializer(serializers.ModelSerializer):
    filename = serializers.Field('filename.url')

    class Meta:
        model = OrganizationThumbnail


class OrganizationSignatoryWritableSerializer(serializers.ModelSerializer):
    organization = SmartPrimaryKeyRelatedField()

    class Meta:
        model = OrganizationSignatory


class UserProfileReadableSerializer(serializers.ModelSerializer):
    username = serializers.Field('user.username')

    class Meta:
        model = UserProfile
        fields = ('username',)


class UserReadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)


class OrganizationWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization


class OrganizationCoordinatorReadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class OrganizationListSerializer(serializers.ModelSerializer):
    thumbnail_relation = ThumbnailOrganizationReadableSerializer()
    offers_active_count = serializers.Field(source='get_offers_active_count')
    coordinator = OrganizationCoordinatorReadableSerializer(source='coordinator')
    can_autoskip = serializers.Field(source='can_autoskip')

    class Meta:
        model = Organization
        fields = ('fullname', 'thumbnail_relation', 'id', 'offers_active_count', 'coordinator', 'can_autoskip',)


class OrganizationReadableSerializer(serializers.ModelSerializer):
    coordinator = OrganizationCoordinatorReadableSerializer(source='coordinator')
    type = serializers.Field(source='type.name')
    thumbnail_relation = ThumbnailOrganizationReadableSerializer()

    class Meta:
        model = Organization
        exclude = ('user',)
        fields = ('type', 'id', 'fullname', 'shortname', 'street', 'house_number', 'apartment_number',
            'zipcode', 'district', 'city', 'province', 'country', 'nip', 'krs', 'phonenumber', 'description',
            'is_active', 'thumbnail_relation', 'coordinator')


class AbilityReadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ability


class OrgAbilityReadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrgAbility


class EducationReadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education


class OrganizationTypeReadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType


class VolunteerProfileWritableSerializer(serializers.ModelSerializer):
    user = SmartPrimaryKeyRelatedField()
    education = SmartPrimaryKeyRelatedField()
    abilities = SmartPrimaryKeyRelatedField(many=True)


    class Meta:
        model = VolunteerProfile


class VolunteerProfileReadableSerializer(serializers.ModelSerializer):
    username = serializers.Field(source='user.username')
    first_name = serializers.Field(source='user.first_name')
    last_name = serializers.Field(source='user.last_name')
    email = serializers.Field(source='user.email')
    user_id = serializers.Field(source='user.id')
    education = EducationReadableSerializer()
    abilities = AbilityReadableSerializer(many=True)
    thumbnail_relation = ThumbnailVolunteerProfileReadableSerializer()

    class Meta:
        model = VolunteerProfile
        exclude = ('user',)


class CategorySubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorySubscription


class CategoryReadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category


class OriginalThumbnailOfferWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    offer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = OriginalOfferThumbnail


class LargeThumbnailOfferWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    offer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = LargeOfferThumbnail


class LargeThumbnailOfferReadableSerializer(serializers.ModelSerializer):
    filename = serializers.Field('filename.url')

    class Meta:
        model = LargeOfferThumbnail
        fields = ('filename', 'id',)


class PromotedThumbnailOfferWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    offer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = PromotedOfferThumbnail


class PromotedThumbnailOfferReadableSerializer(serializers.ModelSerializer):
    filename = serializers.Field('filename.url')

    class Meta:
        model = PromotedOfferThumbnail
        fields = ('filename', 'id',)


class SmallThumbnailOfferWritableSerializer(serializers.ModelSerializer):
    filename = serializers.ImageField()
    offer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = SmallOfferThumbnail


class SmallThumbnailOfferReadableSerializer(serializers.ModelSerializer):
    filename = serializers.Field('filename.url')

    class Meta:
        model = SmallOfferThumbnail
        fields = ('filename', 'id',)


class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement


class AgreementTemplateSerializer(serializers.ModelSerializer):
    organization = SmartPrimaryKeyRelatedField()
    offer = SmartPrimaryKeyRelatedField(required=False)

    class Meta:
        model = AgreementTemplate


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate


class CertificateTemplateSerializer(serializers.ModelSerializer):
    organization = SmartPrimaryKeyRelatedField()
    offer = SmartPrimaryKeyRelatedField(required=False)

    class Meta:
        model = CertificateTemplate


class OfferGenericReadableSerializer(serializers.ModelSerializer):
    large_thumbnail_relation = LargeThumbnailOfferReadableSerializer()
    small_thumbnail_relation = SmallThumbnailOfferReadableSerializer()
    promoted_thumbnail_relation = PromotedThumbnailOfferReadableSerializer()
    category = CategoryReadableSerializer()
    published_by = UserReadableSerializer()
    publishing_organization = OrganizationReadableSerializer()
    last_modified_by = UserReadableSerializer()
    volunteers_joined_count = serializers.Field(source='get_volunteers_joined_count')
    volunteers_rejected_count = serializers.Field(source='get_volunteers_rejected_count')
    remaining_time = serializers.Field(source='get_remaining_time')
    is_current = serializers.Field(source='is_current')


class OfferDetailSerializer(OfferGenericReadableSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'title', 'category', 'description', 'description_problem', 'large_thumbnail_relation',
            'description_requirements', 'description_quests', 'description_benefits', 'description_time',
            'description_additional_requirements', 'publishing_organization', 'remaining_time',
            'volunteers_joined_count', 'volunteer_max_count', 'is_current', 'localization', 'publish_to', 'publish_from',
            'agreement_stands_from', 'agreement_stands_to', 'agreement_signatories', 'views_count_volunteers', 'views_count_guests',)


class OrganizationOffersListSerializer(OfferGenericReadableSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'title', 'category', 'publish_from', 'publish_to', 'volunteers_joined_count', 'volunteer_max_count',
            'volunteers_rejected_count', 'status', 'small_thumbnail_relation')


class OfferListSerializer(OfferGenericReadableSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'title', 'small_thumbnail_relation', 'category', 'publishing_organization',
            'volunteer_max_count', 'volunteers_joined_count', 'remaining_time', 'status', 'publish_to', 'publish_from')


class AdminOfferListSerializer(OfferGenericReadableSerializer):
    created_at = serializers.Field(source='step_2.created_at')

    class Meta:
        model = Offer
        fields = ('id', 'title', 'small_thumbnail_relation', 'category', 'publishing_organization', 'created_at', 'is_promoted',
            'volunteer_max_count', 'volunteers_joined_count', 'remaining_time', 'status', 'publish_to', 'publish_from',
            'published_at')


class OfferForApplicationSerializer(OfferGenericReadableSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'title', 'small_thumbnail_relation', 'category', 'publishing_organization', 'agreement_stands_to',
            'volunteer_max_count', 'volunteers_joined_count', 'remaining_time', 'status', 'publish_to', 'publish_from')


class PromotedOfferListSerializer(OfferGenericReadableSerializer):
    publishing_organization = serializers.Field(source='publishing_organization.fullname')

    class Meta:
        model = Offer
        fields = ('id', 'title', 'promoted_thumbnail_relation', 'publishing_organization', 'volunteers_joined_count',
                  'volunteer_max_count')


class OfferWritableSerializer(serializers.ModelSerializer):
    category = SmartPrimaryKeyRelatedField(many=True, required=False)
    published_by = SmartPrimaryKeyRelatedField(required=False)
    depublished_by = SmartPrimaryKeyRelatedField(required=False)
    publishing_organization = SmartPrimaryKeyRelatedField(required=False)
    step_1 = SmartPrimaryKeyRelatedField(required=False)
    step_2 = SmartPrimaryKeyRelatedField(required=False)

    class Meta:
        model = Offer


class AgreementTaskSerializer(serializers.ModelSerializer):
    offer = SmartPrimaryKeyRelatedField()
    volunteer = SmartPrimaryKeyRelatedField(required=False)

    class Meta:
        model = AgreementTask


class UserWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 1
        exclude = ("is_staff", "is_superuser", "groups", "user_permissions")
        write_only_fields = ('password',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 1
        exclude = ("password", "is_staff", "is_superuser", "groups", "user_permissions")


class UserMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        depth = 1
        fields = ("first_name", "last_name", "email", "id")


class CheckAuthUserSerializer(serializers.ModelSerializer):
    is_organization = serializers.SerializerMethodField('get_is_organization')
    is_volunteer = serializers.SerializerMethodField('get_is_volunteer')
    volunteer_id = serializers.SerializerMethodField('get_volunteer_id')
    organization_id = serializers.SerializerMethodField('get_organization_id')
    avatar = serializers.SerializerMethodField('get_avatar')

    class Meta:
        model = User
        depth = 1
        exclude = ("password", "is_staff", "groups", "user_permissions")

    def __init__(self, *args, **kwargs):
        super(CheckAuthUserSerializer, self).__init__(*args, **kwargs)

        self.volunteer_profile = VolunteerProfile.objects.filter(user=self.object)
        self.user_profiles = UserProfile.objects.filter(user=self.object)

        self.is_volunteer = len(self.volunteer_profile) is not 0
        self.is_organization = len(self.user_profiles) and self.user_profiles[0].organization_member is not None

    def get_is_volunteer(self, obj):
        return self.is_volunteer

    def get_is_organization(self, obj):
        return self.is_organization

    def get_volunteer_id(self, obj):
        return self.volunteer_profile[0].id if self.is_volunteer else None

    def get_organization_id(self, obj):
        return self.user_profiles[0].organization_member.id if self.is_organization else None

    def get_avatar(self, obj):
        ret = None
        if self.is_volunteer:
            try:
                ret = VolunteerProfileThumbnail.objects.get(volunteer_id=self.volunteer_profile[0].id).filename.url
            except VolunteerProfileThumbnail.DoesNotExist:
                pass
        elif self.is_organization:
            try:
                ret = OrganizationThumbnail.objects.get(
                    organization_id=self.user_profiles[0].organization_member.id
                ).filename.url
            except OrganizationThumbnail.DoesNotExist:
                pass
        return ret


class ApplicationWritableSerializer(serializers.ModelSerializer):
    volunteer = SmartPrimaryKeyRelatedField()
    offer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = Application


class RatingWritableSerializer(serializers.ModelSerializer):
    volunteer = SmartPrimaryKeyRelatedField()
    offer = SmartPrimaryKeyRelatedField()
    ability = SmartPrimaryKeyRelatedField()

    class Meta:
        model = Rating


class TestimonialWritableSerializer(serializers.ModelSerializer):
    volunteer = SmartPrimaryKeyRelatedField()
    offer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = Testimonial


class OrgRatingWritableSerializer(serializers.ModelSerializer):
    organization = SmartPrimaryKeyRelatedField()
    offer = SmartPrimaryKeyRelatedField()
    ability = SmartPrimaryKeyRelatedField()

    class Meta:
        model = OrgRating


class OrgTestimonialWritableSerializer(serializers.ModelSerializer):
    organization = SmartPrimaryKeyRelatedField()
    offer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = OrgTestimonial


class ApplicationDetailSerializer(serializers.ModelSerializer):
    volunteer = SmartPrimaryKeyRelatedField()
    offer = SmartPrimaryKeyRelatedField()

    class Meta:
        model = Application
        fields = ('status', 'message', 'volunteer', 'offer', 'created_at', 'last_modified_at',)


class VolunteerProfileForOfferReadableSerializer(serializers.ModelSerializer):
    first_name = serializers.Field(source='user.first_name')
    last_name = serializers.Field(source='user.last_name')
    abilities = AbilityReadableSerializer(many=True)
    thumbnail_relation = ThumbnailVolunteerProfileReadableSerializer()

    class Meta:
        model = VolunteerProfile
        fields = ('id', 'abilities', 'first_name', 'last_name', 'thumbnail_relation',)


class VolunteerProfileListSerializer(serializers.ModelSerializer):
    first_name = serializers.Field(source='user.first_name')
    last_name = serializers.Field(source='user.last_name')
    email = serializers.Field(source='user.email')
    applications = serializers.Field(source='get_application_count')
    applications_in_review = serializers.Field(source='get_application_in_review_count')
    applications_rejected = serializers.Field(source='get_application_rejected_count')
    thumbnail_relation = ThumbnailVolunteerProfileReadableSerializer()

    class Meta:
        model = VolunteerProfile
        fields = ('id', 'pesel', 'first_name', 'last_name', 'email', 'applications', 'applications_in_review',
            'applications_rejected', 'thumbnail_relation')


class ApplicationsForOfferReadableSerializer(serializers.ModelSerializer):
    volunteer = VolunteerProfileForOfferReadableSerializer()

    class Meta:
        model = Application
        fields = ('id', 'status', 'volunteer', 'created_at', 'message', 'created_at', 'last_modified_at',)


class ApplicationListSerializer(serializers.ModelSerializer):
    title = serializers.Field(source='offer.title')
    organization_fullname = serializers.Field(source='offer.publishing_organization.fullname')
    publish_from = serializers.Field(source='offer.publish_from')
    offer = OfferForApplicationSerializer('offer')

    class Meta:
        model = Application
        fields = ('created_at', 'status', 'title', 'organization_fullname', 'publish_from', 'offer', 'last_modified_at', 'message')


class SettingsListSerializer(serializers.ModelSerializer):
    settings = HStoreField()

    class Meta:
        model = Settings
        fields = ('settings',)


class SignedResourceSerializer(serializers.ModelSerializer):
    volunteer_signed_resource = serializers.ImageField()

    class Meta:
        model = Agreement
        fields = ('volunteer_signed_resource',)


class NewsWritableSerializer(serializers.ModelSerializer):
    created_by = SmartPrimaryKeyRelatedField()

    class Meta:
        model = News


class NewsReadableSerializer(serializers.ModelSerializer):
    news_thumbnail = ThumbnailNewsReadableSerializer()
    created_by = UserMinimalSerializer('created_by')

    class Meta:
        model = News
        fields = ('title', 'body', 'created_by', 'created_at', 'id', 'news_thumbnail',)


class GaugeReadableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gauge
        fields = ('slug', 'current_value',)