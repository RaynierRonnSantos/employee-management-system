from rest_framework import serializers
from .models import Employee, SalaryHistory, PerformanceReview, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    department = serializers.CharField(required=True)
    position = serializers.CharField(required=True)
    salary = serializers.DecimalField(max_digits=20, decimal_places=2, required=True)

    class Meta:
        model = Employee
        fields = '__all__'

    def validate_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Salary must be greater than zero.")
        return value

class SalaryHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    new_salary = serializers.DecimalField(max_digits=20, decimal_places=2)

    class Meta:
        model = SalaryHistory
        fields = '__all__'

    def validate_new_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("New salary must be greater than zero.")
        return value

class PerformanceReviewSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = PerformanceReview
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'