from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import UserSerializer


def build_token_pair(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def build_auth_payload(message, user):
    return {
        "message": message,
        "user": UserSerializer(user).data,
        "tokens": build_token_pair(user),
    }


def auth_response(message, user, status_code):
    return Response(build_auth_payload(message, user), status=status_code)
