from django.contrib import admin
from django.urls import path, include
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from drones.views import AppView
from rest_framework.views import APIView
from rest_framework.response import Response


@staff_member_required
def admin_profile_redirect(request):
    """Redirect to the current user's admin change page."""
    return redirect(f'/admin/auth/user/{request.user.pk}/change/')

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

    # Profile redirect (must be before admin/ to take precedence)
    path('admin/profile/', admin_profile_redirect, name='admin-profile'),

    # Адміністрація
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', APIRootView.as_view(), name='api-root'),
    path('api/drones/', include('drones.urls')),
    path('api/users/', include('users.urls')),
    
    # REST Framework auth
    path('api-auth/', include('rest_framework.urls')),
]
