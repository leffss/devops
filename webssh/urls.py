from django.urls import path
from . import views


app_name = 'webssh'
urlpatterns = [
    path('lists/', views.lists, name='lists'),
    path('terminal/', views.terminal, name='terminal'),
    path('logs/', views.logs, name='logs'),
]

