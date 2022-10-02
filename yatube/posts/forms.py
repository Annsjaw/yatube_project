from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = {'image', 'text', 'group'}

        error_messages = {
            'text': {
                'required': "Нельзя ничего не написать",
            }
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = {'text'}
