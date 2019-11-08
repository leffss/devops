from django.urls import path
from . import views_api


app_name = "user"
urlpatterns = [
    path('password/update/', views_api.password_update, name='password_update'),
    path('profile/update/', views_api.profile_update, name='profile_update'),
    path('user/update/', views_api.user_update, name='user_update'),
    path('user/delete/', views_api.user_delete, name='user_delete'),
    path('user/add/', views_api.user_add, name='user_add'),
    path('group/update/', views_api.group_update, name='group_update'),
    path('group/delete/', views_api.group_delete, name='group_delete'),
    path('group/add/', views_api.group_add, name='group_add'),
    path('logs/', views_api.logs, name='logs'),
]
