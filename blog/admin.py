from django.contrib import admin
from .models import Post,Comment
# Register your models here.

# admin.site.register(Post)

#Registring the Model Post in the Admin Panel
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields = ['author']
    # date_hierarchy = 'publish'
    # ordering = ['publish','status']


#Registring the Model Comment in the Admin Panel
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'email', 'body', 'created','updated','active']
    list_filter = ['post', 'name', 'email', 'created','updated','active']
    search_fields = ['post', 'name', 'email', 'body']
