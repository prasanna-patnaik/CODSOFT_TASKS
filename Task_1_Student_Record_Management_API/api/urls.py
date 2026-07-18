from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeAPIView, StudentViewSet
from .auth_views import RegisterView, LoginView, LogoutView, ProfileView, ChangePasswordView

router = DefaultRouter()
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('', HomeAPIView.as_view(), name='home'),
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
]