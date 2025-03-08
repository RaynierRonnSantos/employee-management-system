from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Employee, SalaryHistory, PerformanceReview
from .serializers import EmployeeSerializer, SalaryHistorySerializer, PerformanceReviewSerializer

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
