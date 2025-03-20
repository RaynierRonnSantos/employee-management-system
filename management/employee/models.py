import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    employee_id = models.CharField(max_length=20, unique=True)

    # Avoid reverse accessor clashes by setting related_name
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_groups",  # Set a unique related_name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions",  # Set a unique related_name
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = str(uuid.uuid4())[:8]  # Generates unique ID
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    
class Employee(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, default=0.0)
    active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.position} - {self.department})"

class SalaryHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_history')
    previous_salary = models.DecimalField(max_digits=20, decimal_places=2)
    new_salary = models.DecimalField(max_digits=20, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - Salary Change: {self.previous_salary} → {self.new_salary}"

class PerformanceReview(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.name} - Review ({self.rating}/10)"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Leave', 'Leave'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Present")
    overtime_hours = models.FloatField(default=0)

    def __str__(self):
        return f"{self.employee.name} - {self.date}"