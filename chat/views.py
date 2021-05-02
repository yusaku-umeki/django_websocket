from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.urls import reverse_lazy

from .models import ChatRoom
from .forms import ChatRoomForm

class ChatRoomFormView(FormView):
    template_name = "chat/chatroom_form.html"
    form_class = ChatRoomForm

    def form_valid(self, form):
        room, is_created = ChatRoom.objects.get_or_create(name=form.cleaned_data["name"])
        self.success_url = reverse_lazy("chat_room",args=[room.id])
        return super().form_valid(form)

class ChatRoomDetailView(DetailView):
    model = ChatRoom
