# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.dispatch import receiver
from .models import Post
from django.db.models.signals import post_save

class ThreadConsumer(WebsocketConsumer):
    def connect(self):
        self.thread_id = self.scope['url_route']['kwargs']['thread_id']
        self.group_name = 'thread_%s' % self.thread_id

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave thread group
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def new_post(self, event):
        # Send post to WebSocket
        self.send(text_data=json.dumps({
            'post': event
        }))

    def deleted_post(self, event):
        self.send(text_data=json.dumps({
            'post': event
        }))