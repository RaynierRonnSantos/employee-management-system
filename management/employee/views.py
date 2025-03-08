from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Employee, SalaryHistory, PerformanceReview, Attendance
from .serializers import EmployeeSerializer, SalaryHistorySerializer, PerformanceReviewSerializer, AttendanceSerializer

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    @action(detail=True, methods=['patch'])
    def request_department_transfer(self, request, pk=None):
        employee = self.get_object()
        new_department = request.data.get('new_department')
        if new_department:
            employee.department = new_department
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

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        employee = self.get_object()
        employee.active = False
        employee.save()
        return Response({"message": f"{employee.name} deactivated"})

    @action(detail=True, methods=['post'])
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
    
    @action(detail=True, methods=['delete'])
    def permanent(self, request, pk=None):
        employee = self.get_object()
        approval = request.data.get('approval')
        if approval == 'approve':
            employee.delete()
            return Response({"message": f"{employee.name} permanently deleted"}, status=status.HTTP_200_OK)
        return Response({"error": "HR approval required"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        employee = self.get_object()
        return Response({'message': f'Attendance summary for {employee.name}'})

    @action(detail=True, methods=['patch'])
    def reset_attendance(self, request, pk=None):
        employee = self.get_object()
        employee.attendance = 0
        employee.save()
        return Response({'message': f'Attendance reset for {employee.name}'})
        

class SalaryViewSet(viewsets.ModelViewSet):
    queryset = SalaryHistory.objects.all()
    serializer_class = SalaryHistorySerializer

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
        
        return Response({"error": "New salary not provided"}, status=status.HTTP_400_BAD_REQUEST)

class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer

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
                return Response({"error": "Review and rating are required"}, status=status.HTTP_400_BAD_REQUEST)

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
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    @action(detail=True, methods=['get'])
    def employee_attendance(self, request, pk=None):
        """Fetch attendance records for a specific employee."""
        employee = get_object_or_404(Employee, pk=pk)
        attendance = Attendance.objects.filter(employee=employee)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_attendance(self, request, pk=None):
        """Mark an employee's attendance."""
        employee = get_object_or_404(Employee, pk=pk)
        date = request.data.get('date')
        status = request.data.get('status', 'present')
        check_in_time = request.data.get('check_in_time')
        check_out_time = request.data.get('check_out_time')
        overtime_hours = request.data.get('overtime_hours', 0)

        attendance = Attendance.objects.create(
            employee=employee,
            date=date,
            status=status,
            check_in_time=check_in_time,
            check_out_time=check_out_time,
            overtime_hours=overtime_hours
        )

        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def late_count(self, request, pk=None):
        """Count the number of times an employee was late."""
        employee = get_object_or_404(Employee, pk=pk)
        late_days = Attendance.objects.filter(employee=employee, status='late').count()
        return Response({"late_count": late_days})

    @action(detail=True, methods=['get'])
    def overtime_hours(self, request, pk=None):
        """Calculate total overtime hours for an employee."""
        employee = get_object_or_404(Employee, pk=pk)
        total_overtime = Attendance.objects.filter(employee=employee).aggregate(total=models.Sum('overtime_hours'))['total'] or 0
        return Response({"overtime_hours": total_overtime})

    @action(detail=True, methods=['get'])
    def leave_history(self, request, pk=None):
        """Fetch an employee's leave history."""
        employee = get_object_or_404(Employee, pk=pk)
        leaves = Attendance.objects.filter(employee=employee, status='leave')
        return Response(AttendanceSerializer(leaves, many=True).data)

    @action(detail=True, methods=['post'])
    def request_leave(self, request, pk=None):
        """Request leave for an employee."""
        employee = get_object_or_404(Employee, pk=pk)
        date = request.data.get('date')

        if not date:
            return Response({"error": "Date is required"}, status=status.HTTP_400_BAD_REQUEST)

        leave_record = Attendance.objects.create(employee=employee, date=date, status='leave')

        return Response(AttendanceSerializer(leave_record).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'])
    def approve_leave(self, request, pk=None):
        """Approve or reject a leave request."""
        employee = get_object_or_404(Employee, pk=pk)
        date = request.data.get('date')
        approval = request.data.get('approval')

        try:
            leave_record = Attendance.objects.get(employee=employee, date=date, status='leave')
            if approval == "approve":
                leave_record.status = "leave"
                leave_record.save()
                return Response({"message": "Leave approved"})
            elif approval == "reject":
                leave_record.delete()
                return Response({"message": "Leave rejected"})
            else:
                return Response({"error": "Invalid approval status"}, status=status.HTTP_400_BAD_REQUEST)
        except Attendance.DoesNotExist:
            return Response({"error": "Leave request not found"}, status=status.HTTP_404_NOT_FOUND)