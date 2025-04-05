from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth import views as auth_views  
from .views import custom_logout_view

router = DefaultRouter()
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'attendance', views.AttendanceViewSet, basename='attendance')
router.register(r'performance', views.PerformanceViewSet, basename='performance')




urlpatterns = [
    path('', views.home, name='home'), 
    path('api-docs/', views.api_docs, name='api_docs'),  
    path('api/', include(router.urls)),  
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("logout/", custom_logout_view, name="logout"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),  
]
