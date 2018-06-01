from django import VERSION as DJANGO_VERSION
from django.test import TestCase

if DJANGO_VERSION[:2] < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse
from djeddit.utils.base_tests import TestCalls, createUser
from djeddit.models import Topic, Thread, Post, UserPostVote
from djeddit.utils.utility_funcs import gen_uuid


# Create your tests here.


class CreateThreadTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/create_thread.html')

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='user', email='user@example.com', password='pass')
        cls.topic = Topic.objects.create(title='Test Topic')
        cls.url = reverse('createThread', args=[cls.topic.urlTitle])

    def testLoads(self):
        self._test_call_view_loads(self.url)

    def _testSubmit(self, data):
        self._test_call_view_submit(self.url, code=302, data=data)
        thread = Thread.objects.get(topic=self.topic, title=data['thread-title'])
        self.assertEqual(thread.op.content, data['post-content'])
        self.assertEqual(thread.op.ip_address, '127.0.0.1')
        self.assertEqual(thread.op.user_agent, None)

    def testSubmitUnauthenticated(self):
        data = {'post-content': 'content', 'thread-title': 'Thread1', 'thread-url': ''}
        self._testSubmit(data)

    def testSubmitAuthenticated(self):
        data = {'post-content': 'content', 'thread-title': 'Thread1', 'thread-url': ''}
        self.login()
        self._testSubmit(data)


class DeleteTopicTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        cls.topic = Topic.objects.create(title='Test Topic')
        cls.url = reverse('deleteTopic', args=[cls.topic.urlTitle])

    def testDeleteTopic(self):
        self.login()
        self._test_call_view_submit(self.url, code=302)
        self.assertRaises(Topic.DoesNotExist, self.topic.refresh_from_db)

    def testUnknownTopic(self):
        self.login()
        url = reverse('deleteTopic', args=['Fake_Topic'])
        self._test_call_view_code(url, 404)

    def testRequireLogin(self):
        self._test_call_view_redirected_login(self.url)

    def testRequireSuperUser(self):
        self._create_user_and_login()
        self.login('user', 'pass')
        self._test_call_view_redirected_login(self.url)


class LockThreadTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        topic = Topic.objects.create(title='Test Topic')
        cls.thread = Thread.objects.create(title='Test_Thread', topic=topic, op=Post.objects.create())
        cls.url = reverse('lockThread', args=[cls.thread.id])

    def _testLockAndUnlock(self):
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

    def _testRequireSuperUser(self):
        self._setup_user('not_admin', 'not_admin@example.com', password='pass')
        self.login()
        self._test_call_view_redirected_login(self.url)

    def runTestsInSequence(self):
        self._testLockAndUnlock()
        self._testRequireSuperUser()

    def testRequireLogin(self):
        self._test_call_view_redirected_login(self.url)


class StickyThreadTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        topic = Topic.objects.create(title='Test Topic')
        cls.thread = Thread.objects.create(title='Test_Thread', topic=topic, op=Post.objects.create())
        cls.url = reverse('stickyThread', args=[cls.thread.id])

    def _testStickyAndUnsticky(self):
        self.login()
        self.assertEqual(self.thread.is_stickied, False)
        self._test_call_view_code(self.url, 302) # set sticky to true
        self.assertEqual(self.thread.is_stickied, True)
        self._test_call_view_code(self.url, 302)  # set sticky to false
        self.assertEqual(self.thread.is_stickied, False)

    def _testRequireSuperUser(self):
        self._setup_user('not_admin', 'not_admin@example.com', password='pass')
        self.login()
        self._test_call_view_redirected_login(self.url)

    def runTestsInSequence(self):
        self._testStickyAndUnsticky()
        self._testRequireSuperUser()

    def testRequireLogin(self):
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
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        cls.topic = Topic.objects.create(title='Test Topic')
        cls.url = reverse('topicPage', args=[cls.topic.urlTitle])

    def testLoads(self):
        self._test_call_view_loads(self.url)

    def testRedirectsOldTitle(self):
        url = reverse('topicPage', args=[self.topic.title.replace(' ', '_')])
        self._test_call_view_redirects(url, redirected_url=self.url)

    def testUnknownTopic(self):
        url = reverse('topicPage', args=['Fake_Topic'])
        self._test_call_view_code(url, 404)

    def testEditTopic(self):
        self.login()
        data = dict(title='Test Topic edited', description='Test Description')
        self._test_call_view_submit(self.url, code=302, data=data)
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.title, data['title'])
        self.assertEqual(self.topic.description, data['description'])

    def testEditTopicRequireLogin(self):
        data = dict(title='Test Topic (edited)', description='Test Description')
        self._test_call_view_submit(self.url, code=403, data=data)
        self.topic.refresh_from_db()
        self.assertNotEqual(self.topic.title, data['title'])
        self.assertNotEqual(self.topic.description, data['description'])

    def testEditTopicRequireSuperUser(self):
        self._create_user_and_login()
        self.login('user', 'pass')
        self.testEditTopicRequireLogin()


class ThreadPageTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/thread.html')

    @classmethod
    def setUpTestData(cls):
        cls.topic = Topic.objects.create(title='Test Topic')
        cls.thread = Thread.objects.create(title='Test_Thread', topic=cls.topic, op=Post.objects.create())

    def testLoads(self):
        self._test_call_view_loads(self.thread.relativeUrl)

    def testWrongSlug(self):
        # test no slug
        url = reverse('threadPage', args=[self.topic.urlTitle, self.thread.pk])
        self._test_call_view_redirects(url, redirected_url=self.thread.relativeUrl)
        # test wrong slug
        url = reverse('threadPage', args=[self.topic.urlTitle, self.thread.pk, 'wrong-page'])
        self._test_call_view_redirects(url, redirected_url=self.thread.relativeUrl)

    def testWrongTopic(self):
        url = reverse('threadPage', args=['Fake_Topic', self.thread.id, 'fake-topic'])
        self._test_call_view_code(url, 404)

    def testOldTitleRedirect(self):
        url = reverse('threadPage', args=[self.topic.title.replace(' ', '_'), self.topic.pk, self.thread.slug])
        self._test_call_view_redirects(url, redirected_url=self.thread.relativeUrl)

    def testWrongThread(self):
        url = reverse('threadPage', args=[self.topic.urlTitle, self.thread.id + 1, 'fake-topic'])
        self._test_call_view_code(url, 404)


class ReplyPostTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/reply_form.html')

    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create()
        topic = Topic.objects.create(title='Test Topic')
        Thread.objects.create(title='Test_Thread', topic=topic, op=cls.post)
        cls.url = reverse('replyPost', args=[cls.post.uid])

    def testLoads(self):
        self._test_call_view_loads(self.url)

    def testSubmit(self):
        self._test_call_view_submit(self.url, code=302, data=dict(content='replied'))
        rp = Post.objects.get(parent=self.post, content='replied')  # assert object exists
        self.assertEqual(rp.ip_address, '127.0.0.1')
        self.assertEqual(rp.user_agent, None)

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
        topic = Topic.objects.create(title='Test Topic')
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
        self._create_user_and_login(create_admin=True)
        url = reverse('editPost', args=[str(self.User1Post.uid)])
        self._test_call_view_submit(url, code=302, data={'post-content': 'edited'})
        self.User1Post.refresh_from_db()
        self.assertEqual(self.User1Post.content, 'edited')

    def testEditThread(self):
        self._create_user_and_login(create_admin=True)
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
        self._testVote(1, 1, 1)  # test upvote
        self._testVote(2, 1, 1)  # test vote value above 1
        self._testVote(-1, -1, -1)  # test downvote
        self._testVote(-2, -1, -1)  # test downvote value below -1

    def testRequiresLogin(self):
        self._test_call_view_redirected_login(self.url, dict(post=self.post.uid, vote=1))

    def testEmptyData(self):
        self.login()
        self._test_call_view_code(self.url, 400, post=True)

    def testVoteOwnPost(self):
        self.login()
        post = Post.objects.create(created_by=VotePostTest.user)
        self._test_call_view_submit(self.url, code=403, data=dict(post=post.uid, vote=1))

    def testVoteOwnPostAsSuperuser(self):
        admin = self._create_user_and_login(create_admin=True)
        post = Post.objects.create(created_by=admin)
        self._testVote(1, 1, 1, user=admin, post=post)


class DeletePostTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        topic = Topic.objects.create(title='Test Topic')
        cls.thread = Thread.objects.create(title='Test_Thread', topic=topic, op=Post.objects.create())
        cls.comment = Post.objects.create(parent=cls.thread.op)
        cls.url = reverse('deletePost', args=[cls.comment.uid])

    def testRequireLogin(self):
        self._test_call_view_redirected_login(self.url)

    def testRequireSuperUser(self):
        self._create_user_and_login()
        self._test_call_view_redirected_login(self.url)

    def testDeleteComment(self):
        self.login()
        self._test_call_view_redirects(self.url, self.thread.relativeUrl)
        self.assertRaises(Post.DoesNotExist, self.comment.refresh_from_db)

    def testDeleteThread(self):
        self.login()
        url = reverse('deletePost', args=[self.thread.op.uid])
        redirect_url = reverse('topicPage', args=[self.thread.topic.urlTitle])
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
        cls.topic = Topic.objects.create(title='Test Topic')
        cls.url = reverse('userSummary', args=[cls.username])

    def testLoadsEmpty(self):
        self._test_call_view_loads(self.url)

    def testLoads(self):
        op = Post.objects.create(created_by=self.user)
        Thread.objects.create(topic=self.topic, title='Test Thread', op=op)
        Post.objects.create(created_by=self.user, parent=op)
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
        cls.topic = Topic.objects.create(title='Test Topic')
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
        topic = Topic.objects.create(title='Test Topic')
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


class UsersPageTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self, 'djeddit/users_page.html')

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        cls.url = reverse('usersPage')

    def testLoads(self):
        user = createUser()
        topic = Topic.objects.create(title='Test Topic')
        op = Post.objects.create(created_by=user)
        Thread.objects.create(topic=topic, title='Test Thread', op=op)
        Post.objects.create(created_by=user, parent=op)
        self.login()
        self._test_call_view_loads(self.url)

    def testRequireLogin(self):
        self._test_call_view_redirected_login(self.url)

    def testRequireSuperUser(self):
        self._create_user_and_login()
        self._test_call_view_redirected_login(self.url)


class SetUserStatusTest(TestCase, TestCalls):
    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        TestCalls.__init__(self)

    @classmethod
    def setUpTestData(cls):
        cls._setup_user(username='admin', email='admin@example.com', password='pass', is_superuser=True)
        cls.url = reverse('setUserStatus')

    def _testChangeStatus(self, user, status):
        self._test_call_view_submit(self.url, data=dict(username=user.username, status=status))
        user.refresh_from_db()
        if status == 'active':
            self.assertTrue(user.is_active)
            self.assertTrue(not user.is_superuser)
        elif status == 'banned':
            self.assertTrue(not user.is_active)
            self.assertTrue(not user.is_superuser)
        elif status == 'admin':
            self.assertTrue(user.is_active)
            self.assertTrue(user.is_superuser)
        else:
            raise Exception('Invalid status: %s' % status)

    def testPromoteToAdmin(self):
        user = self._create_user_and_login()
        self.login()
        self._testChangeStatus(user, 'admin')
        self._testChangeStatus(user, 'active')
        self._testChangeStatus(user, 'banned')

    def testRequireLogin(self):
        self._test_call_view_redirected_login(self.url)

    def testRequireSuperUser(self):
        self._create_user_and_login()
        self._test_call_view_redirected_login(self.url)
