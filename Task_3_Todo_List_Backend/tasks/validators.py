from django.utils import timezone


def validate_not_blank(value, message, exception_class=ValueError):
    if not value or not value.strip():
        raise exception_class(message)
    return value.strip()


def validate_due_date_not_past(value, exception_class=ValueError):
    if value and value < timezone.now():
        raise exception_class("Due date cannot be in the past.")
    return value
