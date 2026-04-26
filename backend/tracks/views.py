from django.utils import timezone

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
from chat.models import ChatRoom


class PendingSubmissionsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "curator":
            return Response({"error": "Доступ только кураторам"}, status=403)
        # Используем ManyToMany связь curators
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
        tasks = list(track.tasks.all().order_by("order"))

        # Выполненные задания (авто + принятые практики)
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

        # Разделяем по категориям
        theory_tasks = [t for t in tasks if t.category == "theory"]
        practice_tasks = [t for t in tasks if t.category == "practice"]

        # Словарь: task.id -> locked
        locked_map = {}

        # Теория
        theory_completed_so_far = True  # первое всегда открыто
        for task in theory_tasks:
            is_completed = task.id in completed_ids
            locked_map[task.id] = not theory_completed_so_far
            if not is_completed:
                theory_completed_so_far = False

        # Практика
        practice_completed_so_far = True
        for task in practice_tasks:
            is_completed = task.id in completed_ids
            locked_map[task.id] = not practice_completed_so_far
            if not is_completed:
                practice_completed_so_far = False

        # Формируем ответ
        result = []
        for task in tasks:
            serializer = TaskSerializer(task, context={"request": request})
            task_data = serializer.data
            task_data["completed"] = task.id in completed_ids
            task_data["locked"] = locked_map.get(task.id, False)
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


class CreateEnrollmentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, track_id):
        track = get_object_or_404(Track, id=track_id)
        if request.user.role != "student":
            return Response(
                {"error": "Только студенты могут подавать заявки"}, status=400
            )
        if EnrollmentRequest.objects.filter(
            student=request.user, track=track, status="pending"
        ).exists():
            return Response({"error": "У вас уже есть активная заявка"}, status=400)
        if request.user.group and request.user.group.track == track:
            return Response({"error": "Вы уже зачислены на этот трек"}, status=400)

        enrollment = EnrollmentRequest.objects.create(student=request.user, track=track)
        return Response(
            EnrollmentRequestSerializer(enrollment).data, status=status.HTTP_201_CREATED
        )


class CuratorEnrollmentRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "curator":
            return Response({"error": "Доступ только для кураторов"}, status=403)
        # Заявки на треки, где этот куратор состоит
        requests = EnrollmentRequest.objects.filter(
            track__curator=request.user, status="pending"
        )

        serializer = EnrollmentRequestSerializer(requests, many=True)
        return Response(serializer.data)


class ReviewEnrollmentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        # Только куратор может обрабатывать заявки
        if request.user.role != "curator":
            return Response(
                {"error": "Доступ только кураторам"}, status=status.HTTP_403_FORBIDDEN
            )

        enrollment = get_object_or_404(EnrollmentRequest, id=request_id)
        track = enrollment.track

        # Проверка: текущий пользователь – куратор этого трека
        # Если поле curator в Track – ForeignKey (рекомендуется)
        if track.curator != request.user:
            return Response(
                {"error": "Вы не куратор этого трека"}, status=status.HTTP_403_FORBIDDEN
            )

        action = request.data.get("action")
        if action not in ("accept", "reject"):
            return Response(
                {"error": "Действие должно быть accept или reject"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "accept":
            enrollment.status = "accepted"

            # 1. Создаём или получаем группу для трека
            group, _ = Group.objects.get_or_create(
                track=track,
                defaults={"name": f"Группа {track.name}", "curator": request.user},
            )

            # 2. Зачисляем студента в группу
            student = enrollment.student
            student.group = group
            student.save()

            # 3. Создаём или получаем групповой чат трека
            group_chat, created = ChatRoom.objects.get_or_create(
                track=track, is_group_chat=True, defaults={"title": track.name}
            )

            # 4. Добавляем студента и куратора в участники
            group_chat.participants.add(student)
            if request.user not in group_chat.participants.all():
                group_chat.participants.add(request.user)

            # 5. Приветственное сообщение (только при создании чата)
            if created:
                ChatMessage.objects.create(
                    room=group_chat,
                    user=request.user,
                    message=f'Добро пожаловать в групповой чат трека "{track.name}"! Здесь можно обсуждать учебные вопросы.',
                )

            # 6. Создаём прогресс студента по треку
            UserProgress.objects.get_or_create(user=student, track=track)

        else:  # reject
            enrollment.status = "rejected"

        enrollment.reviewed_by = request.user
        enrollment.save()
        return Response({"status": enrollment.status})


class CuratorStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "curator":
            return Response({"error": "Доступ только для кураторов"}, status=403)
        # Получаем все треки, где куратор состоит
        tracks = request.user.tracks_as_curator.all()
        students_data = []
        for track in tracks:
            group = Group.objects.filter(track=track).first()
            if group:
                students = group.students.all()
                for student in students:
                    progress = UserProgress.objects.filter(
                        user=student, track=track
                    ).first()
                    total_tasks = track.tasks.count()
                    completed_tasks = (
                        progress.completed_tasks.count() if progress else 0
                    )
                    students_data.append(
                        {
                            "student_id": student.id,
                            "name": student.get_full_name(),
                            "track": track.name,
                            "total_tasks": total_tasks,
                            "completed_tasks": completed_tasks,
                            "percentage": (
                                round(
                                    completed_tasks / total_tasks * 100,
                                    1,
                                )
                                if total_tasks
                                else 0
                            ),
                        }
                    )
        return Response(students_data)


class CuratorStudentsStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != "curator":
            return Response({"error": "Доступ только для кураторов"}, status=403)

        if request.user.role == "curator":
            tracks = request.user.tracks_as_curator.all()
        else:  # teacher
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
                total_tasks = track.tasks.count()
                completed = progress.completed_tasks.count() if progress else 0
                result.append(
                    {
                        "student_id": student.id,
                        "name": student.get_full_name(),
                        "track": track.name,
                        "total_tasks": total_tasks,
                        "completed_tasks": completed,
                        "percentage": (
                            round(completed / total_tasks * 100, 1)
                            if total_tasks
                            else 0
                        ),
                    }
                )
        return Response(result)


class TrackTaskUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, track_id, task_id):
        track = get_object_or_404(Track, id=track_id)
        if request.user.role not in ("teacher", "curator"):
            return Response({"error": "Недостаточно прав"}, status=403)
        if (
            request.user not in track.teachers.all()
            and request.user not in track.curator
        ):
            return Response({"error": "Вы не привязаны к этому треку"}, status=403)

        task = get_object_or_404(Task, id=task_id, track=track)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


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
        # проверка прав: учитель или куратор, связанный с треком
        if request.user.role not in ("teacher", "curator"):
            return Response({"error": "Недостаточно прав"}, status=403)
        if (
            request.user not in track.teachers.all()
            and request.user not in track.curator
        ):
            return Response({"error": "Вы не привязаны к этому треку"}, status=403)

        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(track=track)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
