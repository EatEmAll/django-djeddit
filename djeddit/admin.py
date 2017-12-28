from django.contrib import admin

from .models import Topic
from .models import Post
from .models import Thread
# Register your models here.

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'locked')
    readonly_fields = ('views', 'topic', 'op')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ('content', 'modified_on')
    readonly_fields = ('created_by',
                       'created_on',
                       '_upvotes',
                       '_downvotes',
                       'wsi',
                       'parent',
                       'ip_address',
                       'user_agent')

admin.site.register(Topic)
