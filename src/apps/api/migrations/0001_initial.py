# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Settings'
        db.create_table(u'api_settings', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('settings', self.gf(u'django_hstore.fields.DictionaryField')()),
        ))
        db.send_create_signal(u'api', ['Settings'])

        # Adding model 'OrganizationType'
        db.create_table(u'api_organizationtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('is_krs_required', self.gf('django.db.models.fields.BooleanField')()),
            ('is_nip_required', self.gf('django.db.models.fields.BooleanField')()),
        ))
        db.send_create_signal(u'api', ['OrganizationType'])

        # Adding model 'Organization'
        db.create_table(u'api_organization', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.OrganizationType'])),
            ('coordinator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('fullname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('nip', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
            ('krs', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
            ('phonenumber', self.gf('django.db.models.fields.CharField')(default='', max_length=40, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('house_number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('apartment_number', self.gf('django.db.models.fields.CharField')(default='', max_length=10, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('district', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('province', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('country', self.gf('django_countries.fields.CountryField')(max_length=2)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', max_length=350, null=True, blank=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'api', ['Organization'])

        # Adding model 'OrganizationSignatory'
        db.create_table(u'api_organizationsignatory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Organization'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('position', self.gf('django.db.models.fields.CharField')(default='', max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['OrganizationSignatory'])

        # Adding model 'OrganizationThumbnail'
        db.create_table(u'api_organizationthumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='thumbnail_relation', unique=True, null=True, to=orm['api.Organization'])),
        ))
        db.send_create_signal(u'api', ['OrganizationThumbnail'])

        # Adding model 'OriginalOrganizationThumbnail'
        db.create_table(u'api_originalorganizationthumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='original_thumbnail_relation', unique=True, null=True, to=orm['api.Organization'])),
        ))
        db.send_create_signal(u'api', ['OriginalOrganizationThumbnail'])

        # Adding model 'Education'
        db.create_table(u'api_education', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'api', ['Education'])

        # Adding model 'Ability'
        db.create_table(u'api_ability', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'api', ['Ability'])

        # Adding model 'OrgAbility'
        db.create_table(u'api_orgability', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'api', ['OrgAbility'])

        # Adding model 'Category'
        db.create_table(u'api_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'api', ['Category'])

        # Adding model 'CeleryTask'
        db.create_table(u'api_celerytask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('performed_at', self.gf('django.db.models.fields.DateTimeField')()),
            ('duration', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'api', ['CeleryTask'])

        # Adding model 'CategorySubscription'
        db.create_table(u'api_categorysubscription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Category'])),
        ))
        db.send_create_signal(u'api', ['CategorySubscription'])

        # Adding unique constraint on 'CategorySubscription', fields ['user', 'category']
        db.create_unique(u'api_categorysubscription', ['user_id', 'category_id'])

        # Adding model 'VolunteerProfile'
        db.create_table(u'api_volunteerprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')()),
            ('gender', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('phonenumber', self.gf('django.db.models.fields.CharField')(default='', max_length=40, null=True, blank=True)),
            ('pesel', self.gf('django.db.models.fields.CharField')(default='', max_length=11, null=True, blank=True)),
            # ('proof_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('proof_number', self.gf('django.db.models.fields.CharField')(default='', max_length=20, null=True, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('house_number', self.gf('django.db.models.fields.CharField')(default='', max_length=10, null=True, blank=True)),
            ('apartment_number', self.gf('django.db.models.fields.CharField')(default='', max_length=10, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(default='', max_length=20, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('country', self.gf('django_countries.fields.CountryField')(default=None, max_length=2, null=True, blank=True)),
            ('about', self.gf('django.db.models.fields.TextField')()),
            ('education', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Education'])),
            ('abilities_description', self.gf('django.db.models.fields.TextField')(default='', max_length=500, null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['VolunteerProfile'])

        # Adding M2M table for field abilities on 'VolunteerProfile'
        m2m_table_name = db.shorten_name(u'api_volunteerprofile_abilities')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('volunteerprofile', models.ForeignKey(orm[u'api.volunteerprofile'], null=False)),
            ('ability', models.ForeignKey(orm[u'api.ability'], null=False))
        ))
        db.create_unique(m2m_table_name, ['volunteerprofile_id', 'ability_id'])

        # Adding model 'VolunteerProfileThumbnail'
        db.create_table(u'api_volunteerprofilethumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('volunteer', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='thumbnail_relation', unique=True, null=True, to=orm['api.VolunteerProfile'])),
        ))
        db.send_create_signal(u'api', ['VolunteerProfileThumbnail'])

        # Adding model 'OriginalVolunteerProfileThumbnail'
        db.create_table(u'api_originalvolunteerprofilethumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('volunteer', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='original_thumbnail_relation', unique=True, null=True, to=orm['api.VolunteerProfile'])),
        ))
        db.send_create_signal(u'api', ['OriginalVolunteerProfileThumbnail'])

        # Adding model 'ResourceMetadata'
        db.create_table(u'api_resourcemetadata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default='', auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='created_set', blank=True, to=orm['auth.User'])),
            ('last_modified_at', self.gf('django.db.models.fields.DateTimeField')(default='', auto_now=True, null=True, blank=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='last_modified_set', blank=True, to=orm['auth.User'])),
        ))
        db.send_create_signal(u'api', ['ResourceMetadata'])

        # Adding model 'Offer'
        db.create_table(u'api_offer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=200, null=True, blank=True)),
            ('publishing_organization', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='publishing_organization_set', null=True, to=orm['api.Organization'])),
            ('publish_from', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 3, 13, 0, 0), null=True, blank=True)),
            ('publish_to', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2015, 3, 13, 0, 0), null=True, blank=True)),
            ('published_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='publisher_set', null=True, to=orm['auth.User'])),
            ('published_at', self.gf('django.db.models.fields.DateTimeField')(default='', null=True, blank=True)),
            ('depublished_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='depublisher_set', null=True, to=orm['auth.User'])),
            ('depublished_at', self.gf('django.db.models.fields.DateTimeField')(default='', null=True, blank=True)),
            ('volunteer_max_count', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('is_promoted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('localization', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', max_length=1000, null=True, blank=True)),
            ('description_time', self.gf('django.db.models.fields.TextField')(default='', max_length=200, null=True, blank=True)),
            ('description_problem', self.gf('django.db.models.fields.TextField')(default='', max_length=500, null=True, blank=True)),
            ('description_requirements', self.gf('django.db.models.fields.TextField')(default='', max_length=600, null=True, blank=True)),
            ('description_quests', self.gf('django.db.models.fields.TextField')(default='', max_length=1000, null=True, blank=True)),
            ('description_benefits', self.gf('django.db.models.fields.TextField')(default='', max_length=800, null=True, blank=True)),
            ('description_additional_requirements', self.gf('django.db.models.fields.TextField')(default='', max_length=600, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            # ('status_change_reason', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('agreement_stands_from', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('agreement_stands_to', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('step_1', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='first_step_set', null=True, to=orm['api.ResourceMetadata'])),
            ('step_2', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='second_step_set', null=True, to=orm['api.ResourceMetadata'])),
            ('views_count_volunteers', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('views_count_guests', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal(u'api', ['Offer'])

        # Adding M2M table for field category on 'Offer'
        m2m_table_name = db.shorten_name(u'api_offer_category')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('offer', models.ForeignKey(orm[u'api.offer'], null=False)),
            ('category', models.ForeignKey(orm[u'api.category'], null=False))
        ))
        db.create_unique(m2m_table_name, ['offer_id', 'category_id'])

        # Adding M2M table for field agreement_signatories on 'Offer'
        m2m_table_name = db.shorten_name(u'api_offer_agreement_signatories')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('offer', models.ForeignKey(orm[u'api.offer'], null=False)),
            ('organizationsignatory', models.ForeignKey(orm[u'api.organizationsignatory'], null=False))
        ))
        db.create_unique(m2m_table_name, ['offer_id', 'organizationsignatory_id'])

        # Adding model 'Review'
        db.create_table(u'api_review', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Organization'])),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Offer'])),
        ))
        db.send_create_signal(u'api', ['Review'])

        # Adding model 'Rating'
        db.create_table(u'api_rating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.VolunteerProfile'])),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offer_rating_set', to=orm['api.Offer'])),
            ('ability', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Ability'])),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default='', auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], blank=True)),
        ))
        db.send_create_signal(u'api', ['Rating'])

        # Adding unique constraint on 'Rating', fields ['volunteer', 'offer', 'ability']
        db.create_unique(u'api_rating', ['volunteer_id', 'offer_id', 'ability_id'])

        # Adding model 'OrgRating'
        db.create_table(u'api_orgrating', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Organization'])),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offer_orgrating_set', to=orm['api.Offer'])),
            ('ability', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.OrgAbility'])),
            ('rating', self.gf('django.db.models.fields.IntegerField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default='', auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], blank=True)),
        ))
        db.send_create_signal(u'api', ['OrgRating'])

        # Adding model 'Testimonial'
        db.create_table(u'api_testimonial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.VolunteerProfile'])),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Offer'])),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('is_public', self.gf('django.db.models.fields.BooleanField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default='', auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], blank=True)),
            ('published_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('depublished_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['Testimonial'])

        # Adding model 'OrgTestimonial'
        db.create_table(u'api_orgtestimonial', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Organization'])),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Offer'])),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('is_public', self.gf('django.db.models.fields.BooleanField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default='', auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['auth.User'], blank=True)),
            ('published_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('depublished_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['OrgTestimonial'])

        # Adding model 'AgreementTemplate'
        db.create_table(u'api_agreementtemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_general', self.gf('django.db.models.fields.BooleanField')()),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Organization'], null=True, blank=True)),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Offer'], unique=True, null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'api', ['AgreementTemplate'])

        # Adding unique constraint on 'AgreementTemplate', fields ['organization', 'offer']
        db.create_unique(u'api_agreementtemplate', ['organization_id', 'offer_id'])

        # Adding model 'AgreementTask'
        db.create_table(u'api_agreementtask', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Offer'])),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.VolunteerProfile'], null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'api', ['AgreementTask'])

        # Adding unique constraint on 'AgreementTask', fields ['volunteer', 'offer']
        db.create_unique(u'api_agreementtask', ['volunteer_id', 'offer_id'])

        # Adding model 'Agreement'
        db.create_table(u'api_agreement', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.VolunteerProfile'])),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Offer'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.AgreementTemplate'])),
            ('not_signed_resource', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('volunteer_signed_resource', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('organization_signed_resource', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'api', ['Agreement'])

        # Adding unique constraint on 'Agreement', fields ['volunteer', 'offer']
        db.create_unique(u'api_agreement', ['volunteer_id', 'offer_id'])

        # Adding model 'CertificateTemplate'
        db.create_table(u'api_certificatetemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_general', self.gf('django.db.models.fields.BooleanField')()),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Organization'], null=True, blank=True)),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Offer'], unique=True, null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'api', ['CertificateTemplate'])

        # Adding unique constraint on 'CertificateTemplate', fields ['organization', 'offer']
        db.create_unique(u'api_certificatetemplate', ['organization_id', 'offer_id'])

        # Adding model 'Certificate'
        db.create_table(u'api_certificate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.VolunteerProfile'])),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.Offer'])),
            ('template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.CertificateTemplate'])),
            ('not_signed_resource', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('volunteer_signed_resource', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('organization_signed_resource', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'api', ['Certificate'])

        # Adding unique constraint on 'Certificate', fields ['volunteer', 'offer']
        db.create_unique(u'api_certificate', ['volunteer_id', 'offer_id'])

        # Adding model 'LargeOfferThumbnail'
        db.create_table(u'api_largeofferthumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('offer', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='large_thumbnail_relation', unique=True, null=True, to=orm['api.Offer'])),
        ))
        db.send_create_signal(u'api', ['LargeOfferThumbnail'])

        # Adding model 'PromotedOfferThumbnail'
        db.create_table(u'api_promotedofferthumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('offer', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='promoted_thumbnail_relation', unique=True, null=True, to=orm['api.Offer'])),
        ))
        db.send_create_signal(u'api', ['PromotedOfferThumbnail'])

        # Adding model 'SmallOfferThumbnail'
        db.create_table(u'api_smallofferthumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('offer', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='small_thumbnail_relation', unique=True, null=True, to=orm['api.Offer'])),
        ))
        db.send_create_signal(u'api', ['SmallOfferThumbnail'])

        # Adding model 'OriginalOfferThumbnail'
        db.create_table(u'api_originalofferthumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('offer', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='original_thumbnail_relation', unique=True, null=True, to=orm['api.Offer'])),
        ))
        db.send_create_signal(u'api', ['OriginalOfferThumbnail'])

        # Adding model 'Application'
        db.create_table(u'api_application', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('volunteer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='volunteer_application_set', to=orm['api.VolunteerProfile'])),
            ('offer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='offer_application_set', to=orm['api.Offer'])),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('message', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default='', auto_now_add=True, null=True, blank=True)),
            ('last_modified_at', self.gf('django.db.models.fields.DateTimeField')(default='', null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['Application'])

        # Adding unique constraint on 'Application', fields ['volunteer', 'offer']
        db.create_unique(u'api_application', ['volunteer_id', 'offer_id'])

        # Adding model 'UserProfile'
        db.create_table(u'api_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('organization_member', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='member_set', null=True, to=orm['api.Organization'])),
        ))
        db.send_create_signal(u'api', ['UserProfile'])

        # Adding model 'News'
        db.create_table(u'api_news', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default='', auto_now_add=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='news_created', blank=True, to=orm['auth.User'])),
            ('last_modified_at', self.gf('django.db.models.fields.DateTimeField')(default='', null=True, blank=True)),
            ('last_modified_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='news_modified', null=True, to=orm['auth.User'])),
        ))
        db.send_create_signal(u'api', ['News'])

        # Adding model 'NewsThumbnail'
        db.create_table(u'api_newsthumbnail', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('filename', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('news', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='news_thumbnail', unique=True, null=True, to=orm['api.News'])),
        ))
        db.send_create_signal(u'api', ['NewsThumbnail'])


    def backwards(self, orm):
        # Removing unique constraint on 'Application', fields ['volunteer', 'offer']
        db.delete_unique(u'api_application', ['volunteer_id', 'offer_id'])

        # Removing unique constraint on 'Certificate', fields ['volunteer', 'offer']
        db.delete_unique(u'api_certificate', ['volunteer_id', 'offer_id'])

        # Removing unique constraint on 'CertificateTemplate', fields ['organization', 'offer']
        db.delete_unique(u'api_certificatetemplate', ['organization_id', 'offer_id'])

        # Removing unique constraint on 'Agreement', fields ['volunteer', 'offer']
        db.delete_unique(u'api_agreement', ['volunteer_id', 'offer_id'])

        # Removing unique constraint on 'AgreementTask', fields ['volunteer', 'offer']
        db.delete_unique(u'api_agreementtask', ['volunteer_id', 'offer_id'])

        # Removing unique constraint on 'AgreementTemplate', fields ['organization', 'offer']
        db.delete_unique(u'api_agreementtemplate', ['organization_id', 'offer_id'])

        # Removing unique constraint on 'Rating', fields ['volunteer', 'offer', 'ability']
        db.delete_unique(u'api_rating', ['volunteer_id', 'offer_id', 'ability_id'])

        # Removing unique constraint on 'CategorySubscription', fields ['user', 'category']
        db.delete_unique(u'api_categorysubscription', ['user_id', 'category_id'])

        # Deleting model 'Settings'
        db.delete_table(u'api_settings')

        # Deleting model 'OrganizationType'
        db.delete_table(u'api_organizationtype')

        # Deleting model 'Organization'
        db.delete_table(u'api_organization')

        # Deleting model 'OrganizationSignatory'
        db.delete_table(u'api_organizationsignatory')

        # Deleting model 'OrganizationThumbnail'
        db.delete_table(u'api_organizationthumbnail')

        # Deleting model 'OriginalOrganizationThumbnail'
        db.delete_table(u'api_originalorganizationthumbnail')

        # Deleting model 'Education'
        db.delete_table(u'api_education')

        # Deleting model 'Ability'
        db.delete_table(u'api_ability')

        # Deleting model 'OrgAbility'
        db.delete_table(u'api_orgability')

        # Deleting model 'Category'
        db.delete_table(u'api_category')

        # Deleting model 'CeleryTask'
        db.delete_table(u'api_celerytask')

        # Deleting model 'CategorySubscription'
        db.delete_table(u'api_categorysubscription')

        # Deleting model 'VolunteerProfile'
        db.delete_table(u'api_volunteerprofile')

        # Removing M2M table for field abilities on 'VolunteerProfile'
        db.delete_table(db.shorten_name(u'api_volunteerprofile_abilities'))

        # Deleting model 'VolunteerProfileThumbnail'
        db.delete_table(u'api_volunteerprofilethumbnail')

        # Deleting model 'OriginalVolunteerProfileThumbnail'
        db.delete_table(u'api_originalvolunteerprofilethumbnail')

        # Deleting model 'ResourceMetadata'
        db.delete_table(u'api_resourcemetadata')

        # Deleting model 'Offer'
        db.delete_table(u'api_offer')

        # Removing M2M table for field category on 'Offer'
        db.delete_table(db.shorten_name(u'api_offer_category'))

        # Removing M2M table for field agreement_signatories on 'Offer'
        db.delete_table(db.shorten_name(u'api_offer_agreement_signatories'))

        # Deleting model 'Review'
        db.delete_table(u'api_review')

        # Deleting model 'Rating'
        db.delete_table(u'api_rating')

        # Deleting model 'OrgRating'
        db.delete_table(u'api_orgrating')

        # Deleting model 'Testimonial'
        db.delete_table(u'api_testimonial')

        # Deleting model 'OrgTestimonial'
        db.delete_table(u'api_orgtestimonial')

        # Deleting model 'AgreementTemplate'
        db.delete_table(u'api_agreementtemplate')

        # Deleting model 'AgreementTask'
        db.delete_table(u'api_agreementtask')

        # Deleting model 'Agreement'
        db.delete_table(u'api_agreement')

        # Deleting model 'CertificateTemplate'
        db.delete_table(u'api_certificatetemplate')

        # Deleting model 'Certificate'
        db.delete_table(u'api_certificate')

        # Deleting model 'LargeOfferThumbnail'
        db.delete_table(u'api_largeofferthumbnail')

        # Deleting model 'PromotedOfferThumbnail'
        db.delete_table(u'api_promotedofferthumbnail')

        # Deleting model 'SmallOfferThumbnail'
        db.delete_table(u'api_smallofferthumbnail')

        # Deleting model 'OriginalOfferThumbnail'
        db.delete_table(u'api_originalofferthumbnail')

        # Deleting model 'Application'
        db.delete_table(u'api_application')

        # Deleting model 'UserProfile'
        db.delete_table(u'api_userprofile')

        # Deleting model 'News'
        db.delete_table(u'api_news')

        # Deleting model 'NewsThumbnail'
        db.delete_table(u'api_newsthumbnail')


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
            'publish_from': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 3, 13, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'publish_to': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 3, 13, 0, 0)', 'null': 'True', 'blank': 'True'}),
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
            'education': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.Education']"}),
            'gender': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'house_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pesel': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '11', 'null': 'True', 'blank': 'True'}),
            'phonenumber': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'proof_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            # 'proof_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
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