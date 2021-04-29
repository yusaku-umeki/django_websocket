from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "main"
urlpatterns = [
    path("contact", views.ContactView.as_view(), name="contact"),
    path("chat/inbox/<token>", views.ThreadInboxView.as_view(), name="chat_inbox"),
    path("chat/<token>", views.ChatView.as_view(), name="chat"),
]
