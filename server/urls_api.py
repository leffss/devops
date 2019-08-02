from django.urls import path
from . import views_api

app_name="server"
urlpatterns = [
    path('test/', views_api.test, name='test'),
]

