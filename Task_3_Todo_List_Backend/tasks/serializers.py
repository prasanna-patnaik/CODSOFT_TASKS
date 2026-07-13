from rest_framework import serializers

from tasks.models import Task
from tasks.validators import validate_due_date_not_past, validate_not_blank


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
        return validate_not_blank(
            value,
            "Task title cannot be empty.",
            exception_class=serializers.ValidationError,
        )

    def validate_category(self, value):
        return value.strip() if value else value

    def validate_due_date(self, value):
        return validate_due_date_not_past(
            value,
            exception_class=serializers.ValidationError,
        )
