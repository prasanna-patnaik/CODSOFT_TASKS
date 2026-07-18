from django.db import models
from django.core.validators import EmailValidator, RegexValidator


class Student(models.Model):
    student_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique student identifier (e.g., STU-2024-001)"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()],
    )
    date_of_birth = models.DateField()
    enrollment_date = models.DateField()
    phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        validators=[
            RegexValidator(
                regex=r'^\+?[\d\s\-()]*$',
                message='Enter a valid phone number.'
            )
        ]
    )
    address = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'student'
        verbose_name_plural = 'students'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
