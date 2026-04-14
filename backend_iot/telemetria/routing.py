from django.urls import re_path
from .consumers import AlertasConsumer

websocket_urlpatterns = [
    re_path(r'^ws/alertas-criticas/$', AlertasConsumer.as_asgi())
]