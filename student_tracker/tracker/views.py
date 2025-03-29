from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Student, Attendance, Performance
from .serializers import UserSerializer, StudentSerializer, AttendanceSerializer, PerformanceSerializer

# Create your views here.

# Custom permission for teachers/staff
class IsTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow read methods for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Write permissions only for staff/teachers
        return request.user.is_authenticated and request.user.is_staff

# Standard views for templates
def home(request):
    return render(request, 'tracker/home.html')

def api_docs(request):
    return render(request, 'tracker/api_docs.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# API ViewSets
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filterset_fields = ['class_name']
    search_fields = ['name', 'class_name', 'admission_number']
    ordering_fields = ['name', 'enrollment_date', 'class_name']

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filterset_fields = ['student', 'date', 'status']
    search_fields = ['student__name', 'status']
    ordering_fields = ['date', 'status']
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Get attendance summary data
        total_records = Attendance.objects.count()
        present_count = Attendance.objects.filter(status='present').count()
        absent_count = Attendance.objects.filter(status='absent').count()
        late_count = Attendance.objects.filter(status='late').count()
        
        if total_records > 0:
            present_percent = (present_count / total_records) * 100
            absent_percent = (absent_count / total_records) * 100
            late_percent = (late_count / total_records) * 100
        else:
            present_percent = absent_percent = late_percent = 0
        
        return Response({
            'total_records': total_records,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'present_percent': round(present_percent, 2),
            'absent_percent': round(absent_percent, 2),
            'late_percent': round(late_percent, 2)
        })

class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filterset_fields = ['student', 'subject', 'date_recorded']
    search_fields = ['student__name', 'subject']
    ordering_fields = ['date_recorded', 'score']
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        # Get performance summary data
        avg_score = Performance.objects.aggregate(avg_score=Avg('score'))['avg_score']
        
        # Get subject breakdown
        subjects = {}
        for subject in Performance.objects.values_list('subject', flat=True).distinct():
            subject_avg = Performance.objects.filter(subject=subject).aggregate(
                avg=Avg('score')
            )['avg']
            subjects[subject] = round(subject_avg, 2) if subject_avg else 0
        
        return Response({
            'overall_average': round(avg_score, 2) if avg_score else 0,
            'total_records': Performance.objects.count(),
            'subject_breakdown': subjects
        })