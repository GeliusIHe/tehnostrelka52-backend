from django.urls import re_path
from backend_auth.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/tickets/(?P<ticket_id>\d+)/$', ChatConsumer.as_asgi()),
]
