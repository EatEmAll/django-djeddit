# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from djeddit.urls import urlpatterns as djeddit_urls

urlpatterns = [
    url(r'^', include(djeddit_urls, namespace='djeddit')),
]
