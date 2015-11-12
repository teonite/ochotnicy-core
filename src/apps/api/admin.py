# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from django.contrib import admin

from . import models
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from registration_api import models as registration_models
import reversion


class ShowAllFieldsAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [f.name for f in self.model._meta.fields]


class OrganizationResource(resources.ModelResource):
    class Meta:
        model = models.Organization


class OrganizationAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = OrganizationResource
    pass

admin.site.register(models.Organization, OrganizationAdmin)


class OrganizationTypeResource(resources.ModelResource):
    class Meta:
        model = models.OrganizationType


class OrganizationTypeAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = OrganizationTypeResource
    pass

admin.site.register(models.OrganizationType, OrganizationTypeAdmin)
admin.site.register(models.OrganizationThumbnail, ShowAllFieldsAdmin)


class UserProfileResource(resources.ModelResource):
    class Meta:
        model = models.UserProfile


class UserProfileAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = UserProfileResource
    pass

admin.site.register(models.UserProfile, UserProfileAdmin)


class VolunteerProfileResource(resources.ModelResource):
    class Meta:
        model = models.VolunteerProfile


class VolunteerProfileAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = VolunteerProfileResource
    pass

admin.site.register(models.VolunteerProfile, VolunteerProfileAdmin)


class EducationResource(resources.ModelResource):
    class Meta:
        model = models.Education


class EducationAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = EducationResource
    pass

admin.site.register(models.Education, EducationAdmin)


class ApplicationResource(resources.ModelResource):
    class Meta:
        model = models.Application


class ApplicationAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = ApplicationResource
    pass

admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.LargeOfferThumbnail, ShowAllFieldsAdmin)
admin.site.register(models.SmallOfferThumbnail, ShowAllFieldsAdmin)


class CategoryResource(resources.ModelResource):
    class Meta:
        model = models.Category


class CategoryAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = CategoryResource
    pass

admin.site.register(models.Category, CategoryAdmin)


class OfferResource(resources.ModelResource):
    class Meta:
        model = models.Offer


class OfferAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = OfferResource
    pass

admin.site.register(models.Offer, OfferAdmin)


class AgreementTemplateResource(resources.ModelResource):
    class Meta:
        model = models.AgreementTemplate


class AgreementTemplateAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = AgreementTemplateResource
    pass

admin.site.register(models.AgreementTemplate, AgreementTemplateAdmin)


class AgreementResource(resources.ModelResource):
    class Meta:
        model = models.Agreement


class AgreementAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = AgreementResource
    pass

admin.site.register(models.Agreement, AgreementAdmin)


class CertificateTemplateResource(resources.ModelResource):
    class Meta:
        model = models.CertificateTemplate


class CertificateTemplateAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = CertificateTemplateResource
    pass

admin.site.register(models.CertificateTemplate, CertificateTemplateAdmin)


class CertificateResource(resources.ModelResource):
    class Meta:
        model = models.Certificate


class CertificateAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = CertificateResource
    pass

admin.site.register(models.Certificate, CertificateAdmin)


class AbilityResource(resources.ModelResource):
    class Meta:
        model = models.Ability


class AbilityAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = AbilityResource
    pass

admin.site.register(models.Ability, AbilityAdmin)


class OrgAbilityResource(resources.ModelResource):
    class Meta:
        model = models.OrgAbility


class OrgAbilityAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = OrgAbilityResource
    pass

admin.site.register(models.OrgAbility, OrgAbilityAdmin)


class AgreementTaskResource(resources.ModelResource):
    class Meta:
        model = models.AgreementTask


class AgreementTaskAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = AgreementTaskResource
    pass

admin.site.register(models.AgreementTask, AgreementTaskAdmin)


class NewsResource(resources.ModelResource):
    class Meta:
        model = models.News


class NewsAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = NewsResource
    pass

admin.site.register(models.News, NewsAdmin)


class NewsThumbnailResource(resources.ModelResource):
    class Meta:
        model = models.NewsThumbnail


class NewsThumbnailAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = NewsThumbnailResource
    pass

admin.site.register(models.NewsThumbnail, NewsThumbnailAdmin)


class RatingResource(resources.ModelResource):
    class Meta:
        model = models.Rating


class RatingAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = RatingResource
    pass

admin.site.register(models.Rating, RatingAdmin)


class OrgRatingResource(resources.ModelResource):
    class Meta:
        model = models.OrgRating


class OrgRatingAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = OrgRatingResource
    pass

admin.site.register(models.OrgRating, OrgRatingAdmin)


class OrganizationSignatoryResource(resources.ModelResource):
    class Meta:
        model = models.OrganizationSignatory


class OrganizationSignatoryAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = OrganizationSignatoryResource
    pass

admin.site.register(models.OrganizationSignatory, OrganizationSignatoryAdmin)


class RegistrationProfileResource(resources.ModelResource):
    class Meta:
        model = registration_models.RegistrationProfile


class RegistrationProfileAdmin(reversion.VersionAdmin, ImportExportModelAdmin, ImportExportActionModelAdmin, ShowAllFieldsAdmin):
    resource_class = RegistrationProfileResource
    pass

admin.site.register(registration_models.RegistrationProfile, RegistrationProfileAdmin)
admin.site.register(models.Settings, ShowAllFieldsAdmin)


