from django.urls import path,include
from users.views import *

urlpatterns = [
    path('auth/', include('django.contrib.auth.urls')),
    path('home/',home),
    path('login/',login_user),
    path('logout/',logout_user),
    path('register/',register_user),
    path('refresh/',token_refresh),
    path('forgot_password/',forgot_password),
    path('change_password/',change_password),
    path('verify_otp/',verify_otp),
    path('reset_password/',reset_password),
    path('get_all_users/',get_all_users),
    path('edit_profile/',edit_profile),
    path('delete_user/',delete_user),
    path('update_user/',update_user),
    path('upload_profile_picture/',upload_profile_picture)
]