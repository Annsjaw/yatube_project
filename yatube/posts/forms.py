from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = {'text', 'group'}

        error_messages = {
            'text': {
                'required': "Нельзя ничего не написать",
            }
        }
