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
from .models import Chat, ChatRoom
from .notification import MailNotification
# from .signing import loads
from .validators import FileSizeValidator


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["uuid"]
        self.room_group_name = f"chat-{self.room_name}"
        await self.set_room()
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message")
            file_name = text_data_json.get("file_name")

            if message:
                # 通常のテキストメッセージ
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                    },
                )

                await self.create_chat_message(message=message)

            elif file_name:
                # ファイル名
                self.file_name = file_name


        else:
            # ファイルが送信されたとき
            new_file = ContentFile(bytes_data, self.file_name)
            try:
                FileExtensionValidator(ACCEPT_LIST, "このファイルの形式はサポートされておりません。")(new_file)
                FileSizeValidator(10 * 1024 * 1024, "ファイルサイズは10MB以下である必要があります。")(new_file)
            except ValidationError as e:
                await self.send(text_data=json.dumps({"error_msg": e.message}))

            new_chat = await self.create_chat_message(src=new_file)
            url = new_chat.src.url
            # extend = os.path.splitext(url)[1][1:]
            # if extend not in ["jpg", "jpeg", "png"]:
            #     url = static("chat/svg/file_error.svg")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_file",
                    "url": url,
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
                }
            )
        )

    async def set_time_dict(self):
        now = timezone.localtime(timezone.now())
        self.time_dict = {
            "time": now.strftime("%Y年%-m月%-d日%H:%M："),
        }


    @database_sync_to_async
    def set_room(self):
        print(self.room_name)
        self.room = ChatRoom.objects.get(pk=self.room_name)

    @database_sync_to_async
    def create_chat_message(self, message=None, src=None):
        new_chat = Chat.objects.create(
            room=self.room,
            content=message,
            src=src,
        )
        if src:
            return new_chat
