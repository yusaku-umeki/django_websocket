from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path("ws/chat_room/<uuid>", consumers.ChatConsumer.as_asgi()),
]
