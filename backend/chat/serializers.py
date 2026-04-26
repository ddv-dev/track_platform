from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from accounts.serializers import UserSerializer


class ChatMessageSerializer(serializers.ModelSerializer):
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = "__all__"

    def get_user_info(self, obj):
        from accounts.serializers import UserSerializer

        return UserSerializer(obj.user).data


class ChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = "__all__"
        read_only_fields = ("id", "created_at", "is_active")
        extra_kwargs = {"curator": {"required": False}}  # <-- это ключевое

    def get_last_message(self, obj):
        last_msg = obj.messages.last()
        return ChatMessageSerializer(last_msg).data if last_msg else None

    def get_unread_count(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(user=request.user).count()
        return 0


class ChatRoomDetailSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    student_info = UserSerializer(source="student", read_only=True)
    curator_info = UserSerializer(source="curator", read_only=True)

    class Meta:
        model = ChatRoom
        fields = (
            "id",
            "track",
            "student",
            "student_info",
            "curator",
            "curator_info",
            "messages",
            "created_at",
        )
