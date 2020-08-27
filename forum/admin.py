from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Board, Thread, Post, User, BannedUser

class BoardAdmin(admin.ModelAdmin):
    model = Board
    filter_horizontal = ('banned_users',)

admin.site.register(Board, BoardAdmin)
admin.site.register(Thread)
admin.site.register(Post)
admin.site.register(BannedUser)