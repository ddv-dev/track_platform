from rest_framework import serializers
from .models import (
    Direction,
    Track,
    Guide,
    Checklist,
    ChecklistItem,
    Task,
    TaskOption,
    UserTaskAttempt,
    PracticalSubmission,
)


class DirectionSerializer(serializers.ModelSerializer):
    tracks_count = serializers.SerializerMethodField()

    class Meta:
        model = Direction
        fields = ("id", "code", "name", "description", "tracks_count")

    def get_tracks_count(self, obj):
        return obj.tracks.filter(is_active=True).count()


class TrackListSerializer(serializers.ModelSerializer):
    direction_name = serializers.CharField(source="direction.name", read_only=True)

    class Meta:
        model = Track
        fields = (
            "id",
            "name",
            "short_description",
            "direction",
            "direction_name",
            "duration",
            "image",
            "order",
        )


class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ("id", "text", "order")


class ChecklistSerializer(serializers.ModelSerializer):
    items = ChecklistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Checklist
        fields = ("id", "title", "order", "items")


class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = ("id", "title", "content", "order", "created_at")


class TaskOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskOption
        fields = ("id", "text")


class TaskSerializer(serializers.ModelSerializer):
    options = TaskOptionSerializer(many=True, read_only=True)
    user_attempt = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "task_type",
            "category",
            "points",
            "order",
            "options",
            "user_attempt",
        )

    def get_user_attempt(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            try:
                attempt = UserTaskAttempt.objects.get(user=request.user, task=obj)
                return {
                    "is_correct": attempt.is_correct,
                    "points_earned": attempt.points_earned,
                    "answer": attempt.answer,
                }
            except UserTaskAttempt.DoesNotExist:
                return None
        return None


class TaskSubmitSerializer(serializers.Serializer):
    answer = serializers.CharField(required=True)


class TrackDetailSerializer(serializers.ModelSerializer):
    direction = DirectionSerializer(read_only=True)
    guides = GuideSerializer(many=True, read_only=True)
    checklists = ChecklistSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = (
            "id",
            "name",
            "direction",
            "short_description",
            "full_description",
            "career_paths",
            "skills",
            "duration",
            "image",
            "guides",
            "checklists",
            "tasks",
        )


class PracticalSubmissionSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source="task.title", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = PracticalSubmission
        fields = "__all__"
        read_only_fields = ("user", "submitted_at", "reviewed_at")
