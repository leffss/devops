from django.urls import path
from . import views_api


app_name = "webssh"
urlpatterns = [
    path('session/close/', views_api.session_close, name='session_close'),
]

