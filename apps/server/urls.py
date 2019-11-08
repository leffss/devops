from django.urls import path
from . import views

app_name = "server"
urlpatterns = [
    path('', views.index, name='index'),
    path('hosts/', views.hosts, name='hosts'),
    path('host/<int:host_id>/', views.host, name='host'),
    path('host/<int:host_id>/edit/', views.host_edit, name='host_edit'),
    path('host/add/', views.host_add, name='host_add'),

    path('users/', views.users, name='users'),
    path('user/<int:user_id>/', views.user, name='user'),
    path('user/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('user/add/', views.user_add, name='user_add'),

    path('groups/', views.groups, name='groups'),
    path('group/<int:group_id>/', views.group, name='group'),
    path('group/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('group/add/', views.group_add, name='group_add'),

]
