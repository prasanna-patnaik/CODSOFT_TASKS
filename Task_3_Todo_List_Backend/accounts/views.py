from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from accounts.serializers import (
    AuthResponseSerializer,
    DocumentedTokenRefreshSerializer,
    LoginSerializer,
    LogoutSerializer,
    MessageResponseSerializer,
    RegistrationSerializer,
    TokenRefreshResponseSerializer,
    UserSerializer,
)
from accounts.utils import auth_response


class RegistrationView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    @extend_schema(
        tags=["Authentication"],
        summary="Register a new user",
        request=RegistrationSerializer,
        responses={
            201: AuthResponseSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "Registration request",
                value={
                    "username": "jane",
                    "email": "jane@example.com",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "password": "StrongPass123!",
                    "password_confirm": "StrongPass123!",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return auth_response("User registered successfully.", user, status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @extend_schema(
        tags=["Authentication"],
        summary="Log in and receive JWT tokens",
        request=LoginSerializer,
        responses={
            200: AuthResponseSerializer,
            400: OpenApiResponse(description="Invalid credentials or validation error"),
        },
        examples=[
            OpenApiExample(
                "Login request",
                value={"username": "jane", "password": "StrongPass123!"},
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return auth_response("Login successful.", user, status.HTTP_200_OK)


class RefreshTokenView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = DocumentedTokenRefreshSerializer

    @extend_schema(
        tags=["Authentication"],
        summary="Refresh an access token",
        request=DocumentedTokenRefreshSerializer,
        responses={
            200: TokenRefreshResponseSerializer,
            401: OpenApiResponse(description="Refresh token is invalid or expired"),
        },
        examples=[
            OpenApiExample(
                "Refresh request",
                value={"refresh": "your-refresh-token"},
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = TokenRefreshSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken("Refresh token is invalid or expired.") from exc
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CurrentUserView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    @extend_schema(
        tags=["Authentication"],
        summary="Get the authenticated user",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(
                description="Authentication credentials were not provided or are invalid"
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class LogoutView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    @extend_schema(
        tags=["Authentication"],
        summary="Log out by blacklisting a refresh token",
        request=LogoutSerializer,
        responses={
            200: MessageResponseSerializer,
            400: OpenApiResponse(description="Refresh token is invalid or already blacklisted"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided or are invalid"
            ),
        },
        examples=[
            OpenApiExample(
                "Logout request",
                value={"refresh": "your-refresh-token"},
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
