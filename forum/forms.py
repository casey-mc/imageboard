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

# class BoardForm(forms.Form):
#     name = forms.CharField(label="Name", max_length=25)
#     title = forms.CharField(label="Title", max_length=60)
#     description = forms.CharField(label="Description", max_length=500)

class BoardForm(ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'title', 'description']