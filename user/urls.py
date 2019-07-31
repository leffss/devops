from django.urls import path
from . import views


app_name = 'user'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('lists/', views.lists, name='lists'),
    path('groups/', views.groups, name='groups'),
    path('logs/', views.logs, name='logs'),
    path('changepasswd/', views.change_passwd, name='changepasswd'),
    path('userinfo/', views.user_info, name='userinfo'),
]

