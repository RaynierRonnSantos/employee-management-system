from rest_framework import serializers
from .models import Employee, SalaryHistory, PerformanceReview, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    department = serializers.CharField(required=True)
    position = serializers.CharField(required=True)
    salary = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = '__all__'

    def get_salary(self, obj):
        return f"₱{obj.salary:,.2f}"

    def validate_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Salary must be greater than zero.")
        return value

class SalaryHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    previous_salary = serializers.SerializerMethodField()
    new_salary = serializers.SerializerMethodField()

    class Meta:
        model = SalaryHistory
        fields = '__all__'

    def get_previous_salary(self, obj):
        return f"₱{obj.previous_salary:,.2f}"

    def get_new_salary(self, obj):
        return f"₱{obj.new_salary:,.2f}"

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