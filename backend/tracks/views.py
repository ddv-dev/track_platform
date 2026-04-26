from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import (
    Direction,
    Track,
    Task,
    UserTaskAttempt,
    ChecklistItem,
    PracticalSubmission,
    EnrollmentRequest,
    Group,
)
from .serializers import (
    DirectionSerializer,
    TrackListSerializer,
    TrackDetailSerializer,
    TaskSerializer,
    TaskSubmitSerializer,
    PracticalSubmissionSerializer,
    EnrollmentRequestSerializer,
)
from accounts.models import UserProgress, User
from chat.models import ChatRoom, ChatMessage


# ========== Направления и треки ==========
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


# ========== Задания и прогресс ==========
class TrackTasksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, track_id):
        track = get_object_or_404(Track, id=track_id)
        tasks = list(track.tasks.all().order_by("order"))
        completed_auto = set(
            UserTaskAttempt.objects.filter(
                user=request.user, is_correct=True
            ).values_list("task_id", flat=True)
        )
        completed_practice = set(
            PracticalSubmission.objects.filter(
                user=request.user, status="approved"
            ).values_list("task_id", flat=True)
        )
        completed_ids = completed_auto | completed_practice

        theory_tasks = [t for t in tasks if t.category == "theory"]
        practice_tasks = [t for t in tasks if t.category == "practice"]

        locked_map = {}
        need_unlock_theory = True
        for task in theory_tasks:
            locked_map[task.id] = not need_unlock_theory
            if task.id not in completed_ids:
                need_unlock_theory = False
        need_unlock_practice = True
        for task in practice_tasks:
            locked_map[task.id] = not need_unlock_practice
            if task.id not in completed_ids:
                need_unlock_practice = False

        result = []
        for task in tasks:
            serializer = TaskSerializer(task, context={"request": request})
            data = serializer.data
            data["completed"] = task.id in completed_ids
            data["locked"] = locked_map.get(task.id, False)
            result.append(data)
        return Response(result)


class SubmitTaskView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, task_id):
        task = get_object_or_404(Task, id=task_id)
        answer = request.data.get("answer")
        if not answer:
            return Response({"error": "Ответ не предоставлен"}, status=400)

        # Проверка блокировки
        prev_tasks = Task.objects.filter(
            track=task.track, order__lt=task.order
        ).order_by("order")
        for prev in prev_tasks:
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
            except ValueError:
                return False
        elif task.task_type == "multiple":
            # answer приходит как строка с ID через запятую
            selected = [
                int(x.strip()) for x in answer.split(",") if x.strip().isdigit()
            ]
            correct = set(
                task.options.filter(is_correct=True).values_list("id", flat=True)
            )
            return set(selected) == correct
        else:
            return answer.strip().lower() == task.correct_answer.strip().lower()


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
        total = track.tasks.count()
        completed = progress.completed_tasks.count()
        return Response(
            {
                "total_tasks": total,
                "completed_tasks": completed,
                "percentage": round(completed / total * 100, 1) if total > 0 else 0,
                "completed_task_ids": list(
                    progress.completed_tasks.values_list("id", flat=True)
                ),
                "completed_checklist_ids": list(
                    progress.checklist_items.values_list("id", flat=True)
                ),
            }
        )


# ========== Заявки на зачисление ==========
class CreateEnrollmentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, track_id):
        if request.user.role != "student":
            return Response(
                {"error": "Только студенты могут подавать заявки"}, status=400
            )
        if request.user.group is not None:
            return Response({"error": "Вы уже зачислены на трек"}, status=400)

        track = get_object_or_404(Track, id=track_id)
        if EnrollmentRequest.objects.filter(
            student=request.user, track=track, status="pending"
        ).exists():
            return Response(
                {"error": "У вас уже есть активная заявка на этот трек"}, status=400
            )

        enrollment = EnrollmentRequest.objects.create(student=request.user, track=track)
        serializer = EnrollmentRequestSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CuratorEnrollmentRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "curator":
            return Response({"error": "Доступ только кураторам"}, status=403)
        requests = EnrollmentRequest.objects.filter(
            track__curator=request.user, status="pending"
        )
        serializer = EnrollmentRequestSerializer(requests, many=True)
        return Response(serializer.data)


class ReviewEnrollmentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        if request.user.role != "curator":
            return Response({"error": "Доступ только кураторам"}, status=403)
        req = get_object_or_404(EnrollmentRequest, id=request_id)
        if req.track.curator != request.user:
            return Response({"error": "Вы не куратор этого трека"}, status=403)

        action = request.data.get("action")
        if action not in ("accept", "reject"):
            return Response(
                {"error": "Действие должно быть accept или reject"}, status=400
            )

        if action == "accept":
            with transaction.atomic():
                req.status = "accepted"
                group, _ = Group.objects.get_or_create(
                    track=req.track,
                    defaults={
                        "name": f"Группа {req.track.name}",
                        "curator": request.user,
                    },
                )
                student = req.student
                student.group = group
                student.save()
                UserProgress.objects.get_or_create(user=student, track=req.track)

                # Создание группового чата
                group_chat, created = ChatRoom.objects.get_or_create(
                    track=req.track,
                    is_group_chat=True,
                    defaults={"title": req.track.name},
                )
                group_chat.participants.add(request.user)
                group_chat.participants.add(student)
                if created:
                    ChatMessage.objects.create(
                        room=group_chat,
                        user=request.user,
                        message=f"Добро пожаловать в групповой чат трека «{req.track.name}»!",
                    )
                # Личный чат студент-куратор
                private_chat, _ = ChatRoom.objects.get_or_create(
                    track=req.track,
                    student=student,
                    curator=request.user,
                    is_group_chat=False,
                )
                if private_chat.messages.count() == 0:
                    ChatMessage.objects.create(
                        room=private_chat,
                        user=request.user,
                        message=f"Здравствуйте, {student.first_name}! Я куратор. Если будут вопросы – пишите.",
                    )
        else:
            req.status = "rejected"

        req.reviewed_by = request.user
        req.save()
        return Response({"status": req.status})


# ========== Статистика куратора ==========
class CuratorStudentsStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "curator":
            return Response({"error": "Доступ только кураторам"}, status=403)
        tracks = Track.objects.filter(curator=request.user)
        result = []
        for track in tracks:
            group = Group.objects.filter(track=track).first()
            if not group:
                continue
            for student in group.students.all():
                progress = UserProgress.objects.filter(
                    user=student, track=track
                ).first()
                total = track.tasks.count()
                completed = progress.completed_tasks.count() if progress else 0
                result.append(
                    {
                        "student_id": student.id,
                        "name": student.get_full_name(),
                        "track": track.name,
                        "total_tasks": total,
                        "completed_tasks": completed,
                        "percentage": round(completed / total * 100, 1) if total else 0,
                    }
                )
        return Response(result)


# ========== Проверка практических заданий (куратор/преподаватель) ==========
class PendingSubmissionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role not in ("curator", "teacher"):
            return Response(
                {"error": "Доступ только кураторам и преподавателям"}, status=403
            )
        # Для куратора – задания своих треков, для преподавателя – привязанных треков
        if request.user.role == "curator":
            submissions = PracticalSubmission.objects.filter(
                status="pending", task__track__curator=request.user
            )
        else:  # teacher
            submissions = PracticalSubmission.objects.filter(
                status="pending", task__track__teachers=request.user
            )
        submissions = submissions.select_related("task", "user")
        serializer = PracticalSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class ReviewSubmissionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, submission_id):
        submission = get_object_or_404(PracticalSubmission, id=submission_id)
        # Проверка прав: куратор проверяет задания своих треков, преподаватель – своих
        if request.user.role == "curator":
            if submission.task.track.curator != request.user:
                return Response({"error": "Вы не куратор этого трека"}, status=403)
        elif request.user.role == "teacher":
            if not submission.task.track.teachers.filter(id=request.user.id).exists():
                return Response({"error": "Вы не привязаны к этому треку"}, status=403)
        else:
            return Response({"error": "Недостаточно прав"}, status=403)

        action = request.data.get("action")
        feedback = request.data.get("feedback", "")
        if action not in ("approve", "reject"):
            return Response(
                {"error": "Действие должно быть approve или reject"}, status=400
            )

        if action == "approve":
            submission.status = "approved"
            progress, _ = UserProgress.objects.get_or_create(
                user=submission.user, track=submission.task.track
            )
            progress.completed_tasks.add(submission.task)
        else:
            submission.status = "rejected"

        submission.feedback = feedback
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.save()
        return Response({"status": submission.status})


# ========== Преподавательские эндпоинты ==========
class TeacherTracksView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "teacher":
            return Response({"error": "Доступ только преподавателям"}, status=403)
        tracks = request.user.tracks_as_teacher.all()
        serializer = TrackListSerializer(tracks, many=True)
        return Response(serializer.data)


class TeacherStudentsStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "teacher":
            return Response({"error": "Доступ только преподавателям"}, status=403)
        tracks = request.user.tracks_as_teacher.all()
        result = []
        for track in tracks:
            group = Group.objects.filter(track=track).first()
            if not group:
                continue
            for student in group.students.all():
                progress = UserProgress.objects.filter(
                    user=student, track=track
                ).first()
                total = track.tasks.count()
                completed = progress.completed_tasks.count() if progress else 0
                result.append(
                    {
                        "student_id": student.id,
                        "name": student.get_full_name(),
                        "track": track.name,
                        "total_tasks": total,
                        "completed_tasks": completed,
                        "percentage": round(completed / total * 100, 1) if total else 0,
                    }
                )
        return Response(result)


class TrackTaskCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, track_id):
        track = get_object_or_404(Track, id=track_id)
        if request.user.role not in ("teacher", "curator"):
            return Response({"error": "Недостаточно прав"}, status=403)
        if request.user.role == "curator" and track.curator != request.user:
            return Response({"error": "Вы не куратор этого трека"}, status=403)
        if (
            request.user.role == "teacher"
            and not track.teachers.filter(id=request.user.id).exists()
        ):
            return Response({"error": "Вы не привязаны к этому треку"}, status=403)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(track=track)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class TrackTaskUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, track_id, task_id):
        track = get_object_or_404(Track, id=track_id)
        if request.user.role not in ("teacher", "curator"):
            return Response({"error": "Недостаточно прав"}, status=403)
        if request.user.role == "curator" and track.curator != request.user:
            return Response({"error": "Вы не куратор этого трека"}, status=403)
        if (
            request.user.role == "teacher"
            and not track.teachers.filter(id=request.user.id).exists()
        ):
            return Response({"error": "Вы не привязаны к этому треку"}, status=403)

        task = get_object_or_404(Task, id=task_id, track=track)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
