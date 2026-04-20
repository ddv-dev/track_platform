from django.urls import path
from .views import (
    DirectionListView, TrackListView, TrackDetailView,
    TaskSubmitView, ChecklistItemToggleView, TrackProgressView
)

urlpatterns = [
    path('directions/', DirectionListView.as_view(), name='directions'),
    path('', TrackListView.as_view(), name='tracks'),
    path('<int:id>/', TrackDetailView.as_view(), name='track-detail'),
    path('<int:track_id>/tasks/<int:task_id>/submit/', TaskSubmitView.as_view(), name='task-submit'),
    path('<int:track_id>/checklist/<int:item_id>/toggle/', ChecklistItemToggleView.as_view(), name='checklist-toggle'),
    path('<int:track_id>/progress/', TrackProgressView.as_view(), name='track-progress'),
]
