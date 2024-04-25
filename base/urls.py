from django.urls import path
from .views import *

app_name = 'base'
urlpatterns = [
    path('login',Login.as_view(),name='login'),
    path('logout',Logout.as_view(),name='logout'),
    path('role',ChooseRole.as_view(),name='role'),
    path('register/<str:role_type>',Register.as_view(),name='register'),
    path('personal',Personal.as_view(),name='personal'),
]
