import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack  # 🔥 IMPORTANTE
from telemetria.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_iot.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    # 🔥 ESTE BLOQUE ES LA CLAVE
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})