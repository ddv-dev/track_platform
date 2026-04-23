from datetime import timezone

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import (
    Track,
    Direction,
    Task,
    UserTaskAttempt,
    ChecklistItem,
    PracticalSubmission,
)
from .serializers import (
    DirectionSerializer,
    TrackListSerializer,
    TrackDetailSerializer,
    TaskSerializer,
    TaskSubmitSerializer,
    PracticalSubmissionSerializer,
)
from accounts.models import UserProgress


from tracks.models import PracticalSubmission


class PendingSubmissionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "curator":
            return Response({"error": "Доступ только кураторам"}, status=403)
        # Задания, где куратор закреплён за треком (нужно добавить связь)
        # Пока упростим – все pending для треков, где куратор закреплён
        submissions = PracticalSubmission.objects.filter(
            status="pending", task__track__curator=request.user
        )
        serializer = PracticalSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class ReviewSubmissionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, submission_id):
        if request.user.role != "curator":
            return Response({"error": "Доступ только кураторам"}, status=403)
        submission = get_object_or_404(PracticalSubmission, id=submission_id)
        action = request.data.get("action")  # 'approve' или 'reject'
        feedback = request.data.get("feedback", "")
        if action == "approve":
            submission.status = "approved"
            # Добавляем задание в прогресс пользователя
            progress, _ = UserProgress.objects.get_or_create(
                user=submission.user, track=submission.task.track
            )
            progress.completed_tasks.add(submission.task)
        elif action == "reject":
            submission.status = "rejected"
        else:
            return Response({"error": "Неверное действие"}, status=400)
        submission.feedback = feedback
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.save()
        return Response({"status": submission.status})


class TrackTasksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, track_id):
        track = get_object_or_404(Track, id=track_id)
        tasks = track.tasks.all().order_by("order")
        completed_task_ids = set()
        for task in tasks:
            if task.is_auto_check:
                if UserTaskAttempt.objects.filter(
                    user=request.user, task=task, is_correct=True
                ).exists():
                    completed_task_ids.add(task.id)
            else:
                if PracticalSubmission.objects.filter(
                    user=request.user, task=task, status="approved"
                ).exists():
                    completed_task_ids.add(task.id)
        result = []
        next_unlocked = True
        for task in tasks:
            is_completed = task.id in completed_task_ids
            is_locked = not next_unlocked
            if not is_completed:
                next_unlocked = False
            serializer = TaskSerializer(task, context={"request": request})
            task_data = serializer.data
            task_data["completed"] = is_completed
            task_data["locked"] = is_locked
            result.append(task_data)
        return Response(result)


class SubmitTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        answer = request.data.get("answer")
        if not answer:
            return Response({"error": "Ответ не предоставлен"}, status=400)

        # Проверка блокировки: предыдущие задания должны быть выполнены
        previous_tasks = Task.objects.filter(
            track=task.track, order__lt=task.order
        ).order_by("order")
        for prev in previous_tasks:
            if prev.is_auto_check:
                if not UserTaskAttempt.objects.filter(
                    user=request.user, task=prev, is_correct=True
                ).exists():
                    return Response(
                        {"error": "Выполните предыдущие задания"}, status=403
                    )
            else:
                if not PracticalSubmission.objects.filter(
                    user=request.user, task=prev, status="approved"
                ).exists():
                    return Response(
                        {"error": "Выполните предыдущие задания"}, status=403
                    )

        if task.is_auto_check:
            # Автопроверка
            is_correct = self.check_answer(task, answer)
            attempt, _ = UserTaskAttempt.objects.update_or_create(
                user=request.user,
                task=task,
                defaults={
                    "answer": answer,
                    "is_correct": is_correct,
                    "points_earned": task.points if is_correct else 0,
                },
            )
            if is_correct:
                progress, _ = UserProgress.objects.get_or_create(
                    user=request.user, track=task.track
                )
                progress.completed_tasks.add(task)
            return Response({"status": "completed", "is_correct": is_correct})
        else:
            submission, _ = PracticalSubmission.objects.update_or_create(
                user=request.user,
                task=task,
                defaults={"answer": answer, "status": "pending"},
            )
            return Response(
                {"status": "pending", "message": "Ответ отправлен на проверку"}
            )

    def check_answer(self, task, answer):
        if task.task_type == "single":
            try:
                opt_id = int(answer)
                return task.options.filter(id=opt_id, is_correct=True).exists()
            except:
                return False
        elif task.task_type == "multiple":
            selected = [int(x) for x in answer.split(",") if x.strip().isdigit()]
            correct = set(
                task.options.filter(is_correct=True).values_list("id", flat=True)
            )
            return set(selected) == correct
        else:
            return answer.strip().lower() == task.correct_answer.strip().lower()


class DirectionListView(generics.ListAPIView):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer
    permission_classes = (permissions.AllowAny,)


class TrackListView(generics.ListAPIView):
    serializer_class = TrackListSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_fields = ["direction"]

    def get_queryset(self):
        queryset = Track.objects.filter(is_active=True)
        direction_id = self.request.query_params.get("direction")
        search = self.request.query_params.get("search")

        if direction_id:
            queryset = queryset.filter(direction_id=direction_id)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(short_description__icontains=search)
            )
        return queryset


class TrackDetailView(generics.RetrieveAPIView):
    queryset = Track.objects.filter(is_active=True)
    serializer_class = TrackDetailSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = "id"


class TaskSubmitView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaskSubmitSerializer

    def post(self, request, track_id, task_id):
        task = get_object_or_404(Task, id=task_id, track_id=track_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answer = serializer.validated_data["answer"]
        is_correct = False

        # Проверка ответа в зависимости от типа задания
        if task.task_type == "single":
            try:
                option = task.options.get(id=int(answer), is_correct=True)
                is_correct = True
            except:
                is_correct = False
        elif task.task_type == "text":
            is_correct = answer.lower().strip() == task.correct_answer.lower().strip()
        elif task.task_type == "code":
            # Простая проверка кода (можно расширить)
            is_correct = answer.strip() == task.correct_answer.strip()

        # Сохраняем попытку
        attempt, created = UserTaskAttempt.objects.update_or_create(
            user=request.user,
            task=task,
            defaults={
                "answer": answer,
                "is_correct": is_correct,
                "points_earned": task.points if is_correct else 0,
            },
        )

        # Обновляем прогресс пользователя
        if is_correct:
            progress, _ = UserProgress.objects.get_or_create(
                user=request.user, track=task.track
            )
            if task not in progress.completed_tasks.all():
                progress.completed_tasks.add(task)

        return Response(
            {
                "is_correct": is_correct,
                "points_earned": attempt.points_earned,
                "message": (
                    "Правильно!" if is_correct else "Неправильно. Попробуйте еще раз."
                ),
            }
        )


class ChecklistItemToggleView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, track_id, item_id):
        item = get_object_or_404(
            ChecklistItem, id=item_id, checklist__track_id=track_id
        )
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user, track_id=track_id
        )

        if item in progress.checklist_items.all():
            progress.checklist_items.remove(item)
            checked = False
        else:
            progress.checklist_items.add(item)
            checked = True

        return Response({"checked": checked})


class TrackProgressView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, track_id):
        track = get_object_or_404(Track, id=track_id)
        progress, _ = UserProgress.objects.get_or_create(user=request.user, track=track)

        total_tasks = track.tasks.count()
        completed_tasks = progress.completed_tasks.count()

        return Response(
            {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "percentage": (
                    (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
                ),
                "completed_task_ids": list(
                    progress.completed_tasks.values_list("id", flat=True)
                ),
                "completed_checklist_ids": list(
                    progress.checklist_items.values_list("id", flat=True)
                ),
            }
        )
