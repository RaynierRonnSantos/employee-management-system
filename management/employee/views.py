from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Employee, SalaryHistory, PerformanceReview, Attendance
from .serializers import EmployeeSerializer, SalaryHistorySerializer, PerformanceReviewSerializer, AttendanceSerializer, RegisterSerializer, LoginSerializer, UserSerializer
from django.utils.timezone import now
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
            if user:
                refresh = RefreshToken.for_user(user)
                update_last_login(None, user)
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Employee.objects.filter(archived=False)

    @action(detail=True, methods=['patch'])
    def request_department_transfer(self, request, pk=None):
        employee = self.get_object()
        new_department = request.data.get('new_department')
        if new_department:
            employee.department = new_department
            employee.status = 'pending_transfer'
            employee.save()
            return Response({'status': 'Transfer requested successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'New department not provided'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def approve_transfer(self, request, pk=None):
        employee = self.get_object()
        approval = request.data.get('approval')
        if approval == 'approve':
            employee.status = 'transferred'
            employee.save()
            return Response({'status': 'Transfer approved'}, status=status.HTTP_200_OK)
        elif approval == 'reject':
            return Response({'status': 'Transfer rejected'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid approval status'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        employee = self.get_object()
        employee.active = False
        employee.save()
        return Response({"message": f"{employee.name} deactivated"})

    @action(detail=True, methods=['patch'])
    def restore(self, request, pk=None):
        employee = self.get_object()
        employee.active = True
        employee.save()
        return Response({"message": f"{employee.name} restored"})

    @action(detail=True, methods=['patch'])
    def archive(self, request, pk=None):
        employee = self.get_object()
        employee.archived = True
        employee.save()
        return Response({"message": f"{employee.name} archived"})

    @action(detail=True, methods=['patch'])
    def unarchive(self, request, pk=None):
        employee = self.get_object()
        if employee.archived:
            employee.archived = False
            employee.save()
            return Response({"message": f"{employee.name} unarchived successfully"}, status=status.HTTP_200_OK)
        return Response({"error": f"{employee.name} is not archived"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def archived(self, request):
        archived_employees = Employee.objects.filter(archived=True)
        serializer = self.get_serializer(archived_employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SalaryViewSet(viewsets.ModelViewSet):
    serializer_class = SalaryHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SalaryHistory.objects.filter(employee__archived=False)

    @action(detail=True, methods=['get'])
    def salary_history(self, request, pk=None):
        try:
            employee = Employee.objects.get(pk=pk)
            salary_history = SalaryHistory.objects.filter(employee=employee)

            if not salary_history.exists():
                return Response({"message": f"{employee.name} has no salary changes yet."}, status=status.HTTP_200_OK)

            serializer = SalaryHistorySerializer(salary_history, many=True)
            return Response(serializer.data)

        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'])
    def adjust_salary(self, request, pk=None):
        employee = Employee.objects.get(pk=pk)
        new_salary = request.data.get('new_salary')
        
        if new_salary:
            salary_record = SalaryHistory.objects.create(
                employee=employee,
                previous_salary=employee.salary,
                new_salary=new_salary
            )
            serializer = SalaryHistorySerializer(salary_record)
            
            employee.salary = new_salary
            employee.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({
                            "new_salary":  [
                                "This field is required."
                            ]
                        }, status=status.HTTP_400_BAD_REQUEST)

class PerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
            return PerformanceReview.objects.filter(employee__archived=False)

    @action(detail=True, methods=['get'])
    def performance_reviews(self, request, pk=None):
        try:
            employee = Employee.objects.get(id=pk)
            reviews = PerformanceReview.objects.filter(employee=employee)
            data = [{"employee_id": review.employee.id, "employee_name": review.employee.name, "review": review.review, "rating": review.rating} for review in reviews]
            return Response(data)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def submit_performance_review(self, request, pk=None):
        try:
            employee = Employee.objects.get(id=pk)
            review = request.data.get('review')
            rating = request.data.get('rating')

            if not review or not rating:
                return Response({
                                    "review": [
                                                "This field is required."
                                            ],
                                    "rating": [
                                                "This field is required."
                                            ],  
                                }, status=status.HTTP_400_BAD_REQUEST)

            performance = PerformanceReview.objects.create(
                employee=employee,
                review=review,
                rating=rating
            )
            return Response({"message": f"Performance review submitted for {employee.name}"}, status=status.HTTP_201_CREATED)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def top_performers(self, request):
        top_performers = PerformanceReview.objects.filter(rating__gte=9).select_related('employee')
        data = [{"employee_id": review.employee.id, "employee_name": review.employee.name, "rating": review.rating} for review in top_performers]
        return Response(data)

    @action(detail=True, methods=['delete'])
    def remove_performance_record(self, request, pk=None):
        review_id = request.data.get('review_id')
        try:
            employee = Employee.objects.get(id=pk)
            review = PerformanceReview.objects.get(id=review_id, employee=employee)
            review.delete()
            return Response({"message": "Performance review removed"}, status=status.HTTP_204_NO_CONTENT)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
        except PerformanceReview.DoesNotExist:
            return Response({"error": "Review not found"}, status=status.HTTP_404_NOT_FOUND)

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
            return Attendance.objects.filter(employee__archived=False)

    @action(detail=True, methods=['get'])
    def employee_attendance(self, request, pk=None):
        employee = Employee.objects.filter(pk=pk).first()

        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        attendance = Attendance.objects.filter(employee=employee)
        if not attendance.exists():
            return Response({"message": "No attendance records found for this employee."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        employee = Employee.objects.filter(pk=pk).first()
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        today = now().date()
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'check_in_time': now().time(), 'status': 'Present'}
        )

        if not created:
            return Response({"error": "Check-in already recorded"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Check-in recorded",
            "attendance": AttendanceSerializer(attendance).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        employee = Employee.objects.filter(pk=pk).first()
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        today = now().date()
        attendance = Attendance.objects.filter(employee=employee, date=today).first()

        if not attendance:
            return Response({"error": "No check-in record found"}, status=status.HTTP_400_BAD_REQUEST)

        if attendance.check_out_time:
            return Response({"error": "Check-out already recorded"}, status=status.HTTP_400_BAD_REQUEST)

        attendance.check_out_time = now().time()

        check_in_time = attendance.check_in_time
        if check_in_time:
            time_difference = (now() - now().replace(hour=check_in_time.hour, minute=check_in_time.minute)).total_seconds()
            hours_worked = time_difference / 3600
            overtime = max(0, hours_worked - 8)
            attendance.overtime_hours = overtime

        attendance.save()

        return Response({
            "message": "Check-out recorded",
            "attendance": AttendanceSerializer(attendance).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def overtime_hours(self, request, pk=None):
        employee = Employee.objects.filter(pk=pk).first()
        
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        total_overtime = Attendance.objects.filter(employee=employee).aggregate(total=Sum('overtime_hours'))['total'] or 0
        return Response({"overtime_hours": total_overtime})

    @action(detail=True, methods=['get'])
    def leave_history(self, request, pk=None):
        employee = Employee.objects.filter(pk=pk).first()
        
        if not employee:
            return Response({"error": "Employee not found"}, status=404)
        
        leaves = Attendance.objects.filter(employee=employee, status='leave')

        if not leaves.exists():
            return Response({"message": "No leave records found"}, status=404)

        return Response(AttendanceSerializer(leaves, many=True).data, status=200)

    @action(detail=True, methods=['post'])
    def request_leave(self, request, pk=None):
        employee = Employee.objects.filter(pk=pk).first()
        
        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        date = request.data.get('date')
        if not date:
            return Response({
                                "date": [
                                    "This field is required."
                                    ]
                            }, status=status.HTTP_400_BAD_REQUEST)

        leave_record = Attendance.objects.create(employee=employee, date=date, status='leave')
        return Response(AttendanceSerializer(leave_record).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def approve_leave(self, request, pk=None):
        employee = Employee.objects.filter(pk=pk).first()

        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        date = request.data.get('date')
        approval = request.data.get('approval')

        leave_record = Attendance.objects.filter(employee=employee, date=date, status='leave').first()

        if not leave_record:
            return Response(
                {
                    "date": [
                        "This field is required."
                    ],
                    "approval": [
                        "This field is required."
                    ]
                }, status=status.HTTP_404_NOT_FOUND)

        if approval == "approve":
            leave_record.status = "on leave"
            leave_record.save()
            return Response({"message": "Leave approved"})
        elif approval == "reject":
            leave_record.delete()
            return Response({"message": "Leave rejected"})
        else:
            return Response({
                                "approval": [
                                    "This field is required."
                                ]
                            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_attendance(self, request, pk=None):
        employee = Employee.objects.filter(pk=pk).first()

        if not employee:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        dates = request.data.get('dates')

        if not dates or not isinstance(dates, list):
            return Response({
                    "dates": [
                        "This field is required."
                    ]
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = Attendance.objects.filter(employee=employee, date__in=dates).delete()

        if deleted_count == 0:
            return Response({"message": "No matching attendance records found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": f"Deleted {deleted_count} attendance records for {employee.name}"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'])
    def delete_all_attendance(self, request):
        deleted_count, _ = Attendance.objects.all().delete()

        if deleted_count == 0:
            return Response({"message": "No attendance records to delete"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": f"Deleted {deleted_count} attendance records"}, status=status.HTTP_204_NO_CONTENT)
