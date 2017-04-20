# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.homePage, name='home'),
    url(r'^topics/?$', views.topicsPage, name='topics'),
    url(r'^topics/(\w+)?/?$', views.topicPage, name='topicPage'),
    url(r'^topics/(\w+)/newthread/?$', views.createThread, name='createThread'),
    url(r'^topics/(\w+)/(\d+)?/?$', views.threadPage, name='threadPage'),
    url(r'^reply_post/([\w\-]{36})?/?$', views.replyPost, name='replyPost'),
    url(r'^edit_post/([\w\-]{36})?/?$', views.editPost, name='editPost'),
    url(r'^vote_post/?$', views.votePost, name='votePost'),
    url(r'^user/(.+)/summary/?$', views.userSummary, name='userSummary'),
    url(r'^user/(.+)/threads/?$', views.userThreadsPage, name='userThreads'),
    url(r'^user/(.+)/replies/?$', views.userRepliesPage, name='userReplies'),
]
