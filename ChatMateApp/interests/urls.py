from django.urls import path,include
from .views import *

urlpatterns=[
    path('send_interest/',send_interest, name='send-interest'),
    path('update-interest/<int:interest_id>/', accept_or_reject_interest, name='update-interest')
]