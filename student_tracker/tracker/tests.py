from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Student, Attendance, Performance
import datetime

# Create your tests here.
class StudentTrackerTests(TestCase):
    def setUp(self):
        # Create test user (teacher)
        self.teacher = User.objects.create_user(
            username='teacher',
            password='password123',
            is_staff=True
        )
        
        # Create test user (student)
        self.student = User.objects.create_user(
            username='student',
            password='password123',
            is_staff=False
        )
        
        # Create test student
        self.test_student = Student.objects.create(
            name='Test Student',
            class_name='Class 10A',
            admission_number='ADM001',
            enrollment_date=datetime.date(2023, 1, 15)
        )
        
        # Create API client
        self.client = APIClient()
    
    def test_list_students(self):
        # Login as teacher
        self.client.force_authenticate(user=self.teacher)
        
        # Get students list
        response = self.client.get('/api/students/')
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that the student was returned
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Student')
    
    def test_create_attendance(self):
        # Login as teacher
        self.client.force_authenticate(user=self.teacher)
        
        # Attendance data
        data = {
            'student': self.test_student.id,
            'date': '2023-03-15',
            'status': 'present'
        }
        
        # Create attendance record
        response = self.client.post('/api/attendance/', data)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the attendance was created
        self.assertEqual(Attendance.objects.count(), 1)
        attendance = Attendance.objects.first()
        self.assertEqual(attendance.status, 'present')
    
    def test_create_performance(self):
        # Login as teacher
        self.client.force_authenticate(user=self.teacher)
        
        # Performance data
        data = {
            'student': self.test_student.id,
            'subject': 'Mathematics',
            'score': 85.5,
            'date_recorded': '2023-03-20'
        }
        
        # Create performance record
        response = self.client.post('/api/performance/', data)
        
        # Check status code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the performance was created
        self.assertEqual(Performance.objects.count(), 1)
        performance = Performance.objects.first()
        self.assertEqual(performance.subject, 'Mathematics')
        self.assertEqual(performance.score, 85.5)