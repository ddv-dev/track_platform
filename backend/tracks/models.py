from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Direction(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name='Код направления')
    name = models.CharField(max_length=200, verbose_name='Название направления')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направления'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Track(models.Model):
    direction = models.ForeignKey(Direction, on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=200, verbose_name='Название трека')
    short_description = models.TextField(verbose_name='Краткое описание')
    full_description = models.TextField(verbose_name='Полное описание')
    career_paths = models.TextField(verbose_name='Карьерные перспективы')
    skills = models.TextField(verbose_name='Навыки, которые вы получите')
    duration = models.CharField(max_length=100, blank=True, verbose_name='Длительность обучения')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    order = models.IntegerField(default=0, verbose_name='Порядок отображения')
    image = models.ImageField(upload_to='tracks/', null=True, blank=True, verbose_name='Изображение')
    
    class Meta:
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'
        ordering = ['direction', 'order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_total_tasks(self):
        return self.tasks.count()
    
    def get_completion_percentage(self, user):
        from accounts.models import UserProgress
        try:
            progress = UserProgress.objects.get(user=user, track=self)
            total = self.tasks.count()
            if total == 0:
                return 0
            return (progress.completed_tasks.count() / total) * 100
        except:
            return 0

class Guide(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='guides')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Гайд'
        verbose_name_plural = 'Гайды'
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title

class Checklist(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='checklists')
    title = models.CharField(max_length=200, verbose_name='Название чек-листа')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Чек-лист'
        verbose_name_plural = 'Чек-листы'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.track.name} - {self.title}"

class ChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE, related_name='items')
    text = models.CharField(max_length=500, verbose_name='Текст пункта')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Пункт чек-листа'
        verbose_name_plural = 'Пункты чек-листа'
        ordering = ['order']
    
    def __str__(self):
        return self.text

class Task(models.Model):
    TASK_TYPE_CHOICES = (
        ('text', 'Текстовый ответ'),
        ('single', 'Один правильный ответ'),
        ('multiple', 'Несколько правильных ответов'),
        ('code', 'Код'),
    )
    
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200, verbose_name='Название задания')
    description = models.TextField(verbose_name='Описание задания')
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='text', verbose_name='Тип задания')
    correct_answer = models.TextField(blank=True, verbose_name='Правильный ответ')
    points = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name='Баллы')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ['order']
    
    def __str__(self):
        return self.title

class TaskOption(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=500, verbose_name='Текст варианта')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный вариант')
    
    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответа'
    
    def __str__(self):
        return self.text

class UserTaskAttempt(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='task_attempts')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attempts')
    answer = models.TextField(verbose_name='Ответ пользователя')
    is_correct = models.BooleanField(default=False, verbose_name='Правильно')
    points_earned = models.IntegerField(default=0, verbose_name='Полученные баллы')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Попытка выполнения'
        verbose_name_plural = 'Попытки выполнения'
        ordering = ['-created_at']
        unique_together = ['user', 'task']  # Одна попытка на задание
    
    def __str__(self):
        return f"{self.user.username} - {self.task.title} - {'✓' if self.is_correct else '✗'}"
