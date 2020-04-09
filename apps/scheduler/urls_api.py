from django.urls import path
from . import views_api


app_name = "scheduler"
urlpatterns = [
    path('client/upload/', views_api.client_upload, name='client_upload'),
]
