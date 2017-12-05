from django.contrib.sitemaps import Sitemap

from .models import Thread

class ThreadSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Thread.objects.all()

    def lastmod(self, obj):
        return obj.op.modified_on
