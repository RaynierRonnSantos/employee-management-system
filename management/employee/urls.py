from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, SalaryViewSet, PerformanceViewSet, TrainingViewSet

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'salary', SalaryViewSet, basename='salary')
router.register(r'performance', PerformanceViewSet, basename='performance')
router.register(r'training', TrainingViewSet, basename='training')

urlpatterns = [
    path('', include(router.urls)),
]
