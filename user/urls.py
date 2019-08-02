from django.urls import path
from . import views


app_name="user"
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('users/', views.users, name='users'),
    path('groups/', views.groups, name='groups'),
    path('logs/', views.logs, name='logs'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('user/<int:user_id>/', views.user, name='user'),
    path('user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
]
