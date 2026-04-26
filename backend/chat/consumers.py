import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            # Проверяем, существует ли комната перед добавлением в группу
            room_exists = await self.room_exists()
            if not room_exists:
                await self.close()
                return
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user = self.scope["user"]

        saved_message = await self.save_message(user, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": user.username,
                "user_id": user.id,
                "created_at": saved_message["created_at"],
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "user": event["user"],
                    "user_id": event["user_id"],
                    "created_at": event["created_at"],
                }
            )
        )

    @database_sync_to_async
    def room_exists(self):
        from .models import ChatRoom
        try:
            return ChatRoom.objects.filter(id=self.room_id).exists()
        except Exception:
            return False

    @database_sync_to_async
    def save_message(self, user, message):
        from .models import ChatRoom, ChatMessage
        room = ChatRoom.objects.get(id=self.room_id)
        msg = ChatMessage.objects.create(room=room, user=user, message=message)
        return {
            "id": msg.id,
            "message": msg.message,
            "created_at": msg.created_at.isoformat(),
        }