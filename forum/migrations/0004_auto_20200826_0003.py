# Generated by Django 3.0.6 on 2020-08-26 06:03

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0003_auto_20200726_2114'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BannedUsers',
            new_name='BannedUser',
        ),
    ]
