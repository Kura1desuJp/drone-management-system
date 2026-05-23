from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Drone, Maintenance, Inspection
from .serializers import DroneSerializer, MaintenanceSerializer, InspectionSerializer


# ============================================================
# SPA: ОДНОСТОРІНКОВА ПРОГРАМА
# ============================================================
class AppView(LoginRequiredMixin, View):
    """
    Головна SPA програма для управління дронами.
    Безшовна навігація без редиректів.
    """
    login_url = '/admin/login/'
    
    def get(self, request):
        context = {
            'user': request.user,
        }
        return render(request, 'app.html', context)


class DroneViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управління дронами.
    
    Функціональність:
    - Список усіх дронів з пагінацією
    - Фільтрування за статусом та моделлю
    - Пошук за серійним номером
    - CRUD операції (Create, Read, Update, Delete)
    - Користувацькі дії для статистики
    """
    
    queryset = Drone.objects.all()
    serializer_class = DroneSerializer
    permission_classes = [IsAuthenticated]
    
    # Фільтрування, пошук та сортування
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'model_name', 'owner']
    search_fields = ['serial_number', 'model_name']
    ordering_fields = ['created_at', 'hours_flown', 'purchase_date']
    ordering = ['-created_at']
    
    def perform_create(self, serializer):
        """Встановлює власника дрона як поточного користувача."""
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active_drones(self, request):
        """Отримати список активних дронів."""
        active = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_maintenance(self, request, pk=None):
        """Позначити дрон як 'На ремонті'."""
        drone = self.get_object()
        drone.status = 'repair'
        drone.save()
        serializer = self.get_serializer(drone)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_active(self, request, pk=None):
        """Позначити дрон як 'Активний'."""
        drone = self.get_object()
        drone.status = 'active'
        drone.save()
        serializer = self.get_serializer(drone)
        return Response(serializer.data)


# ============================================================
# VIEWSET: ОБСЛУГОВУВАННЯ
# ============================================================
class MaintenanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управління обслуговуванням дронів.
    
    Функціональність:
    - Список усіх робіт з пагінацією
    - Фільтрування за статусом та типом
    - Пошук за дроном та описом
    - CRUD операції
    - Користувацькі дії для звітування
    """
    
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]
    
    # Фільтрування, пошук та сортування
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'maintenance_type', 'drone']
    search_fields = ['drone__serial_number', 'description']
    ordering_fields = ['scheduled_date', 'cost', 'created_at']
    ordering = ['-scheduled_date']
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Отримати список запланованих робіт."""
        pending = self.get_queryset().filter(status='scheduled')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Отримати список завершених робіт."""
        completed = self.get_queryset().filter(status='completed')
        serializer = self.get_serializer(completed, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Позначити роботи як завершені."""
        maintenance = self.get_object()
        maintenance.status = 'completed'
        maintenance.performed_by = request.user
        maintenance.save()
        serializer = self.get_serializer(maintenance)
        return Response(serializer.data)


# ============================================================
# VIEWSET: ОГЛЯД/ДІАГНОСТИКА
# ============================================================
class InspectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управління оглядами дронів.
    
    Функціональність:
    - Список усіх оглядів з пагінацією
    - Фільтрування за результатом
    - Пошук за дроном та інспектором
    - CRUD операції
    - Користувацькі дії для аналізу
    """
    
    queryset = Inspection.objects.all()
    serializer_class = InspectionSerializer
    permission_classes = [IsAuthenticated]
    
    # Фільтрування, пошук та сортування
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['result', 'motor_status', 'camera_status', 'drone']
    search_fields = ['drone__serial_number', 'inspector_name']
    ordering_fields = ['inspection_date', 'battery_health']
    ordering = ['-inspection_date']
    
    @action(detail=False, methods=['get'])
    def passed(self, request):
        """Отримати огляди що пройшли перевірку."""
        passed = self.get_queryset().filter(result='passed')
        serializer = self.get_serializer(passed, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Отримати огляди що не пройшли перевірку."""
        failed = self.get_queryset().filter(result='failed')
        serializer = self.get_serializer(failed, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def warnings(self, request):
        """Отримати огляди з попередженнями."""
        warnings = self.get_queryset().filter(result='warning')
        serializer = self.get_serializer(warnings, many=True)
        return Response(serializer.data)
