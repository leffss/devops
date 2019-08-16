from django.urls import path
from . import views


app_name = "webssh"
urlpatterns = [
    path('hosts/', views.hosts, name='hosts'),
    path('terminal/', views.terminal, name='terminal'),
    path('terminal/view/', views.terminal_view, name='terminal_view'),
    path('logs/', views.logs, name='logs'),
    path('sessions/', views.sessions, name='sessions'),
]

