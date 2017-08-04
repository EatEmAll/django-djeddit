"""django1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views
from django.conf import settings

if not hasattr(settings, 'TOPICS_URL'):
    settings.TOPICS_URL = ''
topic_prefix = '%s/' % settings.TOPICS_URL if settings.TOPICS_URL else ''


urlpatterns = [
    url(r'^%s$' % (topic_prefix + '/?' if topic_prefix else ''), views.topicsPage, name='topics'),
    url(r'^lock_thread/(\d+)/?$', views.lockThread, name='lockThread'),
    url(r'^reply_post/([\w\-]{36})?/?$', views.replyPost, name='replyPost'),
    url(r'^edit_post/([\w\-]{36})?/?$', views.editPost, name='editPost'),
    url(r'^vote_post/?$', views.votePost, name='votePost'),
    url(r'^delete_post/([\w\-]{36})/?$', views.deletePost, name='deletePost'),
    url(r'^load_additional_replies/?$', views.loadAdditionalReplies, name='loadAdditionalReplies'),
    url(r'^user/(.+)/summary/?$', views.userSummary, name='userSummary'),
    url(r'^user/(.+)/threads/?$', views.userThreadsPage, name='userThreads'),
    url(r'^user/(.+)/replies/?$', views.userRepliesPage, name='userReplies'),
    url(r'^users/?$', views.usersPage, name='usersPage'),
    url(r'^set_user_status/?$', views.setUserStatus, name='setUserStatus'),
    url(r'^%s(\w+)/?$' % topic_prefix, views.topicPage, name='topicPage'),
    url(r'^%s(\w+)/delete_topic/?$' % topic_prefix, views.deleteTopic, name='deleteTopic'),
    url(r'^%s(\w+)/newthread/?$' % topic_prefix, views.createThread, name='createThread'),
    url(r'^%s(\w+)/(\d+)?/?$' % topic_prefix, views.threadPage, name='threadPage'),
]
