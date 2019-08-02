from django.urls import path
from . import views_api


app_name="user"
urlpatterns = [
    path('password/update/', views_api.password_update, name='password_update'),
    path('profile/update/', views_api.profile_update, name='profile_update'),
    path('user/update/', views_api.user_update, name='user_update'),
]
