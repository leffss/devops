from django.urls import path
from . import views


app_name = "scheduler"
urlpatterns = [
    path('hosts/', views.hosts, name='hosts'),
    path('host/<int:host_id>/', views.host, name='host'),
    path('host/<int:host_id>/jobs/', views.jobs, name='jobs'),
]
