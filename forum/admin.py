from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Board, Thread, Post, User

admin.site.register(Board)
admin.site.register(Thread)
admin.site.register(Post)