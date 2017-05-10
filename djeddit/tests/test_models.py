from django.test import TestCase
from djeddit.models import Topic, Thread, Post

# Create your tests here.


class TopicModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = Topic.objects.create(title='Test Topic')
        # create 3 threads
        cls.threadCount = 3
        cls.threads = [Thread.objects.create(title='Thread %s' % i,
                                             topic=cls.topic,
                                             op=Post.objects.create()) for i in range(1, cls.threadCount + 1)]

    def testThreadCount(self):
        self.assertEqual(self.topic.getThreadCount(), self.threadCount)

    def testGetUrlTitle(self):
        self.assertEqual(self.topic.getUrlTitle(), 'Test_Topic')

    def testGetTopic(self):
        self.assertEqual(Topic.getTopic('Test Topic'), self.topic)
        self.assertEqual(Topic.getTopic('Test_Topic'), self.topic)


class ThreadModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.thread = Thread.objects.create(title='Test Thread',
                                           topic=Topic.objects.create(title='Test Topic'),
                                           op=Post.objects.create())

    def testThreadDelete(self):
        uid = self.thread.op.uid
        self.thread.delete()
        self.assertRaises(Thread.DoesNotExist, Thread.objects.get, title='Test Thread')
        self.assertRaises(Post.DoesNotExist, Post.objects.get, uid=uid)


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create()
        cls.thread = Thread.objects.create(title='Test Thread', topic=Topic.objects.create(title='Test Topic'), op=cls.post)
        cls.replies = [Post.objects.create(parent=cls.post) for _ in range(1, 4)]

    def testGetReplies(self):
        self.assertListEqual(self.replies, list(self.post.getReplies()))

    def getThread(self):
        self.assertEqual(self.thread, self.post.getThread())
