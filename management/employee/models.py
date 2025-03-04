from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    salary = models.FloatField()
    mentor = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=True)
    archived = models.BooleanField(default=False)

class SalaryHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_history')
    previous_salary = models.DecimalField(max_digits=10, decimal_places=2)
    new_salary = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)

class PerformanceReview(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class TrainingSession(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='trainings')
    course_name = models.CharField(max_length=200)
    date_enrolled = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name, f"{self.employee.name} Review ({self.rating})", f"{self.employee.name} - {self.course_name}"
    