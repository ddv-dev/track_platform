from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Track, Direction, Task, UserTaskAttempt, ChecklistItem
from .serializers import (
    DirectionSerializer, TrackListSerializer, TrackDetailSerializer,
    TaskSerializer, TaskSubmitSerializer
)
from accounts.models import UserProgress

class DirectionListView(generics.ListAPIView):
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer
    permission_classes = (permissions.AllowAny,)

class TrackListView(generics.ListAPIView):
    serializer_class = TrackListSerializer
    permission_classes = (permissions.AllowAny,)
    filterset_fields = ['direction']
    
    def get_queryset(self):
        queryset = Track.objects.filter(is_active=True)
        direction_id = self.request.query_params.get('direction')
        search = self.request.query_params.get('search')
        
        if direction_id:
            queryset = queryset.filter(direction_id=direction_id)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(short_description__icontains=search)
            )
        return queryset

class TrackDetailView(generics.RetrieveAPIView):
    queryset = Track.objects.filter(is_active=True)
    serializer_class = TrackDetailSerializer
    permission_classes = (permissions.AllowAny,)
    lookup_field = 'id'

class TaskSubmitView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TaskSubmitSerializer
    
    def post(self, request, track_id, task_id):
        task = get_object_or_404(Task, id=task_id, track_id=track_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        answer = serializer.validated_data['answer']
        is_correct = False
        
        # Проверка ответа в зависимости от типа задания
        if task.task_type == 'single':
            try:
                option = task.options.get(id=int(answer), is_correct=True)
                is_correct = True
            except:
                is_correct = False
        elif task.task_type == 'text':
            is_correct = answer.lower().strip() == task.correct_answer.lower().strip()
        elif task.task_type == 'code':
            # Простая проверка кода (можно расширить)
            is_correct = answer.strip() == task.correct_answer.strip()
        
        # Сохраняем попытку
        attempt, created = UserTaskAttempt.objects.update_or_create(
            user=request.user,
            task=task,
            defaults={
                'answer': answer,
                'is_correct': is_correct,
                'points_earned': task.points if is_correct else 0
            }
        )
        
        # Обновляем прогресс пользователя
        if is_correct:
            progress, _ = UserProgress.objects.get_or_create(
                user=request.user,
                track=task.track
            )
            if task not in progress.completed_tasks.all():
                progress.completed_tasks.add(task)
        
        return Response({
            'is_correct': is_correct,
            'points_earned': attempt.points_earned,
            'message': 'Правильно!' if is_correct else 'Неправильно. Попробуйте еще раз.'
        })

class ChecklistItemToggleView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, track_id, item_id):
        item = get_object_or_404(ChecklistItem, id=item_id, checklist__track_id=track_id)
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            track_id=track_id
        )
        
        if item in progress.checklist_items.all():
            progress.checklist_items.remove(item)
            checked = False
        else:
            progress.checklist_items.add(item)
            checked = True
        
        return Response({'checked': checked})

class TrackProgressView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, track_id):
        track = get_object_or_404(Track, id=track_id)
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            track=track
        )
        
        total_tasks = track.tasks.count()
        completed_tasks = progress.completed_tasks.count()
        
        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'percentage': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'completed_task_ids': list(progress.completed_tasks.values_list('id', flat=True)),
            'completed_checklist_ids': list(progress.checklist_items.values_list('id', flat=True))
        })
