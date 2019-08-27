from django.urls import path
from . import views


app_name = "webssh"
urlpatterns = [
    path('hosts/', views.hosts, name='hosts'),
    path('terminal/', views.terminal, name='terminal'),
    path('terminal/cli/', views.terminal_cli, name='terminal_cli'),
    path('terminal/view/', views.terminal_view, name='terminal_view'),
    path('terminal/clissh/view/', views.terminal_clissh_view, name='terminal_clissh_view'),
    path('logs/', views.logs, name='logs'),
    path('test/', views.test, name='test'),
    path('sessions/', views.sessions, name='sessions'),
]

