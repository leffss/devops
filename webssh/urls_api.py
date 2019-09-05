from django.urls import path
from . import views_api


app_name = "webssh"
urlpatterns = [
    path('session/close/', views_api.session_close, name='session_close'),
    path('session/lock/', views_api.session_lock, name='session_lock'),
    path('session/unlock/', views_api.session_unlock, name='session_unlock'),
    path('session/rdp/close/', views_api.session_rdp_close, name='session_rdp_close'),
    path('session/clissh/close/', views_api.session_clissh_close, name='session_clissh_close'),
    path('session/clissh/lock/', views_api.session_clissh_lock, name='session_clissh_lock'),
    path('session/clissh/unlock/', views_api.session_clissh_unlock, name='session_clissh_unlock'),
]

