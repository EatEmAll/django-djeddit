from django import VERSION as DJANGO_VERSION
from django.test import TestCase

if DJANGO_VERSION[:2] < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse
from djeddit.models import Topic, Thread, Post
from slugify import slugify

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

    def testUrlTitle(self):
        self.assertEqual(self.topic.urlTitle, 'Test-Topic')

    def testGetTopic(self):
        self.assertEqual(Topic.getTopic('Test Topic'), self.topic)
        self.assertEqual(Topic.getTopic('Test-Topic'), self.topic)


class ThreadModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.topic = Topic.objects.create(title='Test Topic')
        cls.thread = Thread.objects.create(title='Test Thread', topic=cls.topic, op=Post.objects.create())

    def testThreadSlugGeneration(self):
        thread = Thread.objects.create(title='Slug Test 1!', topic=self.topic, op=Post.objects.create())
        slug = slugify(thread.title, to_lower=True, max_length=80)
        self.assertEqual(thread.slug, slug)

    def testThreadRelativeUrl(self):
        threadPageUrl = reverse('threadPage', args=[self.thread.topic.urlTitle, self.thread.id, self.thread.slug])
        self.assertEqual(self.thread.relativeUrl, threadPageUrl)

    def testThreadDelete(self):
        thread = Thread.objects.create(title='temp thread', topic=self.topic, op=Post.objects.create())
        uid = thread.op.uid
        thread.delete()
        self.assertRaises(Thread.DoesNotExist, Thread.objects.get, title=thread.title)
        self.assertRaises(Post.DoesNotExist, Post.objects.get, uid=uid)


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create()
        cls.thread = Thread.objects.create(title='Test Thread', topic=Topic.objects.create(title='Test Topic'), op=cls.post)
        cls.replies = [Post.objects.create(parent=cls.post) for _ in range(1, 4)]

    def testGetReplies(self):
        self.assertListEqual(self.replies, list(self.post.getReplies()))

    def testGetThread(self):
        self.assertEqual(self.thread, self.post.thread)

    def testGetScore(self):
        self.post.upvotes = 2
        self.post.downvotes = 1
        self.post.save()
        self.post.refresh_from_db()
        self.assertEqual(self.post.score, 1)

    def testGetSortedRepliesByWsi(self):
        for i, p in enumerate(self.replies):
            p.upvotes = i
            p.save()
            self.replies[i].refresh_from_db()
        self.assertEqual(tuple(self.post.getSortedReplies(by_wsi=True)), tuple(reversed(self.replies)))

    def testGetSortedRepliesByDate(self):
        self.assertEqual(tuple(self.post.getSortedReplies(by_wsi=False)), tuple(self.replies))
