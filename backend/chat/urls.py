from django.urls import path
from .views import (
    ChatRoomListView,
    ChatRoomCreateView,
    ChatRoomDetailView,
    ChatMessageCreateView,
    ChatMessageMarkReadView,
    CreatePrivateChatView,
    TrackCuratorsView,
    UserSearchView,
)

urlpatterns = [
    path("rooms/", ChatRoomListView.as_view(), name="chat-rooms"),
    path("rooms/create/", ChatRoomCreateView.as_view(), name="chat-room-create"),
    path("rooms/<int:pk>/", ChatRoomDetailView.as_view(), name="chat-room-detail"),
    path(
        "rooms/<int:room_id>/messages/",
        ChatMessageCreateView.as_view(),
        name="chat-messages",
    ),
    path(
        "rooms/<int:room_id>/mark-read/",
        ChatMessageMarkReadView.as_view(),
        name="chat-mark-read",
    ),
    path("curators/", TrackCuratorsView.as_view(), name="track-curators"),
    path("users/search/", UserSearchView.as_view(), name="user-search"),
    path(
        "private/create/", CreatePrivateChatView.as_view(), name="create-private-chat"
    ),
    path("rooms/<int:pk>/", ChatRoomDetailView.as_view(), name="chat-room-detail"),
]
