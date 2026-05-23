from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# ============================================================
# МАРШРУТИЗАЦІЯ API
# ============================================================
router = DefaultRouter()
router.register(r'drones', views.DroneViewSet, basename='drone')
router.register(r'maintenance', views.MaintenanceViewSet, basename='maintenance')
router.register(r'inspections', views.InspectionViewSet, basename='inspection')

urlpatterns = [
    path('', include(router.urls)),
]
