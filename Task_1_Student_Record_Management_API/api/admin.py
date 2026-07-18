from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'email', 'enrollment_date', 'is_active')
    list_display_links = ('student_id', 'first_name', 'last_name')
    list_filter = ('is_active', 'enrollment_date')
    search_fields = ('student_id', 'first_name', 'last_name', 'email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
