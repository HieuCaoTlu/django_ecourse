from django.urls import path
from .views import *
from .tests import *

app_name = 'course'
urlpatterns = [
    path('',HomepageCourse.as_view(),name='homepage'),
    path('course/<int:course_id>', DetailCourse.as_view(), name='detail_course'),
    path('category/<int:category_id>', CategoryCourse.as_view(), name='category'),
    path('course/<int:course_id>/overview', OverviewCourse.as_view(), name='overview_course'),
    path('course/<int:course_id>/bookmark', BookmarkCourse.as_view(), name='bookmark_course'),
    path('course/<int:course_id>/certificate', CertificateCourse.as_view(), name='certificate_course'),
    path('course/<int:course_id>/<int:section_id>/<int:lesson_id>', DetailLesson.as_view(), name='detail_lesson'),
]
