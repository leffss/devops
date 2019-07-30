from django.urls import path
from . import views


app_name = 'server'
urlpatterns = [
    path('', views.index, name='index'),
    path('lists/', views.lists, name='lists'),
    path('users/', views.users, name='users'),
]

