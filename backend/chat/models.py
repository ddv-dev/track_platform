from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    track = models.ForeignKey(
        "tracks.Track", on_delete=models.CASCADE, related_name="chat_rooms"
    )
    student = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="chat_rooms",
        null=True,
        blank=True,
    )
    curator = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="curated_chats",
        null=True,
        blank=True,
    )
    is_group_chat = models.BooleanField(default=False)
    participants = models.ManyToManyField(
        "accounts.User", blank=True, related_name="group_chats"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ["track", "student", "curator", "is_group_chat"]
        verbose_name = "Чат-комната"
        verbose_name_plural = "Чат-комнаты"


class ChatMessage(models.Model):
    room = models.ForeignKey(
        ChatRoom, on_delete=models.CASCADE, related_name="messages"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чата"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.message[:50]}"
