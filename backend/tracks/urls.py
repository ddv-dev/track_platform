from django.urls import path
from .views import (
    DirectionListView,
    PendingSubmissionsView,
    ReviewSubmissionView,
    SubmitTaskView,
    TrackListView,
    TrackDetailView,
    TaskSubmitView,
    ChecklistItemToggleView,
    TrackProgressView,
    TrackTasksView,
)

urlpatterns = [
    path("directions/", DirectionListView.as_view(), name="directions"),
    path("", TrackListView.as_view(), name="tracks"),
    path("<int:id>/", TrackDetailView.as_view(), name="track-detail"),
    path("<int:track_id>/tasks/", TrackTasksView.as_view(), name="track-tasks"),
    path("tasks/<int:task_id>/submit/", SubmitTaskView.as_view(), name="task-submit"),
    path(
        "<int:track_id>/checklist/<int:item_id>/toggle/",
        ChecklistItemToggleView.as_view(),
        name="checklist-toggle",
    ),
    path(
        "<int:track_id>/progress/", TrackProgressView.as_view(), name="track-progress"
    ),
    path(
        "curator/pending/", PendingSubmissionsView.as_view(), name="pending-submissions"
    ),
    path(
        "curator/review/<int:submission_id>/",
        ReviewSubmissionView.as_view(),
        name="review-submission",
    ),
]
