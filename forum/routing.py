# forum/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # ws/thread/<thread_id>
    re_path(r'ws/thread/(?P<thread_id>\d+)/$', consumers.ThreadConsumer),
    # (?P<board_name>\w+)/
]