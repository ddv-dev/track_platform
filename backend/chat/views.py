from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import ChatRoom, ChatMessage
from .serializers import ChatRoomSerializer, ChatRoomDetailSerializer, ChatMessageSerializer
from tracks.models import Track

class ChatRoomListView(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'curator':
            return ChatRoom.objects.filter(curator=user, is_active=True)
        return ChatRoom.objects.filter(student=user, is_active=True)

class ChatRoomCreateView(generics.CreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def perform_create(self, serializer):
        track_id = self.request.data.get('track')
        track = get_object_or_404(Track, id=track_id)
        serializer.save(
            student=self.request.user,
            track=track,
            curator=None  # Будет назначен администратором
        )

class ChatRoomDetailView(generics.RetrieveAPIView):
    serializer_class = ChatRoomDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'curator':
            return ChatRoom.objects.filter(curator=user)
        return ChatRoom.objects.filter(student=user)

class ChatMessageCreateView(generics.CreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        room = get_object_or_404(ChatRoom, id=room_id)
        serializer.save(user=self.request.user, room=room)

class ChatMessageMarkReadView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        messages = room.messages.filter(is_read=False).exclude(user=request.user)
        messages.update(is_read=True)
        return Response({'status': 'ok'})
