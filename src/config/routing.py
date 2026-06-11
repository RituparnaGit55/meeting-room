from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.accounts.consumers import UserConsumer
from apps.meetings.consumers import MeetingConsumer
from apps.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/meetings/(?P<meeting_id>\d+)/$", MeetingConsumer.as_asgi()),
    re_path(r"ws/meetings/(?P<meeting_id>\d+)/chat/$", ChatConsumer.as_asgi()),
    re_path(r"ws/users/(?P<user_id>\d+)/$", UserConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
