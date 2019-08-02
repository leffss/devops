from django.urls import path
from . import views

app_name="server"
urlpatterns = [
    path('', views.index, name='index'),
    path('hosts/', views.hosts, name='hosts'),
    path('users/', views.users, name='users'),
]

