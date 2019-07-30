from django.urls import path
from .websocket import WebSSH

websocket_urlpatterns = [
    path('webssh/', WebSSH),
]
