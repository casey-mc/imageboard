# Generated by Django 3.0.6 on 2020-07-27 03:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum', '0002_auto_20200723_1229'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannedUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ban_expiry', models.DateTimeField()),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='forum.Board')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='board',
            name='banned_users',
            field=models.ManyToManyField(blank=True, related_name='board_banned_users', through='forum.BannedUsers', to=settings.AUTH_USER_MODEL),
        ),
    ]
