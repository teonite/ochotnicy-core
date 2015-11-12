# -*- coding: utf-8 -*-

#
# Portal Ochotnicy - http://ochotnicy.pl
#
# Copyright (C) Pracownia badań i innowacji społecznych Stocznia
#
# Development: TEONITE - http://teonite.com
#

from rest_framework.routers import SimpleRouter, Route, DynamicListRoute, DynamicDetailRoute
from rest_framework_nested.routers import NestedSimpleRouter


class DocumentRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create_bulk'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/(?P<lookup_one>.+?)/(?P<lookup_one_value>.+?)/(?P<lookup_two>.+?)/(?P<lookup_two_value>.+?){trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'create',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]


class BulkRouter(SimpleRouter):
    routes = [

        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'put': 'update',
                'patch': 'partial_update',
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),

        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),

        Route(
            url=r'^{prefix}/(?P<lookup_one>.+?)/(?P<lookup_one_value>.+?)/(?P<lookup_two>.+?)/(?P<lookup_two_value>.+?){trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'create',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]


class AgreementTaskRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/(?P<lookup_one>.+?)/(?P<lookup_one_value>.+?)(/(?P<lookup_two>.+?)/(?P<lookup_two_value>.+?))?{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]


class DocumentTemplateRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'post': 'create',
                'put': 'update',
                'patch': 'partial_update',
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'^{prefix}/(?P<lookup_one>.+?)/(?P<lookup_one_value>.+?)/(?P<lookup_two>.+?)/(?P<lookup_two_value>.+?){trailing_slash}$',
            mapping={
                'get': 'retrieve'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]


class RatingRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create',
                'put': 'update',
                'patch': 'update',
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]


class ApplicationRouter(SimpleRouter):
    routes = [
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'post': 'create',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'put': 'update',
                'patch': 'partial_update',
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        Route(
            url=r'^{prefix}/(?P<lookup_one>.+?)/(?P<lookup_one_value>.+?)/(?P<lookup_two>.+?)/(?P<lookup_two_value>.+?){trailing_slash}$',
            mapping={
                'get': 'retrieve'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]