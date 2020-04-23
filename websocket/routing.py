from django.urls import path
from webssh.websocket_layer import WebSSH, WebSSH_view, CliSSH_view
from webtelnet.websocket_layer import WebTelnet
from webguacamole.websocket_layer import WebGuacamole, WebGuacamole_view
from batch.websocket_layer import Cmd, Script, File, Playbook, Module

websocket_urlpatterns = [
    path('ws/webssh/', WebSSH),
    path('ws/webssh/view/', WebSSH_view),
    path('ws/clissh/view/', CliSSH_view),
    path('ws/webtelnet/', WebTelnet),
    path('ws/webguacamole/', WebGuacamole),
    path('ws/webguacamole/view', WebGuacamole_view),
    path('ws/cmd/', Cmd),
    path('ws/script/', Script),
    path('ws/file/', File),
    path('ws/playbook/', Playbook),
    path('ws/module/', Module),
]
