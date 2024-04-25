from django.urls import path
from .views import *

app_name = 'payment'
urlpatterns = [
    path("<int:course_id>", Payment.as_view(),name='payment'),
    path("payment_return/<int:course_id>", PaymentReturn.as_view(), name='payment_return')
]