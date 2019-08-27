from django.urls import path
# from webssh.websocket import WebSSH
from webssh.websocket_layer import WebSSH, WebSSH_view, CliSSH_view
# from webtelnet.websocket import WebTelnet
from webtelnet.websocket_layer import WebTelnet

websocket_urlpatterns = [
    path('webssh/', WebSSH),
    path('webssh/view/', WebSSH_view),
    path('clissh/view/', CliSSH_view),
    path('webtelnet/', WebTelnet),
]
