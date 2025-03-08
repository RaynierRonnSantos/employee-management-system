from rest_framework import serializers
from .models import Employee, SalaryHistory, PerformanceReview, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    salary = serializers.SerializerMethodField()

    def get_salary(self, obj):
        return f"{obj.salary:.2f}"
    
    class Meta:
        model = Employee
        fields = '__all__'

class SalaryHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)

    class Meta:
        model = SalaryHistory
        fields = '__all__'

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