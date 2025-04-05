import django_filters
from .models import Attendance, Performance

class AttendanceFilter(django_filters.FilterSet):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status']

class PerformanceFilter(django_filters.FilterSet):
    class Meta:
        model = Performance
        fields = ['student', 'subject', 'score']
