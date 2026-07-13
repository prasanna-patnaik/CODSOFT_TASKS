from django.utils import timezone
from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "completed",
            "priority",
            "category",
            "due_date",
            "created_at",
            "updated_at",
            "owner",
        )
        read_only_fields = ("id", "created_at", "updated_at", "owner")

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Task title cannot be empty.")
        return value.strip()

    def validate_category(self, value):
        return value.strip() if value else value

    def validate_due_date(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
