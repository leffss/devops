from django.urls import path
from . import views


app_name = "webguacamole"
urlpatterns = [
    path('terminal/', views.terminal, name='terminal'),
    path('terminal/view/', views.terminal_view, name='terminal_view'),
]
