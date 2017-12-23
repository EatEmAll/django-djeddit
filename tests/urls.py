# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from djeddit.urls import urlpatterns as djeddit_urls

from django.contrib.sitemaps.views import sitemap
from djeddit.sitemaps import ThreadSitemap

sitemaps = {
    'djeddit' : ThreadSitemap
}

urlpatterns = [
    url(r'^', include(djeddit_urls)),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
