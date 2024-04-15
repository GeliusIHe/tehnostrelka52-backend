import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import backend_auth.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            backend_auth.routing.websocket_urlpatterns
        )
    ),
})
