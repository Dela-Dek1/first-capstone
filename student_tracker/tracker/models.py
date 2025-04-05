from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    subject = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=100)  
    class_name = models.CharField(max_length=50)
    admission_number = models.CharField(max_length=20, unique=True)
    enrollment_date = models.DateField()
    
    def __str__(self):
        return self.name

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'date'], name='unique_student_attendance')
        ]
        ordering = ['id']

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"

class Performance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performances')
    subject = models.CharField(max_length=50)
    score = models.FloatField()  
    date_recorded = models.DateField()
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-date_recorded']  

    def __str__(self):
        return f"{self.student.name} - {self.subject} - {self.score}"  
