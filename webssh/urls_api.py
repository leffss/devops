from django.urls import path
from . import views_api


app_name = "webssh"
urlpatterns = [
    path('session/close/', views_api.session_close, name='session_close'),
    path('session/clissh/close/', views_api.session_clissh_close, name='session_clissh_close'),
]

