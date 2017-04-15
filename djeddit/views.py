# -*- coding: utf-8 -*-
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    UpdateView,
    ListView
)

from .models import (
	Topic,
	Thread,
	Post,
	UserPostVote,
)


class TopicCreateView(CreateView):

    model = Topic


class TopicDeleteView(DeleteView):

    model = Topic


class TopicDetailView(DetailView):

    model = Topic


class TopicUpdateView(UpdateView):

    model = Topic


class TopicListView(ListView):

    model = Topic


class ThreadCreateView(CreateView):

    model = Thread


class ThreadDeleteView(DeleteView):

    model = Thread


class ThreadDetailView(DetailView):

    model = Thread


class ThreadUpdateView(UpdateView):

    model = Thread


class ThreadListView(ListView):

    model = Thread


class PostCreateView(CreateView):

    model = Post


class PostDeleteView(DeleteView):

    model = Post


class PostDetailView(DetailView):

    model = Post


class PostUpdateView(UpdateView):

    model = Post


class PostListView(ListView):

    model = Post


class UserPostVoteCreateView(CreateView):

    model = UserPostVote


class UserPostVoteDeleteView(DeleteView):

    model = UserPostVote


class UserPostVoteDetailView(DetailView):

    model = UserPostVote


class UserPostVoteUpdateView(UpdateView):

    model = UserPostVote


class UserPostVoteListView(ListView):

    model = UserPostVote

