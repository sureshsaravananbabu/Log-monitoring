from django.urls import re_path

from . import consumer

websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/$', consumer.MonitorConsumer.as_asgi()),
]