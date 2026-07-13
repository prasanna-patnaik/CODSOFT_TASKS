from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    category = models.CharField(max_length=100, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks")

    class Meta:
        ordering = ["completed", "due_date", "-created_at"]
        indexes = [
            models.Index(fields=["owner", "completed"]),
            models.Index(fields=["owner", "priority"]),
            models.Index(fields=["owner", "due_date"]),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if not self.title or not self.title.strip():
            raise ValidationError({"title": "Task title cannot be empty."})

        if self.due_date and self.due_date < timezone.now():
            raise ValidationError({"due_date": "Due date cannot be in the past."})
