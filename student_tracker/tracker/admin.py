from django.contrib import admin
from .models import Student, Attendance, Performance

# Register your models here.
admin.site.register(Student)
admin.site.register(Attendance)
admin.site.register(Performance)