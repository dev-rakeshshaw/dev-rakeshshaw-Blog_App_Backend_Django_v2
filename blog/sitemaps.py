from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Post.objects.filter(status=Post.Status.PUBLISHED).all()

    def lastmod(self, obj):
        return obj.updated
    
    # Specify the method to use for generating URLs
    def location(self, obj):
        return obj.get_absolute_url_for_urls_post_details()