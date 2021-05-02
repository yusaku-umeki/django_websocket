import uuid

from django.db import models


class ChatRoom(models.Model):
    """
    チャットルームのモデル
    同一のルームにいるクライアントとリアルタイムチャットが可能
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("ルーム名", max_length=50)
    created_at = models.DateTimeField("開設日時", auto_now_add=True)

    class Meta:
        verbose_name = "チャットルーム"
        verbose_name_plural = "チャットルーム"


class Chat(models.Model):
    """
    各チャットルーム内で行われるチャットのモデル
    """

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    content = models.TextField("内容", blank=True, null=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    src = models.FileField(
        "添付ファイル",
        blank=True,
        null=True,
        upload_to="chat/%Y/%m/%d/",
    )

    class Meta:
        verbose_name = "チャットルーム"
        verbose_name_plural = "チャットルーム"
