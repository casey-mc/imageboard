from django import forms
from django.forms import ModelForm
from .models import Board

class PostForm(forms.Form):
    media = forms.FileField(
        label="select a file",
        help_text="max. 10 MB",
        required=False
    )
    replytext = forms.CharField(label="Text", max_length=2000)

class BoardForm(ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'title', 'description']

class BannedUserForm(forms.Form):
    ban_duration = forms.DurationField(label="ban duration", required=False)
    post_id = forms.IntegerField(label="post id", required=False)