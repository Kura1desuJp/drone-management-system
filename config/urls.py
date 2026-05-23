from django.contrib import admin
from django.urls import path, include
from drones.views import AppView
from rest_framework.views import APIView
from rest_framework.response import Response

# ============================================================
# ДОМАШНЯ СТОРІНКА API
# ============================================================
class APIRootView(APIView):
    """Домашня сторінка API з описом доступних endpoints."""
    
    def get(self, request):
        return Response({
            'message': 'DroneControl API v1.0 - Система керування дронами 🚁',
            'app': 'Перейти до застосунку: /',
            'admin': 'Адміністрація: /admin/',
            'endpoints': {
                'drones': '/api/drones/drones/',
                'drones_active': '/api/drones/drones/active_drones/',
                'maintenance': '/api/drones/maintenance/',
                'maintenance_pending': '/api/drones/maintenance/pending/',
                'inspections': '/api/drones/inspections/',
                'inspections_passed': '/api/drones/inspections/passed/',
            }
        })

urlpatterns = [
    # SPA - Основна програма
    path('', AppView.as_view(), name='app'),
    
    # Адміністрація
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', APIRootView.as_view(), name='api-root'),
    path('api/drones/', include('drones.urls')),
    path('api/users/', include('users.urls')),
    
    # REST Framework auth
    path('api-auth/', include('rest_framework.urls')),
]
