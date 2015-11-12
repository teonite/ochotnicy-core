# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'VolunteerProfile.proof_type'
        db.add_column(u'api_volunteerprofile', 'proof_type',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'VolunteerProfile.proof_type'
        db.delete_column(u'api_volunteerprofile', 'proof_type')


    models = {
        u'api.ability': {
            'Meta': {'object_name': 'Ability'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'api.agreement': {
            'Meta': {'unique_together': "(('volunteer', 'offer'),)", 'object_name': 'Agreement'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'not_signed_resource': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Offer']"}),
            'organization_signed_resource': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.AgreementTemplate']"}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.VolunteerProfile']"}),
            'volunteer_signed_resource': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'api.agreementtask': {
            'Meta': {'unique_together': "(('volunteer', 'offer'),)", 'object_name': 'AgreementTask'},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Offer']"}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.VolunteerProfile']", 'null': 'True', 'blank': 'True'})
        },
        u'api.agreementtemplate': {
            'Meta': {'unique_together': "(('organization', 'offer'),)", 'object_name': 'AgreementTemplate'},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_general': ('django.db.models.fields.BooleanField', [], {}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Offer']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Organization']", 'null': 'True', 'blank': 'True'})
        },
        u'api.application': {
            'Meta': {'unique_together': "(('volunteer', 'offer'),)", 'object_name': 'Application'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offer_application_set'", 'to': u"orm['api.Offer']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'volunteer_application_set'", 'to': u"orm['api.VolunteerProfile']"})
        },
        u'api.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'api.categorysubscription': {
            'Meta': {'unique_together': "(('user', 'category'),)", 'object_name': 'CategorySubscription'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'api.celerytask': {
            'Meta': {'object_name': 'CeleryTask'},
            'duration': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'performed_at': ('django.db.models.fields.DateTimeField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'api.certificate': {
            'Meta': {'unique_together': "(('volunteer', 'offer'),)", 'object_name': 'Certificate'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'not_signed_resource': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Offer']"}),
            'organization_signed_resource': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.CertificateTemplate']"}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.VolunteerProfile']"}),
            'volunteer_signed_resource': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'api.certificatetemplate': {
            'Meta': {'unique_together': "(('organization', 'offer'),)", 'object_name': 'CertificateTemplate'},
            'body': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_general': ('django.db.models.fields.BooleanField', [], {}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Offer']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Organization']", 'null': 'True', 'blank': 'True'})
        },
        u'api.education': {
            'Meta': {'object_name': 'Education'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'api.largeofferthumbnail': {
            'Meta': {'object_name': 'LargeOfferThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'large_thumbnail_relation'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.Offer']"})
        },
        u'api.news': {
            'Meta': {'object_name': 'News'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'news_created'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'news_modified'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'api.newsthumbnail': {
            'Meta': {'object_name': 'NewsThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'news': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'news_thumbnail'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.News']"})
        },
        u'api.offer': {
            'Meta': {'object_name': 'Offer'},
            'agreement_signatories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['api.OrganizationSignatory']", 'null': 'True', 'blank': 'True'}),
            'agreement_stands_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'agreement_stands_to': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['api.Category']", 'null': 'True', 'blank': 'True'}),
            'depublished_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'depublished_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'depublisher_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'description_additional_requirements': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '600', 'null': 'True', 'blank': 'True'}),
            'description_benefits': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'description_problem': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'description_quests': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'description_requirements': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '600', 'null': 'True', 'blank': 'True'}),
            'description_time': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_promoted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'localization': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'publish_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 3, 16, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'publish_to': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 3, 16, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'published_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'publisher_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'publishing_organization': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'publishing_organization_set'", 'null': 'True', 'to': u"orm['api.Organization']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            # 'status_change_reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'step_1': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'first_step_set'", 'null': 'True', 'to': u"orm['api.ResourceMetadata']"}),
            'step_2': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'second_step_set'", 'null': 'True', 'to': u"orm['api.ResourceMetadata']"}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'views_count_guests': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'views_count_volunteers': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'volunteer_max_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'api.orgability': {
            'Meta': {'object_name': 'OrgAbility'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'api.organization': {
            'Meta': {'object_name': 'Organization'},
            'apartment_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'coordinator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'country': ('django_countries.fields.CountryField', [], {'max_length': '2'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '350', 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'fullname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'house_number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'krs': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'nip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'phonenumber': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.OrganizationType']"}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'api.organizationsignatory': {
            'Meta': {'object_name': 'OrganizationSignatory'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Organization']"}),
            'position': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'api.organizationthumbnail': {
            'Meta': {'object_name': 'OrganizationThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'thumbnail_relation'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.Organization']"})
        },
        u'api.organizationtype': {
            'Meta': {'object_name': 'OrganizationType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_krs_required': ('django.db.models.fields.BooleanField', [], {}),
            'is_nip_required': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'api.orgrating': {
            'Meta': {'object_name': 'OrgRating'},
            'ability': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.OrgAbility']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offer_orgrating_set'", 'to': u"orm['api.Offer']"}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Organization']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {})
        },
        u'api.orgtestimonial': {
            'Meta': {'object_name': 'OrgTestimonial'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'blank': 'True'}),
            'depublished_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Offer']"}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Organization']"}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'api.originalofferthumbnail': {
            'Meta': {'object_name': 'OriginalOfferThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'original_thumbnail_relation'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.Offer']"})
        },
        u'api.originalorganizationthumbnail': {
            'Meta': {'object_name': 'OriginalOrganizationThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'original_thumbnail_relation'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.Organization']"})
        },
        u'api.originalvolunteerprofilethumbnail': {
            'Meta': {'object_name': 'OriginalVolunteerProfileThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'volunteer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'original_thumbnail_relation'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.VolunteerProfile']"})
        },
        u'api.promotedofferthumbnail': {
            'Meta': {'object_name': 'PromotedOfferThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'promoted_thumbnail_relation'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.Offer']"})
        },
        u'api.rating': {
            'Meta': {'unique_together': "(('volunteer', 'offer', 'ability'),)", 'object_name': 'Rating'},
            'ability': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Ability']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'offer_rating_set'", 'to': u"orm['api.Offer']"}),
            'rating': ('django.db.models.fields.IntegerField', [], {}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.VolunteerProfile']"})
        },
        u'api.resourcemetadata': {
            'Meta': {'object_name': 'ResourceMetadata'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'created_set'", 'blank': 'True', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'last_modified_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'last_modified_set'", 'blank': 'True', 'to': u"orm['auth.User']"})
        },
        u'api.review': {
            'Meta': {'object_name': 'Review'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Offer']"}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Organization']"})
        },
        u'api.settings': {
            'Meta': {'object_name': 'Settings'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'settings': (u'django_hstore.fields.DictionaryField', [], {})
        },
        u'api.smallofferthumbnail': {
            'Meta': {'object_name': 'SmallOfferThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'small_thumbnail_relation'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.Offer']"})
        },
        u'api.testimonial': {
            'Meta': {'object_name': 'Testimonial'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['auth.User']", 'blank': 'True'}),
            'depublished_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {}),
            'offer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Offer']"}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'volunteer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.VolunteerProfile']"})
        },
        u'api.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'organization_member': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'member_set'", 'null': 'True', 'to': u"orm['api.Organization']"}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'api.volunteerprofile': {
            'Meta': {'object_name': 'VolunteerProfile'},
            'abilities': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'volunteer_abilities_set'", 'symmetrical': 'False', 'to': u"orm['api.Ability']"}),
            'abilities_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'about': ('django.db.models.fields.TextField', [], {}),
            'apartment_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country': ('django_countries.fields.CountryField', [], {'default': 'None', 'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': "''", 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'education': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Education']"}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'house_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pesel': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'phonenumber': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'proof_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'proof_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'street': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'api.volunteerprofilethumbnail': {
            'Meta': {'object_name': 'VolunteerProfileThumbnail'},
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'filename': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'volunteer': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'thumbnail_relation'", 'unique': 'True', 'null': 'True', 'to': u"orm['api.VolunteerProfile']"})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['api']