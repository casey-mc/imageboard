from django.db import models
from django.contrib.auth import get_user_model
from datetime import date, datetime
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.urls import reverse



#for signals
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from channels.layers import get_channel_layer


def thread_path(instance, filename):
    return '{0}/{1}'.format(instance.thread.id,filename)

    
class Board(models.Model):
    #TODO: Name should be case insensitive
    name = models.CharField(max_length=25, unique=True, validators=[
        RegexValidator(
            regex='^[a-zA-Z]+$',
            message="Board name must use alphabetical characters.",
            code="Invalid Board name"
        ),
    ])
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="board_moderators", blank=True)
    #When using the following relation, query through BannedUsers
    #Otherwise, it doesn't use the BannedUsersManager and filter out expired bans.
    banned_users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='BannedUsers', related_name="board_banned_users", blank=True)
    #Descriptive attributes, could add CSS, sidebar HTML, and stuff like that
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

# TODO: If a custom RelatedManager is possible, maybe you could get Board.banned_users
# to use this for joins (to exlude expired bans) https://docs.djangoproject.com/en/3.0/ref/models/relations/
class BannedUsersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(ban_expiry__gt=timezone.now())


class BannedUsers(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    ban_expiry = models.DateTimeField()
    objects = BannedUsersManager()

#TODO max length of title and text should maybe be customizable by the board owner
#Or not, reddit might not actually do that.
class Thread(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=300)
    text = models.CharField(max_length=40000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # media = models.FileField(upload_to=thread_path, null=True)

    def post_count(self):
        return self.post_set.count()

    def last_five_posts(self):
        last_five_posts = self.post_set.order_by('created_at')[:5]
        return last_five_posts

    def get_json(self):
        return {
            'id': self.id,
            'text': self.text,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            # 'media': self.media.url if self.media != None else None,
            'user': {
                'id': self.user.id,
                'username': self.user.username
                },
            'posts': [post.get_json() for post in self.post_set.all()]
        }



#Might need a seperate field for emoji responses or something, or generic options maybe.  
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    thread = models.ForeignKey('Thread', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    media = models.FileField(upload_to=thread_path, blank=True, null=True)

    def __str__(self):
        return self.user.username + ": " + self.text

    def get_json(self):
        return {
            'id': self.id,
            'text': self.text,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'media': self.media.url if self.media else None,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                # It's kind of awkward to put urls in here, but the alternative is to create them with js on the page.
                # Either you have the waste of doing these for each post server-side (which you would have anyway)
                # Or you have the wonkiness of splicing urls with js
                'addModeratorUrl': reverse('forum:add-moderator', args=(self.thread.board.name,self.user.id,)),
                'deletePostUrl': reverse('forum:delete-post', args=(self.thread.board.name, self.thread.id, self.id,)),
                'banUserUrl': reverse('forum:board-ban-user', args=(self.thread.board.name, self.user.id,)),
                }
        }






# When a new post is saved, this finds the appropriate group and sends new posts to it.
# Posts are saved via POST in views.py to avoid sending images over websockets
# May change image upload to a CDN, in which case this will change too.
@receiver(post_save, sender=Post)
def receive(instance, **kwargs):
    channel_layer = get_channel_layer()
    group_name = 'thread_%d' % instance.thread.id
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'new_post',
            'post': instance.get_json()
        }
    )

@receiver(post_delete, sender=Post)
def receive_delete(instance, **kwargs):
    channel_layer = get_channel_layer()
    group_name = 'thread_%d' % instance.thread.id
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'deleted_post',
            'post': instance.get_json()
        }
    )