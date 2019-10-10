from django.urls import path
# from webssh.websocket import WebSSH
from webssh.websocket_layer import WebSSH, WebSSH_view, CliSSH_view
# from webtelnet.websocket import WebTelnet
from webtelnet.websocket_layer import WebTelnet
from webguacamole.websocket_layer import WebGuacamole
from batch.websocket_layer import Cmd

websocket_urlpatterns = [
    path('webssh/', WebSSH),
    path('webssh/view/', WebSSH_view),
    path('clissh/view/', CliSSH_view),
    path('webtelnet/', WebTelnet),
    path('webguacamole/', WebGuacamole),
    path('cmd/', Cmd),
]

