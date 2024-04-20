from django.urls import path, include
from .views import *

app_name = 'teacher'
urlpatterns = [
    path('',HomepageTeacher.as_view(),name='homepage'),
    
]
