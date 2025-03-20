from rest_framework import serializers
from .models import Employee, SalaryHistory, PerformanceReview, Attendance
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

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