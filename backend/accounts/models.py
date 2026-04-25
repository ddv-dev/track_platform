from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Студент"),
        ("curator", "Куратор"),
        ("teacher", "Преподаватель"),
        ("admin", "Администратор"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    group = models.ForeignKey(
        "tracks.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        verbose_name="Группа",
    )
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    telegram = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="progress")
    track = models.ForeignKey("tracks.Track", on_delete=models.CASCADE)
    completed_tasks = models.ManyToManyField("tracks.Task", blank=True)
    checklist_items = models.ManyToManyField("tracks.ChecklistItem", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["user", "track"]
        verbose_name = "Прогресс пользователя"
        verbose_name_plural = "Прогресс пользователей"
