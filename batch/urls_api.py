from django.urls import path
from . import views_api


app_name = "batch"
urlpatterns = [
    path('get/hosts/', views_api.get_hosts, name='get_hosts'),
    path('upload/', views_api.upload, name='upload'),
    path('logs/', views_api.logs, name='logs'),
]
