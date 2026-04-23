from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProgress


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "group")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {"fields": ("role", "avatar", "group", "phone", "telegram")},
        ),
    )


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "track", "updated_at")
    list_filter = ("track",)
