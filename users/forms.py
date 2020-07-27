from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):

    class Meta(CustomUserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('screen_name',)