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
