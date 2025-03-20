from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, SalaryViewSet, PerformanceViewSet, AttendanceViewSet, AuthViewSet

router = DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register(r'employees', EmployeeViewSet, basename='employees')
router.register(r'salary', SalaryViewSet, basename='salary')
router.register(r'performance', PerformanceViewSet, basename='performance')
router.register(r'attendance', AttendanceViewSet, basename='attendance')

urlpatterns = [
    path('', include(router.urls)),
]
