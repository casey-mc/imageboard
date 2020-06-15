# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.dispatch import receiver
from .models import Post
from django.db.models.signals import post_save
from channels import channels


@receiver(post_save, sender=Post)
def receive(instance, **kwargs):
    print("in signal!")
    channel_layer = channels.get_channel.layer()
    group_name = self.group_name = 'thread_%d' % instance.thread
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'new_post',
            'instance': kwargs.get('instance')
        }