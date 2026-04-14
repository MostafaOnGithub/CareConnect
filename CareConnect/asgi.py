import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import Devices.routing 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CareConnect.settings')

application = ProtocolTypeRouter({
    # Handles standard HTTP (your regular views)
    "http": get_asgi_application(),
    
    # Handles WebSockets (your SOS alarms)
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Devices.routing.websocket_urlpatterns
        )
    ),
})
