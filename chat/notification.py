from django.core import mail
from django.template.loader import render_to_string
from django.urls import reverse

from channels.db import database_sync_to_async


class MailNotification:
    from_email = "hp_form@demia.co.jp"

    def __init__(self, thread, scope, room_name):
        self.thread = thread
        self.scope = scope
        self.room_name = room_name
        self.headers_dict = dict(self.scope["headers"])
        self.set_params()

    def set_params(self):
        self.base_params = {
            "origin": self.headers_dict[b"origin"].decode(),
            "thread": self.thread,
        }

    @database_sync_to_async
    def from_user_to_staff(self):
        """
        user => staff のとき
        担当スタッフ（いなければinfo）にURL付きメールを送る。
        """

        params = {
            **self.base_params,
            "url": reverse("admin:main_chatthread_change", args=[self.thread.id]),
        }

        # メール内容
        message = render_to_string(
            "main/email/chat/to_staff_notification.txt",
            params,
        )

        to_email = [self.thread.staff.email] if self.thread.staff else ["info@demia.co.jp"]
        email = mail.EmailMessage(
            "【DeMiA HP】要確認｜担当分チャット通知",
            message,
            self.from_email,
            to_email,
        )

        connection = mail.get_connection()
        connection.open()
        connection.send_messages([email])
        connection.close()

    @database_sync_to_async
    def from_staff_to_user(self):
        """
        staff => user のとき
        (A) ユーザーにtoken付きメールを送る。
        (B) 担当スタッフに確認メールを送る。
        """

        # (A)のメール
        params_A = {**self.base_params, "url": reverse("main:chat", args=[self.room_name])}

        message_A = render_to_string("main/email/chat/to_user_notification.txt", params_A)
        email_A = mail.EmailMessage(
            "【DeMiA HP】チャット通知",
            message_A,
            self.from_email,
            [self.thread.email],
        )

        # (B)のメール
        params_B = {
            **self.base_params,
            "url": reverse("admin:main_chatthread_change", args=[self.thread.id]),
        }
        message_B = render_to_string("main/email/chat/to_staff_confirm.txt", params_B)

        if self.thread.staff:
            to_email = [self.thread.staff.email]
        else:
            to_email = ["info@demia.co.jp"]

        email_B = mail.EmailMessage(
            "【DeMiA HP】メール送信の確認",
            message_B,
            self.from_email,
            to_email,
        )

        connection = mail.get_connection()
        connection.open()
        connection.send_messages([email_A, email_B])
        connection.close()
