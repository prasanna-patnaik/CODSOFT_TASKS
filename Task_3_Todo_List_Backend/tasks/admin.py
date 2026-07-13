from django.contrib import admin

from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "priority", "category", "completed", "due_date", "created_at")
    list_filter = ("completed", "priority", "category", "created_at", "due_date")
    search_fields = ("title", "description", "category", "owner__username", "owner__email")
    ordering = ("completed", "due_date", "-created_at")
    readonly_fields = ("created_at", "updated_at")
