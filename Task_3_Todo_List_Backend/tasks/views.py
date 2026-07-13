from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated

from tasks.models import Task
from tasks.permissions import IsTaskOwner
from tasks.serializers import TaskSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Tasks"],
        summary="List tasks",
        description="Return all tasks owned by the authenticated user.",
        responses={200: TaskSerializer(many=True)},
    ),
    create=extend_schema(
        tags=["Tasks"],
        summary="Create a task",
        description="Create a new task owned by the authenticated user.",
        request=TaskSerializer,
        responses={
            201: TaskSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
        },
    ),
    retrieve=extend_schema(
        tags=["Tasks"],
        summary="Retrieve a task",
        description="Return one task owned by the authenticated user.",
        responses={
            200: TaskSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
            403: OpenApiResponse(description="Task belongs to another user"),
            404: OpenApiResponse(description="Task was not found"),
        },
    ),
    update=extend_schema(
        tags=["Tasks"],
        summary="Update a task",
        description="Replace all editable fields on a task owned by the authenticated user.",
        request=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
            403: OpenApiResponse(description="Task belongs to another user"),
            404: OpenApiResponse(description="Task was not found"),
        },
    ),
    partial_update=extend_schema(
        tags=["Tasks"],
        summary="Partially update a task",
        description="Update selected editable fields on a task owned by the authenticated user.",
        request=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
            403: OpenApiResponse(description="Task belongs to another user"),
            404: OpenApiResponse(description="Task was not found"),
        },
    ),
    destroy=extend_schema(
        tags=["Tasks"],
        summary="Delete a task",
        description="Delete a task owned by the authenticated user.",
        responses={
            204: OpenApiResponse(description="Task deleted successfully"),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
            403: OpenApiResponse(description="Task belongs to another user"),
            404: OpenApiResponse(description="Task was not found"),
        },
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskOwner]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Task.objects.none()
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
