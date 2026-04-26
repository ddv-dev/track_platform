import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        logger.info(f"WebSocket connection attempt on room {self.room_id}")
        print(f"DEBUG: connect for room {self.room_id}, user={self.scope['user']}")

        if self.scope["user"].is_anonymous:
            logger.warning("User is anonymous, closing")
            await self.close()
            return

        try:
            # Проверяем, существует ли комната
            room_exists = await self.room_exists(self.room_id)
            if not room_exists:
                logger.error(f"Room {self.room_id} does not exist")
                await self.close()
                return

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info(f"WebSocket established for room {self.room_id}")
            print(f"DEBUG: WebSocket accepted for room {self.room_id}")
        except Exception as e:
            logger.exception(f"Error during connect: {e}")
            await self.close()

    async def disconnect(self, close_code):
        logger.info(f"Disconnected from room {self.room_id}, code={close_code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        logger.debug(f"Received message: {text_data}")
        try:
            data = json.loads(text_data)
            message = data.get("message")
            if not message:
                return

            user = self.scope["user"]
            saved_message = await self.save_message(self.room_id, user.id, message)
            if saved_message is None:
                logger.error("Failed to save message")
                return

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
        except Exception as e:
            logger.exception(f"Error processing message: {e}")

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user": event["user"],
            "user_id": event["user_id"],
            "created_at": event["created_at"],
        }))

    @database_sync_to_async
    def room_exists(self, room_id):
        from .models import ChatRoom
        return ChatRoom.objects.filter(id=room_id).exists()

    @database_sync_to_async
    def save_message(self, room_id, user_id, message):
        from django.contrib.auth import get_user_model
        from .models import ChatRoom, ChatMessage
        User = get_user_model()
        try:
            room = ChatRoom.objects.get(id=room_id)
            user = User.objects.get(id=user_id)
            msg = ChatMessage.objects.create(room=room, user=user, message=message)
            return {
                "id": msg.id,
                "message": msg.message,
                "created_at": msg.created_at.isoformat(),
            }
        except ChatRoom.DoesNotExist:
            logger.error(f"Room {room_id} not found")
            return None
        except Exception as e:
            logger.exception(f"Unexpected error saving message: {e}")
            return None