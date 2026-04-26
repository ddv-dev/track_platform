from django.urls import path
from .views import (
    DirectionListView, TrackListView, TrackDetailView,
    TrackTasksView, SubmitTaskView, ChecklistItemToggleView,
    TrackProgressView, PendingSubmissionsView, ReviewSubmissionView,
    CreateEnrollmentRequestView, CuratorEnrollmentRequestsView,
    ReviewEnrollmentRequestView, CuratorStudentsStatsView,
    TeacherTracksView, TeacherStudentsStatsView,
    TrackTaskCreateView, TrackTaskUpdateView,
)

urlpatterns = [
    path("directions/", DirectionListView.as_view(), name="directions"),
    path("", TrackListView.as_view(), name="tracks"),
    path("<int:id>/", TrackDetailView.as_view(), name="track-detail"),
    path("<int:track_id>/tasks/", TrackTasksView.as_view(), name="track-tasks"),
    path("tasks/<int:task_id>/submit/", SubmitTaskView.as_view(), name="task-submit"),
    path("<int:track_id>/checklist/<int:item_id>/toggle/", ChecklistItemToggleView.as_view(), name="checklist-toggle"),
    path("<int:track_id>/progress/", TrackProgressView.as_view(), name="track-progress"),
    path("curator/pending/", PendingSubmissionsView.as_view(), name="pending-submissions"),
    path("curator/review/<int:submission_id>/", ReviewSubmissionView.as_view(), name="review-submission"),
    path("<int:track_id>/enroll/", CreateEnrollmentRequestView.as_view(), name="enroll-request"),
    path("curator/enrollment-requests/", CuratorEnrollmentRequestsView.as_view(), name="curator-requests"),
    path("curator/enrollment-requests/<int:request_id>/review/", ReviewEnrollmentRequestView.as_view(), name="review-request"),
    path("curator/students/", CuratorStudentsStatsView.as_view(), name="curator-students"),
    path("teacher/tracks/", TeacherTracksView.as_view(), name="teacher-tracks"),
    path("teacher/stats/", TeacherStudentsStatsView.as_view(), name="teacher-stats"),
    path("<int:track_id>/tasks/create/", TrackTaskCreateView.as_view(), name="task-create"),
    path("<int:track_id>/tasks/<int:task_id>/update/", TrackTaskUpdateView.as_view(), name="task-update"),
]