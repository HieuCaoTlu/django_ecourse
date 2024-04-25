from django.urls import path, include
from .views import *

app_name = 'teacher'
urlpatterns = [
    path('',HomepageTeacher.as_view(),name='homepage'),
    path('create/', CourseCreate.as_view(), name='create_course'),
    path('update/<int:pk>/', CourseUpdate.as_view(), name='update_course'),
    path('update/lesson/<int:pk>/', SectionUpdate.as_view(), name='update_section'),
]
