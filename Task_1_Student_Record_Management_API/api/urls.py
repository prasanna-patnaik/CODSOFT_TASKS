from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HomeAPIView, StudentViewSet

router = DefaultRouter()
router.register(r'students', StudentViewSet)

urlpatterns = [
    path('', HomeAPIView.as_view(), name='home'),
    path('', include(router.urls)),
]