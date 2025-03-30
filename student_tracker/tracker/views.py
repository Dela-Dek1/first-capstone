from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Avg, Count
from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
import csv
import datetime
from io import BytesIO
import xlsxwriter

from .models import Student, Attendance, Performance
from .serializers import UserSerializer, StudentSerializer, AttendanceSerializer, PerformanceSerializer

# Define filter classes FIRST
class AttendanceFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date', lookup_expr='lte')
    
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'date_from', 'date_to']

class PerformanceFilter(filters.FilterSet):
    date_from = filters.DateFilter(field_name='date_recorded', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='date_recorded', lookup_expr='lte')
    score_min = filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = filters.NumberFilter(field_name='score', lookup_expr='lte')
    
    class Meta:
        model = Performance
        fields = ['student', 'subject', 'date_recorded', 'date_from', 'date_to', 'score_min', 'score_max']

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

# API ViewSets - AFTER filter classes are defined
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
    filterset_class = AttendanceFilter
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
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        format_type = request.query_params.get('format', 'csv')
        
        # Apply filters from the filter_class
        queryset = self.filter_queryset(self.get_queryset())
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="attendance_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Student', 'Date', 'Status', 'Recorded By', 'Timestamp'])
            
            for attendance in queryset:
                writer.writerow([
                    attendance.student.name,
                    attendance.date,
                    attendance.status,
                    attendance.recorded_by.username if attendance.recorded_by else 'N/A',
                    attendance.timestamp
                ])
            
            return response
        
        elif format_type == 'excel':
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            
            # Add headers
            headers = ['Student', 'Date', 'Status', 'Recorded By', 'Timestamp']
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header)
            
            # Add data
            for row_num, attendance in enumerate(queryset, 1):
                worksheet.write(row_num, 0, attendance.student.name)
                worksheet.write(row_num, 1, attendance.date.strftime('%Y-%m-%d'))
                worksheet.write(row_num, 2, attendance.status)
                worksheet.write(row_num, 3, attendance.recorded_by.username if attendance.recorded_by else 'N/A')
                worksheet.write(row_num, 4, attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
            
            workbook.close()
            
            output.seek(0)
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="attendance_export.xlsx"'
            
            return response
        
        return Response({'error': 'Format not supported'}, status=400)

class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsTeacherOrReadOnly]
    filterset_class = PerformanceFilter
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
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        format_type = request.query_params.get('format', 'csv')
        
        # Apply filters from the filter_class
        queryset = self.filter_queryset(self.get_queryset())
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="performance_export.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Student', 'Subject', 'Score', 'Date Recorded', 'Recorded By'])
            
            for performance in queryset:
                writer.writerow([
                    performance.student.name,
                    performance.subject,
                    performance.score,
                    performance.date_recorded,
                    performance.recorded_by.username if performance.recorded_by else 'N/A'
                ])
            
            return response
        
        elif format_type == 'excel':
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            
            # Add headers
            headers = ['Student', 'Subject', 'Score', 'Date Recorded', 'Recorded By']
            for col_num, header in enumerate(headers):
                worksheet.write(0, col_num, header)
            
            # Add data
            for row_num, performance in enumerate(queryset, 1):
                worksheet.write(row_num, 0, performance.student.name)
                worksheet.write(row_num, 1, performance.subject)
                worksheet.write(row_num, 2, performance.score)
                worksheet.write(row_num, 3, performance.date_recorded.strftime('%Y-%m-%d'))
                worksheet.write(row_num, 4, performance.recorded_by.username if performance.recorded_by else 'N/A')
            
            workbook.close()
            
            output.seek(0)
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="performance_export.xlsx"'
            
            return response
        
        return Response({'error': 'Format not supported'}, status=400)
