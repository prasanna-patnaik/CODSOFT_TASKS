from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.permissions import IsTaskOwner
from tasks.serializers import TaskSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["Tasks"],
        summary="List tasks",
        description=(
            "Requires a valid Bearer access token. Returns only tasks owned by the "
            "authenticated user. Supports filtering by "
            "completed, priority, and category; searching title and description; and ordering "
            "by created_at, updated_at, due_date, or priority."
        ),
        parameters=[
            OpenApiParameter(
                name="completed",
                description="Filter by completed status. Use true or false.",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="priority",
                description="Filter by priority. Allowed values: low, medium, high.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="category",
                description="Filter by category using a case-insensitive exact match.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="search",
                description="Search within task title and description.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description=(
                    "Order by created_at, updated_at, due_date, or priority. Prefix with '-' "
                    "for descending order, for example -created_at."
                ),
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="page",
                description="Page number for paginated results. The page size is 10.",
                required=False,
                type=int,
            ),
        ],
        responses={
            200: TaskSerializer(many=True),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
        },
    ),
    create=extend_schema(
        tags=["Tasks"],
        summary="Create a task",
        description=(
            "Requires a valid Bearer access token. Creates a new task and assigns ownership "
            "to the authenticated user. The owner field cannot be supplied by the client."
        ),
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
        description=(
            "Requires a valid Bearer access token. Returns a task only when it belongs to "
            "the authenticated user."
        ),
        responses={
            200: TaskSerializer,
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
            404: OpenApiResponse(description="Task was not found or does not belong to the authenticated user"),
        },
    ),
    update=extend_schema(
        tags=["Tasks"],
        summary="Update a task",
        description=(
            "Requires a valid Bearer access token. Replaces all editable fields only when "
            "the task belongs to the authenticated user."
        ),
        request=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
            404: OpenApiResponse(description="Task was not found or does not belong to the authenticated user"),
        },
    ),
    partial_update=extend_schema(
        tags=["Tasks"],
        summary="Partially update a task",
        description=(
            "Requires a valid Bearer access token. Updates selected editable fields only "
            "when the task belongs to the authenticated user."
        ),
        request=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="Validation error"),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
            404: OpenApiResponse(description="Task was not found or does not belong to the authenticated user"),
        },
    ),
    destroy=extend_schema(
        tags=["Tasks"],
        summary="Delete a task",
        description=(
            "Requires a valid Bearer access token. Deletes a task only when it belongs to "
            "the authenticated user."
        ),
        responses={
            204: OpenApiResponse(description="Task deleted successfully"),
            401: OpenApiResponse(description="Authentication credentials were not provided or are invalid"),
            404: OpenApiResponse(description="Task was not found or does not belong to the authenticated user"),
        },
    ),
)
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskOwner]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority"]
    ordering = ["completed", "due_date", "-created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Task.objects.none()
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
