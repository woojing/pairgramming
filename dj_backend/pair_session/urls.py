# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from .views import index

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dj_backend.views.home', name='home'),
    # url(r'^dj_backend/', include('dj_backend.foo.urls')),

    url(r'^$', index),
)