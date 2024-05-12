from django.contrib import admin
from forum.models import *
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'display_likes']

    def display_likes(self, obj):
        return obj.num_likes
    display_likes.short_description = 'Number of Likes'

admin.site.register(Post, PostAdmin)
admin.site.register(Reply)
admin.site.register(Like)