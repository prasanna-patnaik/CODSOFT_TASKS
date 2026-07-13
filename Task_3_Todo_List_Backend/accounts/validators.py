from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


User = get_user_model()


def normalize_unique_email(email):
    normalized_email = User.objects.normalize_email(email)
    if User.objects.filter(email__iexact=normalized_email).exists():
        raise serializers.ValidationError("A user with this email already exists.")
    return normalized_email


def validate_password_confirmation(password, password_confirm):
    if password != password_confirm:
        raise serializers.ValidationError({"password_confirm": "Passwords do not match."})


def validate_user_password(password, user):
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError({"password": list(exc.messages)}) from exc
