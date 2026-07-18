from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Student
from .serializers import StudentSerializer


class HomeAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = {
            "message": "Welcome to Student Record Management API",
            "endpoints": {
                "students": "/api/students/",
                "auth": {
                    "register": "/api/auth/register/",
                    "login": "/api/auth/login/",
                    "logout": "/api/auth/logout/",
                    "profile": "/api/auth/profile/",
                    "change_password": "/api/auth/change-password/",
                },
                "admin": "/admin/",
            }
        }
        return Response(data)


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'enrollment_date']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    ordering_fields = ['created_at', 'enrollment_date', 'last_name']
    ordering = ['-created_at']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {"detail": "Student deactivated successfully."},
            status=status.HTTP_200_OK
        )