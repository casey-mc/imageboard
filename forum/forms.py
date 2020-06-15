from django import forms

class PostForm(forms.Form):
    media = forms.FileField(
        label="select a file",
        help_text="max. 10 MB",
        required=False
    )
    replytext = forms.CharField(label="Text", max_length=2000)
