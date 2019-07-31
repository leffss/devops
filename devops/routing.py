from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from websocket import routing as websocketrouting
from webssh.websocket import WebSSH
from webtelnet.websocket import WebTelnet
from django.urls import path


application = ProtocolTypeRouter(
    {
        'websocket': AuthMiddlewareStack(
            URLRouter(
                websocketrouting.websocket_urlpatterns
            )
        )
    }
)

# or like this
# application = ProtocolTypeRouter(
#     {
#         'websocket': AuthMiddlewareStack(
#             URLRouter(
#                 [
#                     path('webssh/', WebSSH),
#                     path('webtelnet/', WebTelnet),
#                 ]
#             )
#         )
#     }
# )
