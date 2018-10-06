# Python standard imports
import json
import logging

# Core Dajngo imports
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Third-party app imports
from ipware.ip import get_ip
from meta.views import Meta

# Imports from our apps
from djeddit.forms import TopicForm, ThreadForm, PostForm
from djeddit.models import Topic, Thread, Post, UserPostVote
from djeddit.templatetags.djeddit_tags import postScore
from djeddit.utils.utility_funcs import is_authenticated


# Create your views here.


def createThread(request, topic_title=None):
    if topic_title:
        try:
            if request.method == 'POST':
                topic = Topic.getTopic(topic_title)
                threadForm = ThreadForm(request.POST, prefix='thread')
                postForm = PostForm(request.POST, prefix='post')
                if threadForm.is_valid() and postForm.is_valid():
                    thread = threadForm.save(commit=False)
                    post = postForm.save(commit=False)
                    post.setMeta(request)
                    if is_authenticated(request):
                        post.created_by = request.user
                    post.save()
                    thread.op = post
                    thread.topic = topic
                    thread.save()
                    return HttpResponseRedirect(thread.relativeUrl)
            else:
                threadForm = ThreadForm(prefix='thread')
                postForm = PostForm(prefix='post')
            context = dict(threadForm=threadForm, postForm=postForm)
            return render(request, 'djeddit/create_thread.html', context)
        except Topic.DoesNotExist:
            pass
    return redirect('topics')


@user_passes_test(lambda u: u.is_superuser)
def deleteTopic(request, topic_title):
    try:
        topic = Topic.getTopic(topic_title)
    except Topic.DoesNotExist:
        raise Http404()
    topic.delete()
    return redirect('topics')


@user_passes_test(lambda u: u.is_superuser)
def lockThread(request, thread_id):
    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        raise Http404
    thread.locked = not thread.locked
    thread.save()
    return HttpResponseRedirect(thread.relativeUrl)


@user_passes_test(lambda u: u.is_superuser)
def stickyThread(request, thread_id):
    try:
        thread = Thread.objects.get(id=thread_id)
    except Thread.DoesNotExist:
        raise Http404
    thread.is_stickied = not thread.is_stickied
    thread.save()
    return HttpResponseRedirect(thread.relativeUrl)


def topicsPage(request):
    topics = Topic.objects.all()
    if request.method == 'POST':
        topicForm = TopicForm(request.POST)
        if topicForm.is_valid():
            topicForm.save()
            return redirect('topics')
        showForm = True
    else:
        topicForm = TopicForm()
        showForm = False
    context = dict(topics=topics, topicForm=topicForm, showForm=showForm)
    return render(request, 'djeddit/topics.html', context)


def topicPage(request, topic_title):
    try:
        topic = Topic.getTopic(topic_title)
    except Topic.DoesNotExist:
        raise Http404()
    # edit topic form
    if topic.urlTitle != topic_title:
        return redirect('topicPage', topic.urlTitle)
    if request.method == 'POST':
        if not request.user.is_superuser:
            return HttpResponseForbidden()
        form = TopicForm(request.POST, instance=topic)
        if form.is_valid():
            form.save()
            return redirect('topicPage', topic.urlTitle)
        showForm = True
    else:
        form = TopicForm(instance=topic)
        showForm = False
    threads = Thread.objects.filter(topic=topic).order_by('-is_stickied', '-op__created_on')
    context = dict(topic=topic, threads=threads, showCreatedBy=True, showTopic=False,
                   topicForm=form, showForm=showForm)
    return render(request, 'djeddit/topic.html', context)


def threadPage(request, topic_title='', thread_id='', slug=''):
    if topic_title and thread_id:
        try:
            topic = Topic.getTopic(topic_title)
            thread = Thread.objects.get(id=thread_id)
            if thread.topic == topic:
                if not slug or slug != thread.slug or topic.urlTitle != topic_title:
                    return HttpResponseRedirect(thread.relativeUrl)
                if thread.op.content:
                    description = thread.op.content[:160]
                else:
                    description = getattr(settings, "DJEDDIT_DESCRIPTION", "The link sharing and discussion portal")
                meta = Meta(
                    title=thread.title,
                    use_title_tag=True,
                    description=description,
                )
                thread.views += 1
                thread.save()
                context = dict(thread=thread, nodes=thread.op.getSortedReplies(), meta=meta)
                return render(request, 'djeddit/thread.html', context)
        except (Topic.DoesNotExist, Thread.DoesNotExist):
            pass
    raise Http404


def replyPost(request, post_uid=''):
    try:
        repliedPost = Post.objects.get(uid=post_uid)
        thread = repliedPost.thread
    except (Post.DoesNotExist, Thread.DoesNotExist):
        raise Http404
    if thread.locked:
        return HttpResponseForbidden()
    repliedUser = repliedPost.created_by.username if repliedPost.created_by else 'guest'
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        if postForm.is_valid():
            post = postForm.save(commit=False)
            post.parent = repliedPost
            post.setMeta(request)

            if is_authenticated(request):
                post.created_by = request.user
            post.save()
            repliedPost.children.add(post)
        return HttpResponseRedirect(thread.relativeUrl)
    else:
        postForm = PostForm()
        postForm.fields['content'].label = ''
        context = dict(postForm=postForm, thread_id=thread.id, post_uid=post_uid, repliedUser=repliedUser)
        return render(request, 'djeddit/reply_form.html', context)


def editPost(request, post_uid=''):
    try:
        post = Post.objects.get(uid=post_uid)
        thread = post.thread
    except (Post.DoesNotExist, Thread.DoesNotExist):
        raise Http404
    if thread.locked or (request.user != post.created_by and not request.user.is_superuser):
        return HttpResponseForbidden()
    if request.method == 'POST':
        postForm = PostForm(request.POST, instance=post, prefix='post')
        threadForm = ThreadForm(request.POST, instance=thread, prefix='thread')
        if postForm.is_valid():
            postForm.save()
        if threadForm.is_valid():
            threadForm.save()
        return HttpResponseRedirect(thread.relativeUrl)
    else:
        postForm = PostForm(instance=post, prefix='post')
        if request.user.is_superuser and thread.op == post:
            threadForm = ThreadForm(instance=thread, prefix='thread')
        else:
            threadForm = None
            postForm.fields['content'].label = ''
        context = dict(postForm=postForm, threadForm=threadForm, post_uid=post.uid, thread=thread, post=post)
        return render(request, 'djeddit/edit_post.html', context)


@login_required
def votePost(request):
    try:
        post_uid = request.POST['post']
        vote_val = request.POST['vote']
        post = Post.objects.get(uid=post_uid)
    except (KeyError, ValueError, Post.DoesNotExist):
        return HttpResponseBadRequest()
    if post.created_by != request.user or request.user.is_superuser:
        try:
            userPostVote = UserPostVote.objects.get(user=request.user, post=post)
            oldval = userPostVote.val
            userPostVote.val = max(min(int(vote_val), 1), -1)
            userPostVote.save()
            voteDelta = userPostVote.val - oldval
        except UserPostVote.DoesNotExist:
            userPostVote = UserPostVote.objects.create(user=request.user, post=post, val=max(min(int(vote_val), 1), -1))
            voteDelta = userPostVote.val
        if voteDelta:
            if voteDelta > 0:
                if userPostVote.val:
                    post.upvotes += 1
                    if voteDelta == 2:
                        post.downvotes -= 1
                else:
                    post.downvotes -= 1
            else:
                if userPostVote.val:
                    post.downvotes += 1
                    if voteDelta == -2:
                        post.upvotes -= 1
                else:
                    post.upvotes -= 1
            post.save()
        scoreStr = postScore(post.score)
        return JsonResponse(dict(scoreStr=scoreStr, score=post.score))
    else:
        return HttpResponseForbidden()


@user_passes_test(lambda u: u.is_superuser)
def deletePost(request, post_uid):
    try:
        post = Post.objects.get(uid=post_uid)
    except Post.DoesNotExist:
        raise Http404
    thread = post.thread
    op = thread.op
    post_uid = post.uid
    post.delete()
    if op.uid == post_uid:
        return redirect('topicPage', thread.topic.urlTitle)
    else:
        return HttpResponseRedirect(thread.relativeUrl)


def loadAdditionalReplies(request):
    """load additional replies to a given post."""
    try:
        post_uid = request.GET['post']
        # exclude all posts with these uids and their descendants
        excluded_uids = json.loads(request.GET['excluded'])
        post = Post.objects.get(uid=post_uid)
    except (KeyError, ValueError, json.decoder.JSONDecodeError, Post.DoesNotExist):
        return HttpResponseBadRequest()
    replies = post.getSortedReplies(excluded=excluded_uids)
    context = dict(thread=post.thread, nodes=replies)
    return render(request, 'djeddit/thread_recursetree.html', context)


def userSummary(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    threads = Thread.objects.filter(op__created_by=user)
    for t in threads:
        t.modified_on = t.op.modified_on
    replies = Post.objects.filter(created_by=user).exclude(parent=None)
    context = dict(items=sorted(list(threads) + list(replies), key=lambda n: n.modified_on, reverse=True),
                   tCount=threads.count(),
                   rCount=replies.count(),
                   tPoints=(sum(t.op.score for t in threads)),
                   rPoints=(sum(r.score for r in replies)),
                   pageUser=user)
    return render(request, 'djeddit/user_summary.html', context)


def userThreadsPage(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    created_threads = Thread.objects.filter(op__created_by=user)
    context = dict(threads=created_threads, showCreatedBy=False, showTopic=True, pageUser=user)
    return render(request, 'djeddit/user_threads.html', context)


def userRepliesPage(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    replies = Post.objects.filter(created_by=user, parent__isnull=False)
    context = dict(replies=replies, pageUser=user)
    return render(request, 'djeddit/user_replies.html', context)


@user_passes_test(lambda u: u.is_superuser)
def usersPage(request):
    """list users with their thread count and replies counts"""
    users = User.objects.all()
    for user in users:
        user.tCount = Thread.objects.filter(op__created_by=user).count()
        user.rCount = Post.objects.filter(created_by=user).exclude(parent=None).count()
    return render(request, 'djeddit/users_page.html', dict(Users=users))


@user_passes_test(lambda u: u.is_superuser)
def setUserStatus(request):
    """set user status to either active (is_active=True), banned(is_active=False), or admin(is_superuser=True)"""
    try:
        username = request.POST['username']
        status = request.POST['status']
    except KeyError:
        return HttpResponseBadRequest()
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404()
    if status == 'active':
        user.is_active = True
        user.is_superuser = False
    elif status == 'banned':
        user.is_active = False
        user.is_superuser = False
    elif status == 'admin':
        user.is_active = True
        user.is_superuser = True
    else:
        return HttpResponseBadRequest()
    user.save()
    return HttpResponse()
