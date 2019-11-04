from django.urls import path
from . import views


app_name = "webtelnet"
urlpatterns = [
    path('terminal/', views.terminal, name='terminal'),
]
