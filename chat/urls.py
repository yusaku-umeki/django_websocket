from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.ChatRoomFormView.as_view(), name="chat_room_form"),
    path("chat_room/<uuid:pk>", views.ChatRoomDetailView.as_view(), name="chat_room"),
    # path("chat/inbox/<token>", views.ThreadInboxView.as_view(), name="chat_inbox"),
    # path("chat/get_thread_by_token", views.get_thread_by_token, name="get_thread_by_token"),
    # path("chat/get_not_read_count", views.GetNotReadCount.as_view(), name="get_not_read_count"),
    # path("chat/put_read_count/<token>", views.PutReadCount.as_view(), name="put_read_count"),
    # path(
    #     "chat/check_thread_password/<token>",
    #     views.CheckThreadPassword.as_view(),
    #     name="check_thread_password",
    # ),
    # path(
    #     "chat/reset_password_email_sent/<token>",
    #     views.reset_password_email_sent,
    #     name="reset_password_email_sent",
    # ),
    # path("chat/reset_password/<token>", views.ResetPasswordView.as_view(), name="reset_password"),
    # path(
    #     "chat/reset_password_complete",
    #     views.reset_password_complete,
    #     name="reset_password_complete",
    # ),
    # path("chat/<token>", views.ChatView.as_view(), name="chat"),
]
