from django.urls import path, include
from .views import *

app_name = 'forum'
urlpatterns = [
    path('',HomepageForum.as_view(),name='homepage'),
    path('<int:post_id>', DetailPost.as_view(), name='post'),
    path('save/',makingpost,name = 'makingpost'),
    path('like/', like_post,name = 'like_post'),
]
