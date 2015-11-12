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
from apps.api.certificates_states import CertificateStateFactory
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib import admin
from django.db.models import IntegerField, CharField, DateField, TextField, OneToOneField, ForeignKey, ManyToManyField, \
    BooleanField, SlugField, DateTimeField, Q
from django.contrib.auth.models import User
from django.db.models.aggregates import Count
from django.dispatch import receiver
from django_countries.fields import CountryField
from django_hstore import hstore
from easy_thumbnails.fields import ThumbnailerImageField
from easy_thumbnails.files import get_thumbnailer, ThumbnailerImageFieldFile
from easy_thumbnails.templatetags.thumbnail import thumbnail_url, thumbnail, thumbnailer
from .application_states import ApplicationStateFactory
from .agreements_states import AgreementStateFactory
from reversion.models import Version
from .offer_states import OfferStateFactory


class Settings(models.Model):
    settings = hstore.DictionaryField()

    objects = hstore.HStoreManager()

    def __unicode__(self):
        return "Default settings"

    class Meta:
        permissions = (
            ("read_any_setting", "Can read any setting"),
            ("write_any_setting", "Can create/update any setting"),
        )


class OrganizationType(models.Model):
    name = CharField(max_length=255)
    is_krs_required = BooleanField()
    is_nip_required = BooleanField()

    def __unicode__(self):
        return self.name


class Organization(models.Model):
    type = ForeignKey(OrganizationType)
    coordinator = ForeignKey(User)

    fullname = CharField(max_length=255)
    shortname = CharField(max_length=255)
    nip = CharField(max_length=30, blank=True, null=True, default="")
    krs = CharField(max_length=30, blank=True, null=True, default="")
    phonenumber = CharField(max_length=40, blank=True, null=True, default="")

    street = CharField(max_length=255)
    house_number = CharField(max_length=10)
    apartment_number = CharField(max_length=10, blank=True, null=True, default="")
    zipcode = CharField(max_length=20)
    district = CharField(max_length=255, blank=True, null=True, default="")
    city = CharField(max_length=255)
    province = CharField(max_length=255, blank=True, null=True, default="")
    country = CountryField()

    description = TextField(max_length=350, blank=True, null=True, default="")

    is_active = BooleanField(blank=True, default=True)
    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')

    def __unicode__(self):
        return self.shortname

    class Meta:
        permissions = (
            ("edit_any_organization_profile", "Can edit any organization profile"),
            ("edit_my_organization_profile", "Can edit my organization profile"),
            ("deactivate_any_organization_profile", "Can deactivate any organization profile"),
            ("deactivate_my_organization_profile", "Can deactivate my organization profile"),
            ("view_organization_list", "Can view organization list")
        )

    def get_offers_active_count(self):
        return Offer.objects.filter(Q(publishing_organization=self) &
            Q(Q(status=OfferStateFactory.PUBLISHED) | Q(status=OfferStateFactory.PUBLISHED_EDITED))).count()

    def can_autoskip(self):
        return self.coordinator.has_perm('api.skip_review')


class OrganizationSignatory(models.Model):
    organization = ForeignKey(Organization)

    first_name = CharField(max_length=40)
    last_name = CharField(max_length=50)
    position = CharField(max_length=50, blank=True, null=True, default="")

    def __unicode__(self):
        return u"{} {}".format(self.first_name, self.last_name)


class OrganizationThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='organization-thumbnails', resize_source={
        'size': (256, 256),
        'crop': "0,0"
    })
    description = CharField(max_length=255, blank=True, default='')
    organization = OneToOneField(Organization, blank=True, null=True, related_name="thumbnail_relation")

    def __unicode__(self):
        return self.filename


class OriginalOrganizationThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='original-organization-thumbnails')
    description = CharField(max_length=255, blank=True, default='')
    organization = OneToOneField(Organization, blank=True, null=True, related_name="original_thumbnail_relation")

    def __unicode__(self):
        return self.filename


class Education(models.Model):
    name = CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Ability(models.Model):
    name = CharField(max_length=255)

    def __unicode__(self):
        return self.name


class OrgAbility(models.Model):
    name = CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = CharField(max_length=30)

    def __unicode__(self):
        return self.name


class CeleryTask(models.Model):
    slug = SlugField()
    performed_at = DateTimeField()
    duration = CharField(max_length=255)

    def __unicode__(self):
        return "{} - {}".format(self.slug, self.performed_at)


class CategorySubscription(models.Model):
    user = ForeignKey(User)
    category = ForeignKey(Category)

    def __unicode__(self):
        return '{} - {}'.format(self.user.username, self.category.name)

    class Meta:
        unique_together = (('user', 'category'),)


class VolunteerProfile(models.Model):
    NOT_SPECIFIED = 0
    MALE = 1
    FEMALE = 2
    GENDER = (
        (NOT_SPECIFIED, 'nie określono'),
        (MALE, 'mężczyzna'),
        (FEMALE, 'kobieta'),
    )

    IDENTITY_CARD = 0
    SCHOOL_CARD = 1
    HIGHSCHOOL_CARD = 2
    PASSPORT = 3
    PROOF_TYPE = (
        (IDENTITY_CARD, 'dowód osobisty'),
        (SCHOOL_CARD, 'legitymacja szkolna'),
        (HIGHSCHOOL_CARD, 'legitymacja studencka'),
        (PASSPORT, 'paszport')
    )

    user = OneToOneField(User)
    birthday = DateField()
    gender = IntegerField(choices=GENDER, blank=True, null=True, default=NOT_SPECIFIED)
    phonenumber = CharField(max_length=40, blank=True, null=True, default="")

    pesel = CharField(max_length=11, blank=True, null=True, default="")
    proof_type = IntegerField(choices=PROOF_TYPE, default=IDENTITY_CARD)
    proof_number = CharField(max_length=20, blank=True, null=True, default="")

    street = CharField(max_length=255, blank=True, null=True, default="")
    house_number = CharField(max_length=10, blank=True, null=True, default="")
    apartment_number = CharField(max_length=10, blank=True, null=True, default="")
    zipcode = CharField(max_length=20, blank=True, null=True, default="")
    city = CharField(max_length=255, blank=True, null=True, default="")
    country = CountryField(blank=True, null=True, default=None)

    about = TextField()
    education = ForeignKey(Education)
    abilities = ManyToManyField(Ability, related_name='volunteer_abilities_set')
    abilities_description = TextField(max_length=500, blank=True, null=True, default="")

    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')

    def __unicode__(self):
        return self.user.username

    class Meta:
        permissions = (
            ('edit_any_volunteer_profile', "Can edit any volunteer profile"),
            ('skip_review', "Are offers skipped from review?"),
            ('view_volunteer_list', "Can view volunteer list")
        )

    def is_older_or_equal_to(self, age):
        delta = self.age()
        return delta >= datetime.timedelta(days=365.25*age)

    def age(self):
        return datetime.datetime.now() - datetime.datetime(self.birthday.year, self.birthday.month, self.birthday.day)

    def get_application_count(self):
        return Application.objects.filter(volunteer=self).count()

    def get_application_in_review_count(self):
        return Application.objects.filter(volunteer=self, status=ApplicationStateFactory.PENDING_TO_REVIEW).count()

    def get_application_rejected_count(self):
        return Application.objects.filter(volunteer=self, status=ApplicationStateFactory.REJECTED).count()


class VolunteerProfileThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='volunteer-thumbnails', resize_source={
        'size': (256, 256),
        'crop': "0,0"
    })
    description = CharField(max_length=255, blank=True, default='')
    volunteer = OneToOneField(VolunteerProfile, blank=True, null=True, related_name="thumbnail_relation")

    def __unicode__(self):
        return self.filename


class OriginalVolunteerProfileThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='original-volunteer-thumbnails')
    description = CharField(max_length=255, blank=True, default='')
    volunteer = OneToOneField(VolunteerProfile, blank=True, null=True, related_name="original_thumbnail_relation")

    def __unicode__(self):
        return self.filename


class ResourceMetadata(models.Model):
    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')
    created_by = ForeignKey(User, blank=True, default=None, related_name='created_set')

    last_modified_at = DateTimeField(auto_now=True, blank=datetime.datetime.now(), null=True, default='')
    last_modified_by = ForeignKey(User, blank=True, default=None, related_name='last_modified_set')

    def __unicode__(self):
        return "Created at: {}".format(self.created_at)


class Offer(models.Model):
    title = CharField(max_length=200, blank=True, null=True, default='')
    category = ManyToManyField(Category, blank=True, null=True)
    publishing_organization = ForeignKey(Organization, blank=True, null=True, related_name='publishing_organization_set')
    publish_from = DateTimeField(blank=True, null=True, default=datetime.datetime.now())
    publish_to = DateTimeField(blank=True, null=True, default=datetime.datetime.now())
    published_by = ForeignKey(User, blank=True, null=True, related_name='publisher_set')
    published_at = DateTimeField(blank=True, null=True, default='')
    depublished_by = ForeignKey(User, blank=True, null=True, related_name='depublisher_set')
    depublished_at = DateTimeField(blank=True, null=True, default='')
    volunteer_max_count = IntegerField(blank=True, default=0)
    is_promoted = BooleanField(blank=True, default=False)
    localization = CharField(max_length=255, blank=True, null=True, default='')
    description = TextField(max_length=1000, blank=True, null=True, default='')
    description_time = TextField(max_length=200, blank=True, null=True, default='')
    description_problem = TextField(max_length=500, blank=True, null=True, default='')
    description_requirements = TextField(max_length=600, blank=True, null=True, default='')
    description_quests = TextField(max_length=1000, blank=True, null=True, default='')
    description_benefits = TextField(max_length=800, blank=True, null=True, default='')
    description_additional_requirements = TextField(max_length=600, blank=True, null=True, default='')
    status = IntegerField(choices=OfferStateFactory.available_statuses, blank=True, default=0)
    status_change_reason = CharField(max_length=255, blank=True, null=True)

    agreement_stands_from = DateField(blank=True, null=True)
    agreement_stands_to = DateField(blank=True, null=True)
    agreement_signatories = ManyToManyField(OrganizationSignatory, blank=True, null=True)

    step_1 = ForeignKey(ResourceMetadata, blank=True, null=True, related_name='first_step_set')
    step_2 = ForeignKey(ResourceMetadata, blank=True, null=True, related_name='second_step_set')

    views_count_volunteers = IntegerField(blank=True, default=0)
    views_count_guests = IntegerField(blank=True, default=0)

    def __unicode__(self):
        return self.title

    class Meta:
        permissions = (
            ('create_offer', "Can create own offer"),
            ('edit_my_offer', "Can edit own offer"),
            ('edit_any_offer', "Can edit any offer"),
            ('deactivate_my_offer', "Can deactivate own offer"),
            ('deactivate_any_offer', "Can deactivate any offer"),
            ('publish_my_offer', "Can publish my offer"),
            ('publish_any_offer', "Can publish any offer"),
            ('remove_any_offer', "Can remove any offer"),
            ('review_any_offer', "Can review any offer"),
            ('view_admin_offer_list', "Can view admin offer list"),
            ('view_any_offer', "Can view any offer details"),
            ('promote_offer', "Can promote offers")
        )

    def get_remaining_time(self):
        return max(self.publish_to - datetime.datetime.now(), datetime.timedelta())

    def get_volunteers_joined_count(self):
        applications = Application.objects.filter(offer=self.pk, status=ApplicationStateFactory.ACCEPTED)
        return len(applications)

    def get_volunteers_rejected_count(self):
        applications = Application.objects.filter(offer=self.pk, status=ApplicationStateFactory.REJECTED)
        return len(applications)

    def is_current(self):
        if self.publish_from < datetime.datetime.now() < self.publish_to:
            return True
        return False


class Review(models.Model):
    organization = ForeignKey(Organization)
    offer = ForeignKey(Offer)


class Rating(models.Model):
    volunteer = ForeignKey(VolunteerProfile)
    offer = ForeignKey(Offer, related_name='offer_rating_set')
    ability = ForeignKey(Ability)

    rating = IntegerField()

    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')
    created_by = ForeignKey(User, blank=True, default=None)

    class Meta:
        unique_together = (('volunteer', 'offer', 'ability',),)


class OrgRating(models.Model):
    organization = ForeignKey(Organization)
    offer = ForeignKey(Offer, related_name='offer_orgrating_set')
    ability = ForeignKey(OrgAbility)

    rating = IntegerField()

    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')
    created_by = ForeignKey(User, blank=True, default=None)


class Testimonial(models.Model):
    volunteer = ForeignKey(VolunteerProfile)
    offer = ForeignKey(Offer)

    body = TextField()

    is_public = BooleanField()

    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')
    created_by = ForeignKey(User, blank=True, default=None)
    published_at = DateTimeField(null=True, blank=True)
    depublished_at = DateTimeField(null=True, blank=True)


class OrgTestimonial(models.Model):
    organization = ForeignKey(Organization)
    offer = ForeignKey(Offer)

    body = TextField()

    is_public = BooleanField()

    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')
    created_by = ForeignKey(User, blank=True, default=None)
    published_at = DateTimeField(null=True, blank=True)
    depublished_at = DateTimeField(null=True, blank=True)


class AgreementTemplate(models.Model):
    is_general = BooleanField()
    organization = ForeignKey(Organization, blank=True, null=True)
    offer = ForeignKey(Offer, blank=True, null=True, unique=True)

    body = TextField()

    def __unicode__(self):
        content_type = ContentType.objects.get_for_model(AgreementTemplate)
        try:
            version = Version.objects.filter(content_type=content_type, object_id=self.id).order_by('-revision')[0]
            return u"Version id={}".format(version.id)
        except IndexError:
            return u"Version id=0"

    class Meta:
        unique_together = (('organization', 'offer'),)


class AgreementTask(models.Model):
    offer = ForeignKey(Offer)
    volunteer = ForeignKey(VolunteerProfile, blank=True, null=True)

    body = TextField()

    class Meta:
        unique_together = (('volunteer', 'offer'),)


class Agreement(models.Model):
    volunteer = ForeignKey(VolunteerProfile)
    offer = ForeignKey(Offer)

    template = ForeignKey(AgreementTemplate)
    not_signed_resource = CharField(max_length=255)
    volunteer_signed_resource = ThumbnailerImageField(upload_to='temp', blank=True, null=True)
    organization_signed_resource = ThumbnailerImageField(upload_to='temp', blank=True, null=True)

    status = IntegerField(choices=AgreementStateFactory.available_statuses, blank=True, default=0)
    created_at = DateTimeField()

    class Meta:
        unique_together = (('volunteer', 'offer'),)


class CertificateTemplate(models.Model):
    is_general = BooleanField()
    organization = ForeignKey(Organization, blank=True, null=True)
    offer = ForeignKey(Offer, blank=True, null=True, unique=True)

    body = TextField()

    def __unicode__(self):
        content_type = ContentType.objects.get_for_model(AgreementTemplate)
        try:
            version = Version.objects.filter(content_type=content_type, object_id=self.id).order_by('-revision')[0]
            return u"Version id={}".format(version.id)
        except IndexError:
            return u"Version id=0"

    class Meta:
        unique_together = (('organization', 'offer'),)


class Certificate(models.Model):
    volunteer = ForeignKey(VolunteerProfile)
    offer = ForeignKey(Offer)

    template = ForeignKey(CertificateTemplate)
    not_signed_resource = CharField(max_length=255)
    volunteer_signed_resource = ThumbnailerImageField(upload_to='temp', blank=True, null=True)
    organization_signed_resource = ThumbnailerImageField(upload_to='temp', blank=True, null=True)

    status = IntegerField(choices=CertificateStateFactory.available_statuses, blank=True, default=0)
    created_at = DateTimeField()

    class Meta:
        unique_together = (('volunteer', 'offer'),)


class LargeOfferThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='large-offer-thumbnails', resize_source={
        'size': (350, 218),
        'crop': "0,0"
    })
    description = CharField(max_length=255, blank=True, default='')
    offer = OneToOneField(Offer, blank=True, null=True, related_name="large_thumbnail_relation")

    def __unicode__(self):
        return self.filename


class PromotedOfferThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='promoted-offer-thumbnails', resize_source={
        'size': (250, 156),
        'crop': "0,0"
    })
    description = CharField(max_length=255, blank=True, default='')
    offer = OneToOneField(Offer, blank=True, null=True, related_name="promoted_thumbnail_relation")

    def __unicode__(self):
        return self.filename


class SmallOfferThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='small-offer-thumbnails', resize_source={
        'size': (155, 96),
        'crop': "0,0"
    })
    description = CharField(max_length=255, blank=True, default='')
    offer = OneToOneField(Offer, blank=True, null=True, related_name="small_thumbnail_relation")

    def __unicode__(self):
        return self.filename


class OriginalOfferThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='original-images')
    description = CharField(max_length=255, blank=True, default='')
    offer = OneToOneField(Offer, blank=True, null=True, related_name="original_thumbnail_relation")

    def __unicode__(self):
        return self.filename


class Application(models.Model):
    volunteer = ForeignKey(VolunteerProfile, related_name='volunteer_application_set')
    offer = ForeignKey(Offer, related_name='offer_application_set')
    status = IntegerField(choices=ApplicationStateFactory.available_statuses, blank=True, default=0)
    message = TextField(blank=True, null=True, default="")

    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')
    last_modified_at = DateTimeField(blank=True, null=True, default='')

    def __unicode__(self):
        return u"{} - {}".format(self.offer.title, self.volunteer.user.username)

    class Meta:
        unique_together = (('volunteer', 'offer'),)
        permissions = (
            ('accept_application', "Can accept/reject application"),
        )


class UserProfile(models.Model):
    user = OneToOneField(User)
    organization_member = ForeignKey(Organization, blank=True, null=True, related_name='member_set')

    def __unicode__(self):
        return self.user.username

    class Meta:
        permissions = (
            ('read_metrics', "Can read metrics"),
        )


class News(models.Model):
    title = CharField(max_length=255)
    body = TextField()

    created_at = DateTimeField(auto_now_add=True, blank=datetime.datetime.now(), null=True, default='')
    created_by = ForeignKey(User, blank=True, default=None, related_name="news_created")

    last_modified_at = DateTimeField(blank=True, null=True, default='')
    last_modified_by = ForeignKey(User, blank=True, null=True, related_name='news_modified')

    def __unicode__(self):
        return self.title

    class Meta:
        permissions = (
            ('create_news', "Can create news"),
            ('edit_news', "Can edit news"),
        )

class NewsThumbnail(models.Model):
    filename = ThumbnailerImageField(upload_to='news-thumbnails', resize_source={
        'size': (256, 256),
        'crop': "0,0"
    })
    description = CharField(max_length=255, blank=True, default='')
    news = OneToOneField(News, blank=True, null=True, related_name="news_thumbnail")

    def __unicode__(self):
        return self.filename
