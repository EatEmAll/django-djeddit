# Core django imports
from django.conf import settings
from django import VERSION as DJANGO_VERSION
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import RegexValidator
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
if DJANGO_VERSION[:2] < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

# Third party imports
from mptt.models import MPTTModel, TreeForeignKey
from slugify import slugify
from ipware.ip import get_ip

# Our app imports
from djeddit.utils.utility_funcs import gen_uuid, wsi_confidence


class IntegerRangeField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        models.IntegerField.__init__(self, verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super(IntegerRangeField, self).formfield(**defaults)


class NamedModel(models.Model):
    class Meta:
        abstract = True

    def getName(self):
        return self.__class__.__name__


@python_2_unicode_compatible
class Topic(NamedModel):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z ]*$', 'Only alphanumeric characters are allowed.')
    title = models.CharField(max_length=20, blank=False, unique=True, validators=[alphanumeric])
    description = models.CharField(max_length=120, blank=True, default='')

    def __str__(self):
        return self.title

    def getThreadCount(self):
        return Thread.objects.filter(topic=self).count()

    @property
    def urlTitle(self):
        return self.title.replace(' ', '-')

    def get_absolute_url(self):
        return reverse('topicPage', args=[self.urlTitle])

    @staticmethod
    def getTopic(title):
        try:
            return Topic.objects.get(title=title)
        except ObjectDoesNotExist:
            try:
                return Topic.objects.get(title=title.replace('-', ' '))
            except ObjectDoesNotExist:
                return Topic.objects.get(title=title.replace('_', ' '))


@python_2_unicode_compatible
class Thread(NamedModel):
    title = models.CharField(max_length=70, blank=False)
    slug = models.SlugField(unique=False, null=True)
    url = models.URLField(max_length=120, blank=True, default='')
    views = models.IntegerField(blank=True, default=0)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    op = models.ForeignKey('Post', related_name='+', on_delete=models.CASCADE)
    locked = models.BooleanField(blank=True, default=False)
    is_stickied = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = self._genSlug()
        super(Thread, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            self.op.delete()
        except Post.DoesNotExist:
            pass
        super(Thread, self).delete(*args, **kwargs)

    def _genSlug(self):
        slug = slugify(self.title, to_lower=True, max_length=80)
        return slug

    @property
    def relativeUrl(self):
        return reverse('threadPage', args=[self.topic.urlTitle, self.id, self.slug])

    def get_absolute_url(self):
        return self.relativeUrl


@python_2_unicode_compatible
class Post(MPTTModel, NamedModel):
    uid = models.UUIDField(max_length=8, primary_key=True, default=gen_uuid, editable=False)
    content = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='+')
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_on = models.DateTimeField(auto_now_add=False, auto_now=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    _upvotes = models.IntegerField(blank=True, default=0)
    _downvotes = models.IntegerField(blank=True, default=0)
    wsi = models.FloatField(blank=True, default=0) # Wilson score interval
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=150, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        Post.upvotes = property(lambda self: self._upvotes, Post._voteSetterWrapper('_upvotes'))
        Post.downvotes = property(lambda self: self._downvotes, Post._voteSetterWrapper('_downvotes'))

    class MPTTMetta:
        order_insertion_by = ['created_on']

    def __str__(self):
        return self.content[:70]

    @staticmethod
    def _voteSetterWrapper(attr):
        def voteSetter(self, value):
            setattr(self, attr, max(0, value))
            self.wsi = wsi_confidence(self._upvotes, self._downvotes)
        return voteSetter

    @property
    def thread(self): # TODO: thread should be stored in Post
        post = self
        while post.parent:
            post = post.parent
        return Thread.objects.get(op=post)

    @property
    def score(self):
        return self.upvotes - self.downvotes

    def getReplies(self, excluded=()):
        """:param excluded: exclude all posts with these uids and their descendants"""
        replies = Post.objects.filter(parent=self.uid).exclude(uid__in=excluded)
        for reply in replies:
            replies |= reply.getReplies(excluded=excluded)
        return replies

    def getSortedReplies(self, limit=50, by_wsi=True, excluded=()):
        """
        :param limit: number of replies to return
        :param by_wsi: sort replies by wsi score or by creation date
        :param excluded: uids or excluded replies
        """
        excluded = list(excluded)
        order_field = '-wsi' if by_wsi else 'created_on'
        replies = list(self.getReplies(excluded=excluded).order_by(order_field)[:limit])
        self._getPostsWithChildren(replies)
        sorted_replies = []
        for p in replies:
            sorted_replies.append(p)
            sorted_replies += p.getChildrenList()
        return sorted_replies

    def _getPostsWithChildren(self, replies):
        for p in list(replies):
            if not hasattr(p, 'included_children'):
                p.included_children = []
            if p.parent != self:
                if p.parent not in replies:
                    # add missing parents
                    current_p = p
                    while True:
                        current_p.parent._addToIncludedChildren(current_p)
                        current_p = current_p.parent
                        if current_p in (replies + [self]):
                            break
                    if current_p in replies:
                        replies[replies.index(current_p)] = current_p
                else:
                    p.parent = replies[replies.index(p.parent)]
                    p.parent._addToIncludedChildren(p)
                replies.remove(p)

    def _addToIncludedChildren(self, post):
        if not hasattr(self, 'included_children'):
            self.included_children = [post]
        else:
            self.included_children.append(post)

    def getChildrenList(self):
        children = []
        for p in self.included_children:
            children.append(p)
            if p.included_children:
                children += p.getChildrenList()
        return children

    def setMeta(self, request):
        """update post ip_address & user_agent attributes"""
        ip = get_ip(request)
        if ip is not None:
            self.ip_address = ip
        ua = request.META.get('HTTP_USER_AGENT', '')
        if ua:
            self.user_agent = ua


class UserPostVote(NamedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    post = models.ForeignKey(Post, related_name='+', on_delete=models.CASCADE)
    val = IntegerRangeField(blank=True, default=0, min_value=-1, max_value=1)
