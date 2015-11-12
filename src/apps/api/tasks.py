# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from __future__ import absolute_import
import datetime
from app_metrics.utils import create_metric, create_metric_set, gauge
from apps.api.application_states import ApplicationStateFactory
from celery.task import task
from django.db.models import Q, Count, F
from notification import notify

from .models import Offer, CategorySubscription, CeleryTask, Settings, Organization, VolunteerProfile, Rating, \
    Application, OrgRating
from .helpers import Benchmark, instance_url
from .offer_states import OfferStateFactory


@task()
def metrics(*args):
    orgs_count = create_metric(name="Organizations count", slug='orgs_count')
    orgs_from_last_week = create_metric(name="Organization from last week", slug='orgs_from_last_week')
    orgs_with_offer = create_metric(name='Organizations with offers', slug='orgs_with_offers')
    orgs_without_offer = create_metric(name='Organizations without offers', slug='orgs_without_offers')
    volunteers_with_applications = create_metric(name='Volunteers with applications', slug='volunteers_with_apps')
    volunteers_without_applications = create_metric(name='Volunteers without applications', slug='volunteers_without_apps')
    volunteers_count = create_metric(name='Volunteers count', slug='volunteers_count')
    volunteers_from_last_week = create_metric(name='Volunteers from last week', slug='volunteers_from_last_week')
    offers_count = create_metric(name='Offers count', slug='offers_count')
    offers_with_ratings = create_metric(name='Offers with ratings', slug='offers_with_ratings')
    offers_without_ratings = create_metric(name='Offers without ratings', slug='offers_without_ratings')
    offers_from_last_week = create_metric(name='Offers from last week', slug='offers_from_last_week')
    offers_with_one_org_rating = create_metric(name='Offers with >0 ratings from volunteers', slug='offer_with_one_org_rating')
    offers_with_one_vol_rating = create_metric(name='Offers with >0 ratings from organizations', slug='offer_with_one_vol_rating')
    offers_with_all_org_rating = create_metric(name='Offers with all ratings from volunteers', slug='offer_with_all_org_rating')
    offers_with_all_vol_rating = create_metric(name='Offers with all ratings from organizations', slug='offer_with_all_vol_rating')
    offers_not_ended = create_metric(name='Offers not ended', slug='offer_not_ended')
    offers_ended = create_metric(name='Offers ended', slug='offer_ended')

    my_metric_set = create_metric_set(name='Default', metrics=[orgs_with_offer], email_recipients=[])

    gauge('orgs_count', Organization.objects.all().count())
    gauge('orgs_from_last_week', Organization.objects.filter(
        created_at__gt=datetime.datetime.now() - datetime.timedelta(days=7)).count())
    gauge('orgs_with_offers', Organization.objects.annotate(num_offers=Count('publishing_organization_set')).filter(
        num_offers__gt=0
    ).count())
    gauge('orgs_without_offers', Organization.objects.annotate(num_offers=Count('publishing_organization_set')).filter(
        num_offers=0
    ).count())
    gauge('volunteers_with_apps', VolunteerProfile.objects.annotate(num_apps=Count('volunteer_application_set')).filter(
        num_apps__gt=0
    ).count())
    gauge('volunteers_without_apps', VolunteerProfile.objects.annotate(num_apps=Count('volunteer_application_set')).filter(
        num_apps=0
    ).count())
    gauge('volunteers_count', VolunteerProfile.objects.all().count())
    gauge('volunteers_from_last_week', VolunteerProfile.objects.filter(
        created_at__gt=datetime.datetime.now() - datetime.timedelta(days=7)).count())
    gauge('offers_count', Offer.objects.all().count())
    gauge('offers_from_last_week', Offer.objects.filter(
        step_2__created_at__gt=datetime.datetime.now() - datetime.timedelta(days=7)).count())
    gauge('offers_with_ratings', Offer.objects.annotate(
        num_ratings=Count('offer_rating_set'),
        num_orgratings=Count('offer_orgrating_set')
    ).filter(
        Q(num_ratings__gt=0) | Q(num_orgratings__gt=0)
    ).count())
    gauge('offers_without_ratings', Offer.objects.annotate(
        num_ratings=Count('offer_rating_set'),
        num_orgratings=Count('offer_orgrating_set')
    ).filter(
        num_ratings=0, num_orgratings=0
    ).count())
    gauge('offer_with_one_org_rating', Offer.objects.annotate(
        num_orgratings=Count('offer_orgrating_set')
    ).filter(
        num_orgratings__gt=0
    ).count())
    gauge('offer_with_one_vol_rating', Offer.objects.annotate(
        num_ratings=Count('offer_rating_set')
    ).filter(
        num_ratings__gt=0
    ).count())
    gauge('offers_ended', Offer.objects.filter(status=OfferStateFactory.PUBLISHED, publish_to__lt=datetime.datetime.now()).count())
    gauge('offers_not_ended', Offer.objects.filter(status=OfferStateFactory.PUBLISHED, publish_to__gt=datetime.datetime.now()).count())

    offer_with_all_vol_rating_count = 0
    for offer in Offer.objects.all():
        num_volunteers = Application.objects.filter(offer=offer, status=ApplicationStateFactory.ACCEPTED).count()
        if num_volunteers == 0:
            continue
        num_ratings = Rating.objects.filter(offer=offer).values('volunteer').annotate(Count('ability')).count()
        num_volunteers = Application.objects.filter(offer=offer, status=ApplicationStateFactory.ACCEPTED).count()
        if num_ratings == num_volunteers:
            offer_with_all_vol_rating_count += 1
    gauge('offer_with_all_vol_rating', offer_with_all_vol_rating_count)

    offer_with_all_org_rating_count = 0
    for offer in Offer.objects.all():
        num_volunteers = Application.objects.filter(offer=offer, status=ApplicationStateFactory.ACCEPTED).count()
        if num_volunteers == 0:
            continue
        num_ratings = OrgRating.objects.filter(offer=offer).values('organization', 'created_by') \
            .annotate(Count('ability')).count()
        num_volunteers = Application.objects.filter(offer=offer, status=ApplicationStateFactory.ACCEPTED).count()
        #return "{} {} {}".format(str(offer.id), str(num_ratings), str(num_volunteers))
        if num_ratings == num_volunteers:
            offer_with_all_org_rating_count += 1
    gauge('offer_with_all_org_rating', offer_with_all_org_rating_count)

@task()
def notification(*args):
    benchmark = Benchmark.start()

    last_tasks = CeleryTask.objects.filter(slug='category-subscription')

    if len(last_tasks) > 0:
        last_task = last_tasks.latest('performed_at')

        days_interval, hour_treshold = get_settings()
        delta = get_time_delta(last_task)

        if days_interval > delta or datetime.datetime.now().hour < hour_treshold:
            return "OMIT: {}".format(delta)
    else:
        delta = 0

    subscribing_users = get_subscribing_users()
    notify_subscribing_users(subscribing_users)

    benchmark.stop()

    CeleryTask(slug='category-subscription', performed_at=benchmark.start, duration=benchmark.duration()).save()

    return "SUCCESS: {}, {}".format(delta, benchmark.start)


#private
def get_settings():
    setts = Settings.objects.filter(
        settings__contains=['category_subscription_interval', 'category_subscription_treshold']).first()
    days_interval = int(setts.settings['category_subscription_interval'])
    hour_treshold = int(setts.settings['category_subscription_treshold'])
    return days_interval, hour_treshold


#private
def get_time_delta(last_task):
    now = datetime.datetime.now()
    today = datetime.datetime(now.year, now.month, now.day)
    performed_at = last_task.performed_at
    performed_at_date = datetime.datetime(performed_at.year, performed_at.month, performed_at.day)
    delta = (today - performed_at_date).days
    return delta


#private
def get_subscribing_users():
    users = set()
    for e in CategorySubscription.objects.all().select_related('user'):
        users.add(e.user)
    return users


#private
def notify_subscribing_users(subscribing_users):
    for user in subscribing_users:
        subscriptions = get_subscriptions_for_user(user)

        data = {'categories': [], 'first_name': user.first_name, 'instance_url': instance_url()}
        for subscription in subscriptions:
            offers = get_offers_for_subscription(subscription)

            if len(offers) is 0:
                break

            data['categories'].append({
                'category': subscription.category.name,
                'offers': []
            })

            for offer in offers:
                data['categories'][-1]['offers'].append({
                    'title': offer.title,
                    'publish_to': offer.publish_to,
                    'id': offer.id
                })

        if len(data['categories']) is 0:
            break

        notify('category_subscription', data, subscription.user)


#private
def get_subscriptions_for_user(user):
    return CategorySubscription.objects.filter(user=user)


#private
def get_offers_for_subscription(subscription):
    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    offers = Offer.objects.filter(
        Q(status=OfferStateFactory.PUBLISHED) | Q(status=OfferStateFactory.PUBLISHED_EDITED),
        category=subscription.category.id, publish_from__gt=week_ago).order_by('-publish_from')
    return offers