from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for viewsets
router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'attendance', views.AttendanceViewSet)
router.register(r'performance', views.PerformanceViewSet)

# URL patterns for the tracker app
urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
]