import json
import os

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.templatetags.static import static
from django.utils import timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .constants import ACCEPT_LIST
from .models import Chat, ChatThread
from .notification import MailNotification
# from .signing import loads
from .validators import FileSizeValidator


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["token"]
        self.room_group_name = f"chat-{self.room_name}".replace(":", "-")[:80]

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        self.thread = await self.get_thread(loads(self.room_name)["pk"])

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        self.chat_is_staff = self.scope["user"].is_staff
        if text_data:
            try:
                text_data_json = json.loads(text_data)
                message = text_data_json.get("message")
                file_name = text_data_json.get("file_name")

                if message:
                    # 通常のメッセージ
                    await self.send_email()
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "message": message,
                            "chat_is_staff": self.chat_is_staff,
                        },
                    )

                    await self.create_chat_message(message=message)

                elif file_name:
                    # ファイル名
                    self.file_name = file_name

            except Exception:
                pass

        else:
            # ファイルが送信されたとき
            new_file = ContentFile(bytes_data, self.file_name)
            try:
                FileExtensionValidator(ACCEPT_LIST, "このファイルの形式はサポートされておりません。")(new_file)
                FileSizeValidator(10 * 1024 * 1024, "ファイルサイズは10MB以下である必要があります。")(new_file)
            except ValidationError as e:
                await self.send(text_data=json.dumps({"error_msg": e.message}))

            await self.send_email()
            new_chat = await self.create_chat_message(src=new_file)
            url = new_chat.src.url
            extend = os.path.splitext(url)[1][1:]
            if extend not in ["jpg", "jpeg", "png"]:
                url = static("main/svg/file_error.svg")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_file",
                    "url": url,
                    "chat_is_staff": self.chat_is_staff,
                    "file_name": self.file_name,
                },
            )

    async def chat_message(self, event):
        await self.set_time_dict()
        await self.send(
            text_data=json.dumps(
                {
                    **self.time_dict,
                    "message": event["message"],
                    "chat_is_staff": event["chat_is_staff"],
                }
            )
        )

    async def chat_file(self, event):
        await self.set_time_dict()
        await self.send(
            text_data=json.dumps(
                {
                    **self.time_dict,
                    "file_url": event["url"],
                    "file_name": event["file_name"],
                    "chat_is_staff": event["chat_is_staff"],
                }
            )
        )

    async def set_time_dict(self):
        WEEK = ["月", "火", "水", "木", "金", "土", "日"]
        now = timezone.localtime(timezone.now())
        self.time_dict = {
            "date": now.strftime("%m/%d") + f"({WEEK[now.weekday()]})",
            "time": now.strftime("%H:%M"),
        }

    async def send_email(self):
        last_chat = await self.get_last_chat()
        notification = MailNotification(self.thread, self.scope, self.room_name)
        if self.scope["user"].is_staff and not last_chat.is_staff:
            await notification.from_staff_to_user()
        elif not self.scope["user"].is_staff and last_chat.is_staff:
            await notification.from_user_to_staff()

    @database_sync_to_async
    def get_last_chat(self):
        return self.thread.chat_set.order_by("id").last()

    @database_sync_to_async
    def get_thread(self, pk):
        return ChatThread.objects.get(pk=pk)

    @database_sync_to_async
    def create_chat_message(self, message=None, src=None):
        new_chat = Chat.objects.create(
            thread=self.thread,
            content=message,
            src=src,
            is_staff=self.chat_is_staff,
        )
        if src:
            return new_chat
