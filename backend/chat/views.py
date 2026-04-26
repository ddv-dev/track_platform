from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from accounts.serializers import UserSerializer
from accounts.models import User
from .models import ChatRoom, ChatMessage
from .serializers import (
    ChatRoomSerializer,
    ChatRoomDetailSerializer,
    ChatMessageSerializer,
)
from tracks.models import Track


class CreatePrivateChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        other_user_id = request.data.get("user_id")
        if not other_user_id:
            return Response({"error": "user_id required"}, status=400)
        other_user = get_object_or_404(User, id=other_user_id)

        # Определяем, кто студент, кто преподаватель (или куратор)
        student = None
        mentor = None  # может быть curator или teacher
        if request.user.role == "student" and other_user.role in ("teacher", "curator"):
            student = request.user
            mentor = other_user
        elif (
            request.user.role in ("teacher", "curator") and other_user.role == "student"
        ):
            student = other_user
            mentor = request.user
        else:
            return Response(
                {
                    "error": "Чат может быть создан только между студентом и преподавателем/куратором"
                },
                status=400,
            )

        # Создаём или получаем существующий чат
        chat_room, created = ChatRoom.objects.get_or_create(
            student=student,
            curator=mentor,  # используем поле curator для преподавателя/куратора
            is_group_chat=False,
            defaults={"track": None},  # можно указать track, если нужно
        )
        serializer = ChatRoomSerializer(chat_room)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role == "curator":
            qs = ChatRoom.objects.filter(curator=user, is_active=True)
        elif user.role == "student":
            qs = ChatRoom.objects.filter(student=user, is_active=True)
        elif user.role == "teacher":
            # Преподаватели видят групповые чаты своих треков
            qs = ChatRoom.objects.filter(
                is_group_chat=True, track__teachers=user, is_active=True
            )
        else:
            qs = ChatRoom.objects.none()
        return qs.select_related("student", "curator", "track")


class ChatRoomCreateView(generics.CreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        track_id = request.data.get("track")
        track = get_object_or_404(Track, id=track_id)

        # Находим куратора (первого с ролью curator, либо админа)
        curator = User.objects.filter(role="curator").first()
        if not curator:
            curator = User.objects.filter(is_superuser=True).first()
        if not curator:
            return Response(
                {"error": "Нет доступного куратора"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Создаём или получаем существующую комнату
        room, created = ChatRoom.objects.get_or_create(
            track=track, student=request.user, defaults={"curator": curator}
        )

        # Если комната уже существовала, просто возвращаем её
        serializer = self.get_serializer(room)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
        )


class ChatRoomDetailView(generics.RetrieveAPIView):
    serializer_class = ChatRoomDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role == "curator":
            return ChatRoom.objects.filter(curator=user)
        return ChatRoom.objects.filter(student=user)


class ChatMessageCreateView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        room_id = self.kwargs["room_id"]
        room = get_object_or_404(ChatRoom, id=room_id)
        serializer.save(user=self.request.user, room=room)


class ChatMessageMarkReadView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = room.messages.filter(is_read=False).exclude(user=request.user)
        messages.update(is_read=True)
        return Response({"status": "ok"})


class TrackCuratorsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "student" or not request.user.group:
            return Response([])
        track = request.user.group.track
        curators = track.curators.all()
        serializer = UserSerializer(curators, many=True)
        return Response(serializer.data)


class UserSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        role = request.query_params.get("role")
        query = request.query_params.get("q", "")
        track_id = request.query_params.get("track")

        users = User.objects.all()
        if role:
            users = users.filter(role=role)
        if query:
            users = users.filter(
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
            )
        if track_id:
            # Фильтр по треку (например, для преподавателей, привязанных к треку студента)
            users = users.filter(tracks_as_teacher__id=track_id)

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
