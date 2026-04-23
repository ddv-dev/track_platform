from django.contrib import admin
from django.utils.html import format_html
from .models import Direction, Track, Guide, Checklist, ChecklistItem, Task, TaskOption


class ChecklistItemInline(admin.TabularInline):
    model = ChecklistItem
    extra = 1


class TaskOptionInline(admin.TabularInline):
    model = TaskOption
    extra = 2


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "direction", "is_active", "order", "duration")
    list_filter = ("direction", "is_active")
    search_fields = ("name", "short_description")
    list_editable = ("order", "is_active")
    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "direction",
                    "name",
                    "short_description",
                    "full_description",
                    "image",
                )
            },
        ),
        ("Профессиональное развитие", {"fields": ("career_paths", "skills")}),
        ("Дополнительно", {"fields": ("duration", "is_active", "order")}),
    )


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ("title", "track", "order", "created_at")
    list_filter = ("track",)
    search_fields = ("title", "content")
    list_editable = ("order",)


@admin.register(Checklist)
class ChecklistAdmin(admin.ModelAdmin):
    list_display = ("title", "track", "order")
    list_filter = ("track",)
    inlines = [ChecklistItemInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "track", "task_type", "points", "order")
    list_filter = ("track", "task_type")
    search_fields = ("title", "description")
    list_editable = ("points", "order")
    inlines = [TaskOptionInline]


@admin.register(TaskOption)
class TaskOptionAdmin(admin.ModelAdmin):
    list_display = ("text", "task", "is_correct")
    list_filter = ("is_correct", "task__track")
