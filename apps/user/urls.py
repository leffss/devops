from django.urls import path
from . import views


app_name = "user"
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('lockscreen/', views.lockscreen, name='lockscreen'),
    path('users/', views.users, name='users'),
    path('groups/', views.groups, name='groups'),
    path('logs/', views.logs, name='logs'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('user/<int:user_id>/', views.user, name='user'),
    path('user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('user/add/', views.user_add, name='user_add'),
    
    path('group/<int:group_id>/', views.group, name='group'),
    path('group/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('group/add/', views.group_add, name='group_add'),
    
]
