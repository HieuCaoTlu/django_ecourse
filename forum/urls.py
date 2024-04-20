from django.urls import path, include
from .views import *

app_name = 'forum'
urlpatterns = [
    path('',HomepageForum.as_view(),name='homepage'),
]
