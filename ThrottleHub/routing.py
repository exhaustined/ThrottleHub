from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('message/<int:id>/', consumers.ChatConsumer.as_asgi()),
]