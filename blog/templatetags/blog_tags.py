from django import template
from ..models import Post
from django.db.models import Count


register = template.Library()

#A simple tag will processes the given data and returns a string
@register.simple_tag
def total_posts():
    return Post.objects.filter(status=Post.Status.PUBLISHED).count()


#A inclusion tag will process the given data and returns a rendered template.
@register.inclusion_tag("blog/post/latest_posts.html")
def show_latest_posts(count=5):
    latest_posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by("-publish")[:count]
    return {"latest_posts" : latest_posts}


@register.simple_tag
def get_most_commented_posts(limit=5):
    return Post.objects.filter(status=Post.Status.PUBLISHED).annotate(
               total_comments=Count('comments')
           ).order_by('-total_comments')[:limit]