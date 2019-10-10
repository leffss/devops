from django.urls import path
from . import views


app_name = "tasks"
urlpatterns = [
    path('test/', views.test_api, name='test_api'),
]

