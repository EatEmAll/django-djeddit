from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseForbidden

from djeddit.forms import TopicForm, ThreadForm, PostForm
from djeddit.models import Topic, Thread, Post, UserPostVote
from djeddit.templatetags.djeddit_tags import postScore
from django.contrib.auth.models import User


# Create your views here.

# @user_passes_test(lambda user: user.is_superuser)

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
                    thread.op = post
                    thread.topic = topic
                    thread.save()
                    post.thread = thread
                    if request.user.is_authenticated():
                        post.created_by = request.user
                    post.save()
                    return redirect('threadPage', topic.getUrlTitle(), thread.id)
            else:
                threadForm = ThreadForm(prefix='thread')
                postForm = PostForm(prefix='post')
            context = dict(threadForm=threadForm, postForm=postForm)
            return render(request, 'djeddit/create_thread.html', context)
        except Topic.DoesNotExist:
            pass
    return redirect('topics')


def topicsPage(request):
    topics = Topic.objects.all()
    showForm = False
    if request.method == 'POST':
        topicForm = TopicForm(request.POST)
        if topicForm.is_valid():
            topicForm.save()
            return redirect('topics')
        showForm = True
    else:
        topicForm = TopicForm()
    context = dict(topics=topics, topicForm=topicForm, showForm=showForm)
    return render(request, 'djeddit/topics.html', context)


def topicPage(request, topic_title=None):
    if topic_title:
        try:
            topic = Topic.getTopic(topic_title)
            threads = Thread.objects.filter(topic=topic)
            context = dict(topic=topic, threads=threads, showCreatedBy=True, showTopic=False)
            return render(request, 'djeddit/topic.html', context)
        except Topic.DoesNotExist:
            pass
    return redirect('topics')


def threadPage(request, topic_title='', thread_id=''):
    if topic_title and thread_id:
        try:
            topic = Topic.getTopic(topic_title)
            thread = Thread.objects.get(id=thread_id)
            if thread.topic.title == topic.title:
                thread.views += 1
                thread.save()
                context = dict(thread=thread, nodes=thread.op.getReplies())
                return render(request, 'djeddit/thread.html', context)
        except (Topic.DoesNotExist, Thread.DoesNotExist):
            pass
    return redirect('topics')


def homePage(request):
    # context = sorted(dict(request.GET, **request.POST).items())
    context = dict(request.GET, **request.POST)
    return render(request, 'djeddit/home.html', context)


def replyPost(request, post_uid=''):
    try:
        repliedPost = Post.objects.get(uid=post_uid)
        thread = repliedPost.getThread()
    except (Post.DoesNotExist, Thread.DoesNotExist):
        raise Http404
    repliedUser = repliedPost.created_by.username if repliedPost.created_by else 'guest'
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        if postForm.is_valid():
            post = postForm.save(commit=False)
            post.parent = repliedPost
            if request.user.is_authenticated():
                post.created_by = request.user
            post.save()
            repliedPost.children.add(post)
        return redirect('threadPage', thread.topic.getUrlTitle(), thread.id)
    else:
        postForm = PostForm()
        postForm.fields['content'].label = ''
        context = dict(postForm=postForm, thread_id=thread.id, post_uid=post_uid, repliedUser=repliedUser)
        return render(request, 'djeddit/reply_form.html', context)


def editPost(request, post_uid=''):
    try:
        post = Post.objects.get(uid=post_uid)
        thread = post.getThread()
    except (Post.DoesNotExist, Thread.DoesNotExist):
        raise Http404
    if request.user != post.created_by and not request.user.is_superuser:
        return HttpResponseForbidden()
    if request.method == 'POST':
        postForm = PostForm(request.POST, instance=post)
        if postForm.is_valid():
            postForm.save()
        return redirect('threadPage', thread.topic.getUrlTitle(), thread.id)
    else:
        postForm = PostForm(vars(post))
        postForm.fields['content'].label = ''
        context = dict(postForm=postForm, post_uid=post.uid)
        return render(request, 'djeddit/edit_post.html', context)


@login_required
def votePost(request):
    post_uid = request.POST['post']
    vote_val = request.POST['vote']
    post = Post.objects.get(uid=post_uid)
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
        post.score += voteDelta
        post.save()
        scoreStr = postScore(post.score)
        return JsonResponse(dict(scoreStr=scoreStr, score=post.score))
    else:
        return HttpResponseForbidden()


def userSummary(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404
    threads = Thread.objects.filter(op__created_by=user)
    for t in threads:
        t.modified_on = t.op.modified_on
    replies = Post.objects.filter(created_by=user).exclude(uid__in=(t.op.uid for t in threads))
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
