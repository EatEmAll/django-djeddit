from django.contrib import admin

from .models import Topic
from .models import Post
from .models import Thread
# Register your models here.

admin.site.register(Post)
admin.site.register(Thread)
admin.site.register(Topic)
