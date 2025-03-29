from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Attendance, Performance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['is_staff']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'class_name', 'admission_number', 'enrollment_date']

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    recorded_by_username = serializers.ReadOnlyField(source='recorded_by.username')
    
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'student_name', 'date', 'status', 'recorded_by', 'recorded_by_username', 'timestamp']
        read_only_fields = ['recorded_by', 'timestamp']

class PerformanceSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.name')
    recorded_by_username = serializers.ReadOnlyField(source='recorded_by.username')
    
    class Meta:
        model = Performance
        fields = ['id', 'student', 'student_name', 'subject', 'score', 'date_recorded', 'recorded_by', 'recorded_by_username']
        read_only_fields = ['recorded_by']