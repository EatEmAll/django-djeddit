import uuid
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


# Create your models here.

def gen_uuid():
    return uuid.uuid4()


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


class Topic(NamedModel):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z ]*$', 'Only alphanumeric characters are allowed.')
    title = models.CharField(max_length=20, blank=False, unique=True, validators=[alphanumeric])
    description = models.CharField(max_length=120, blank=True, default='')

    def getThreadCount(self):
        return Thread.objects.filter(topic=self).count()

    def getUrlTitle(self):
        return self.title.replace(' ', '_')

    @staticmethod
    def getTopic(title):
        try:
            return Topic.objects.get(title=title)
        except Topic.DoesNotExist:
            return Topic.objects.get(title=title.replace('_', ' '))


class Thread(NamedModel):
    title = models.CharField(max_length=70, blank=False)
    url = models.URLField(max_length=120, blank=True, default='')
    views = models.IntegerField(blank=True, default=0)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    op = models.ForeignKey('Post', related_name='+', on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        try:
            self.op.delete()
        except Post.DoesNotExist:
            pass
        super(Thread, self).delete(*args, **kwargs)


class Post(MPTTModel, NamedModel):
    content = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='+')
    created_on = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_on = models.DateTimeField(auto_now_add=False, auto_now=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    score = models.IntegerField(blank=True, default=0)
    uid = models.UUIDField(max_length=8, primary_key=True, default=gen_uuid, editable=False)

    class MPTTMetta:
        order_insertion_by = ['created_on']

    def getReplies(self):
        replies = Post.objects.filter(parent=self.uid)
        for reply in replies:
            replies |= reply.getReplies()
        return replies

    def getThread(self):
        post = self
        while post.parent:
            post = post.parent
        return Thread.objects.get(op=post)


class UserPostVote(NamedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+')
    post = models.ForeignKey(Post, related_name='+')
    val = IntegerRangeField(blank=True, default=0, min_value=-1, max_value=1)
