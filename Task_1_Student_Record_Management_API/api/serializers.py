from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'email', 'date_of_birth', 'enrollment_date', 'phone',
            'address', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_student_id(self, value):
        if self.instance and self.instance.student_id == value:
            return value
        if Student.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("A student with this ID already exists.")
        return value

    def validate_email(self, value):
        if self.instance and self.instance.email == value:
            return value
        if Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        return value
