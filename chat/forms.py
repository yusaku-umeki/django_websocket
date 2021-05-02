from django import forms

from .models import Chat, ChatRoom


class ChatRoomForm(forms.Form):
    name = forms.CharField(max_length=50)
