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
        self._test_call_view_submit(self.url, code=302, data=data)
        thread = Thread.objects.get(topic=self.topic, title=data['thread-title'])
        self.assertEqual(thread.op.content, data['post-content'])

    def testSubmitUnauthenticated(self):
        data = {'post-content': 'content', 'thread-title': 'Thread1', 'thread-url': ''}
        self._testSubmit(data)

    def testSubmitAuthenticated(self):
        data = {'post-content': 'content', 'thread-title': 'Thread1', 'thread-url': ''}
        self.login()
        self._testSubmit(data)


class LockThreadTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        topic = Topic.objects.create(title='Test_Topic')
        cls.thread = Thread.objects.create(title='Test_Thread', topic=topic, op=Post.objects.create())
        cls.url = reverse('lockThread', args=[cls.thread.id])

    def testLockAndUnlock(self):
        self.login()
        # lock thread
        self._test_call_view_code(self.url, 302)
        # test thread is locked
        replyUrl = reverse('replyPost', args=[self.thread.op.uid])
        self._test_call_view_code(replyUrl, 403, data=dict(content='replied'), post=True)
        editUrl = reverse('editPost', args=[self.thread.op.uid])
        self._test_call_view_code(editUrl, 403, data={'post-content': 'edited'}, post=True)
        # unlock thread
        self._test_call_view_code(self.url, 302)
        # test thread is unlocked
        self._test_call_view_code(replyUrl, 302, data=dict(content='replied'), post=True)
        Post.objects.get(parent=self.thread.op, content='replied')  # assert object exists
        self._test_call_view_code(editUrl, 302, data={'post-content': 'edited'}, post=True)
        self.thread.op.refresh_from_db()
        self.assertEqual(self.thread.op.content, 'edited')

    def testRequireSuperUser(self):
        self._setup_user('not_admin', 'not_admin@example.com', password='pass')
        self.login()
        self._test_call_view_redirected_login(self.url)

    def testUnauthenticated(self):
        self._test_call_view_redirected_login(self.url)

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
        self._test_call_view_submit(self.url, code=302, data=dict(content='replied'))
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
        user1 = createUser('user1', 'user1@example.com', 'pass')
        cls.User1Post = Post.objects.create(created_by=user1, parent=cls.post)
        cls.url = reverse('editPost', args=[cls.post.uid])

    def testLoads(self):
        self.login()
        self._test_call_view_loads(self.url)

    def testSubmit(self):
        self.login()
        self._test_call_view_submit(self.url, code=302, data={'post-content': 'edited'})
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
        url = reverse('editPost', args=[str(self.User1Post.uid)])
        self.login()
        self._test_call_view_code(url, 403)

    def testEditAnotherPostAsSuperuser(self):
        self._login_as_admin()
        url = reverse('editPost', args=[str(self.User1Post.uid)])
        self._test_call_view_submit(url, code=302, data={'post-content': 'edited'})
        self.User1Post.refresh_from_db()
        self.assertEqual(self.User1Post.content, 'edited')

    def testEditThread(self):
        self._login_as_admin()
        self._test_call_view_submit(self.url, code=302, data={'post-content': 'edited'})
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, 'edited')


class VotePostTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='user', email='user@example.com', password='pass')
        cls.post = Post.objects.create()
        cls.url = reverse('votePost')

    def _testVote(self, submit_val, expected_score, expected_votePost_val, user=None, post=None):
        user = user or VotePostTest.user
        post = post or self.post
        self._test_call_view_submit(self.url, data=dict(post=post.uid, vote=submit_val))
        user_vote = UserPostVote.objects.get(user=user, post=post)  # assert object exists
        self.assertEqual(user_vote.val, expected_votePost_val)
        post.refresh_from_db()
        self.assertEqual(post.score, expected_score)

    def testSubmit(self):
        self.login()
        self.assertEqual(self.post.score, 0)
        self._testVote(1, 1, 1) # test upvote
        self._testVote(2, 1, 1) # test vote value above 1
        self._testVote(-1, -1, -1) # test downvote
        self._testVote(-2, -1, -1) # test downvote value below -1

    def testRequiresLogin(self):
        self._test_call_view_redirected_login(self.url, dict(post=self.post.uid, vote=1))

    def testVoteOwnPost(self):
        self.login()
        post = Post.objects.create(created_by=VotePostTest.user)
        self._test_call_view_submit(self.url, code=403, data=dict(post=post.uid, vote=1))

    def testVoteOwnPostAsSuperuser(self):
        admin = self._login_as_admin()
        post = Post.objects.create(created_by=admin)
        self._testVote(1, 1, 1, user=admin, post=post)


class DeletePostTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        topic = Topic.objects.create(title='Test_Topic')
        cls.thread = Thread.objects.create(title='Test_Thread', topic=topic, op=Post.objects.create())
        cls.comment = Post.objects.create(parent=cls.thread.op)
        cls.url = reverse('deletePost', args=[cls.comment.uid])

    def testRequireLogin(self):
        self._test_call_view_redirected_login(self.url)

    def testRequireSuperUser(self):
        createUser(username='user', email='user@example.com', password='pass')
        self.login(username='user', password='pass')
        self._test_call_view_redirected_login(self.url)

    def testDeleteComment(self):
        self.login()
        redirect_url = reverse('threadPage', args=[self.thread.topic.title, self.thread.id])
        self._test_call_view_redirects(self.url, redirect_url)
        self.assertRaises(Post.DoesNotExist, self.comment.refresh_from_db)

    def testDeleteThread(self):
        self.login()
        url = reverse('deletePost', args=[self.thread.op.uid])
        redirect_url = reverse('topicPage', args=[self.thread.topic.title])
        self._test_call_view_redirects(url, redirect_url)
        self.assertRaises(Post.DoesNotExist, self.thread.op.refresh_from_db)
        self.assertRaises(Thread.DoesNotExist, self.thread.refresh_from_db)


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
