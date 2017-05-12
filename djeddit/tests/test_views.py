from django import VERSION as DJANGO_VERSION
from django.test import TestCase
if DJANGO_VERSION[:2] < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse
from djeddit.utils.base_tests import TestCalls, createUser
from djeddit.models import Topic, Thread, Post, gen_uuid, UserPostVote


# Create your tests here.


class CreateThreadTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/create_thread.html')

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='user', email='user@example.com', password='pass')
        cls.topic = Topic.objects.create(title='Test_Topic')
        cls.url = reverse('createThread', args=[cls.topic.title])

    def testLoads(self):
        self._test_call_view_loads(self.url, {})

    def _testSubmit(self, data):
        self._test_call_view_submit(self.url, data, redirect=True)
        thread = Thread.objects.get(topic=self.topic, title=data['thread-title'])
        self.assertEqual(thread.op.content, data['post-content'])

    def testSubmitUnauthenticated(self):
        data = {'post-content': 'content', 'thread-title': 'Thread1', 'thread-url': ''}
        self._testSubmit(data)

    def testSubmitAuthenticated(self):
        data = {'post-content': 'content', 'thread-title': 'Thread1', 'thread-url': ''}
        self.login()
        self._testSubmit(data)

class TopicsPageTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/topics.html')

    def testLoads(self):
        url = reverse('topics')
        self._test_call_view_loads(url)


class TopicPageTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/topic.html')

    @classmethod
    def setUpTestData(cls):
        cls.topic = Topic.objects.create(title='Test_Topic')

    def testLoads(self):
        url = reverse('topicPage', args=[self.topic.getUrlTitle()])
        self._test_call_view_loads(url)

    def testRedirects(self):
        url = reverse('topicPage', args=['Fake_Topic'])
        redirected_url = reverse('topics')
        self._test_call_view_redirects(url, redirected_url)


class ThreadPageTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/thread.html')

    @classmethod
    def setUpTestData(cls):
        cls.topic = Topic.objects.create(title='Test_Topic')
        cls.thread = Thread.objects.create(title='Test_Thread', topic=cls.topic, op=Post.objects.create())

    def testLoads(self):
        url = reverse('threadPage', args=[self.topic.title, self.thread.id])
        self._test_call_view_loads(url)

    def testWrongTopic(self):
        url = reverse('threadPage', args=['Fake_Topic', self.thread.id])
        redirected_url = reverse('topics')
        self._test_call_view_redirects(url, redirected_url)

    def testWrongThread(self):
        url = reverse('threadPage', args=[self.topic.title, self.thread.id + 1])
        redirected_url = reverse('topics')
        self._test_call_view_redirects(url, redirected_url)


class ReplyPostTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/reply_form.html')

    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create()
        topic = Topic.objects.create(title='Test_Topic')
        Thread.objects.create(title='Test_Thread', topic=topic, op=cls.post)
        cls.url = reverse('replyPost', args=[cls.post.uid])

    def testLoads(self):
        self._test_call_view_loads(self.url)

    def testSubmit(self):
        self._test_call_view_submit(self.url, dict(content='replied'), redirect=True)
        Post.objects.get(parent=self.post, content='replied') # assert object exists

    def testUnknownUid(self):
        uid = gen_uuid()
        url = reverse('replyPost', args=[str(uid)])
        self._test_call_view_code(url, 404)

    def testNoThread(self):
        post = Post.objects.create()
        url = reverse('replyPost', args=[str(post.uid)])
        self._test_call_view_code(url, 404)


class EditPostTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/edit_post.html')

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='user', email='user@example.com', password='pass')
        cls.post = Post.objects.create(created_by=cls.user)
        topic = Topic.objects.create(title='Test_Topic')
        Thread.objects.create(title='Test_Thread', topic=topic, op=cls.post)
        cls.url = reverse('editPost', args=[cls.post.uid])

    def testLoads(self):
        self.login()
        self._test_call_view_loads(self.url)

    def testSubmit(self):
        self.login()
        self._test_call_view_submit(self.url, dict(content='edited'), redirect=True)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, 'edited')

    def testUnknownUid(self):
        uid = gen_uuid()
        self.login()
        url = reverse('editPost', args=[str(uid)])
        self._test_call_view_code(url, 404)

    def testNoThread(self):
        post = Post.objects.create()
        url = reverse('editPost', args=[str(post.uid)])
        self.login()
        self._test_call_view_code(url, 404)

    def testEditAnotherPost(self):
        user = createUser('user1', 'user1@example.com', 'pass')
        post = Post.objects.create(created_by=user)
        url = reverse('editPost', args=[str(post.uid)])
        self.login()
        self._test_call_view_code(url, 404)


class VotePostTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='user', email='user@example.com', password='pass')
        cls.post = Post.objects.create()
        cls.url = reverse('votePost')

    def _testVote(self, submit_val, expected_score, expected_votePost_val):
        self._test_call_view_submit(self.url, dict(post=self.post.uid, vote=submit_val))
        user_vote = UserPostVote.objects.get(user=VotePostTest.user, post=self.post)  # assert object exists
        self.assertEqual(user_vote.val, expected_votePost_val)
        self.post.refresh_from_db()
        self.assertEqual(self.post.score, expected_score)

    def testSubmit(self):
        self.login()
        self.assertEqual(self.post.score, 0)
        self._testVote(1, 1, 1) # test upvote
        self._testVote(2, 1, 1) # test vote value above 1
        self._testVote(-1, -1, -1) # test downvote
        self._testVote(-2, -1, -1) # test downvote value below -1

    def testRequiresLogin(self):
        self._test_call_view_require_login(self.url, dict(post=self.post.uid, vote=1))

    def testVoteOwnPost(self):
        self.login()
        post = Post.objects.create(created_by=VotePostTest.user)
        response = self.client.post(self.url, dict(post=post.uid, vote=1))
        self.assertEqual(response.status_code, 403)


class UserSummaryTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/user_summary.html')

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='user', email='user@example.com', password='pass')
        cls.topic = Topic.objects.create(title='Test_Topic')
        cls.url = reverse('userSummary', args=[cls.username])

    def testLoadsEmpty(self):
        self._test_call_view_loads(self.url)

    def testLoads(self):
        op = Post.objects.create(created_by=self.user)
        Thread.objects.create(topic=self.topic, title='Test Thread', op=op)
        Post.objects.create(created_by=self.user)
        self._test_call_view_loads(self.url)

    def testInvalidUser(self):
        url = reverse('userSummary', args=['invaliduser'])
        self._test_call_view_code(url, 404)


class UserThreadsPageTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/user_threads.html')

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='user', email='user@example.com', password='pass')
        cls.topic = Topic.objects.create(title='Test_Topic')
        cls.url = reverse('userThreads', args=[cls.username])

    def testLoadsEmpty(self):
        self._test_call_view_loads(self.url)

    def testLoads(self):
        op = Post.objects.create(created_by=self.user, content='op content')
        Thread.objects.create(topic=self.topic, title='Test Thread', op=op)
        self._test_call_view_loads(self.url)

    def testInvalidUser(self):
        url = reverse('userSummary', args=['invaliduser'])
        self._test_call_view_code(url, 404)


class UserRepliesPageTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/user_threads.html')

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='user', email='user@example.com', password='pass')
        topic = Topic.objects.create(title='Test_Topic')
        cls.thread = Thread.objects.create(topic=topic, title='Test Thread', op=Post.objects.create())
        cls.url = reverse('userThreads', args=[cls.username])

    def testLoadsEmpty(self):
        self._test_call_view_loads(self.url)

    def testLoads(self):
        Post.objects.create(parent=self.thread.op)
        self._test_call_view_loads(self.url)

    def testInvalidUser(self):
        url = reverse('userSummary', args=['invaliduser'])
        self._test_call_view_code(url, 404)
