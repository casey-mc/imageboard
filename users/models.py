from django.contrib.auth.models import AbstractUser
from django.db import models


# Custom User Class
class User(AbstractUser):
    screen_name = models.CharField(max_length=50)