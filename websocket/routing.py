from django.urls import path
from webssh.websocket import WebSSH
from webtelnet.websocket import WebTelnet

websocket_urlpatterns = [
    path('webssh/', WebSSH),
    path('webtelnet/', WebTelnet),
]
