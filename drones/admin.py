from django.contrib import admin
from django.utils.html import format_html
from .models import Drone, Maintenance, Inspection

# ============================================================
# АДМІН ПАНЕЛЬ: ДРОН
# ============================================================
@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    """Адмін для управління дронами."""
    
    list_display = ['serial_number', 'model_name', 'status_badge', 'hours_flown', 'owner', 'purchase_date']
    list_filter = ['status', 'purchase_date', 'owner']
    search_fields = ['serial_number', 'model_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('🚁 Інформація про дрон', {
            'fields': ('model_name', 'serial_number', 'status', 'owner')
        }),
        ('📊 Технічні характеристики', {
            'fields': ('hours_flown', 'max_flight_time', 'weight', 'purchase_date')
        }),
        ('🕐 Системні дані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Показує статус з кольором."""
        colors = {
            'active': 'green',
            'inactive': 'gray',
            'repair': 'red',
            'storage': 'orange',
        }
        color = colors.get(obj.status, 'blue')
        return format_html(
            '<span style="padding: 3px 10px; background-color: {}; color: white; border-radius: 3px;">{}</span>',
            color,
            dict(obj.STATUS_CHOICES).get(obj.status)
        )
    status_badge.short_description = 'Статус'


# ============================================================
# АДМІН ПАНЕЛЬ: ОБСЛУГОВУВАННЯ
# ============================================================
@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    """Адмін для управління обслуговуванням."""
    
    list_display = ['drone', 'maintenance_type', 'status_badge', 'scheduled_date', 'cost', 'performed_by']
    list_filter = ['status', 'maintenance_type', 'scheduled_date']
    search_fields = ['drone__serial_number', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('🔧 Деталі обслуговування', {
            'fields': ('drone', 'maintenance_type', 'status', 'performed_by')
        }),
        ('📝 Опис', {
            'fields': ('description',),
        }),
        ('📅 Дати', {
            'fields': ('scheduled_date', 'completed_date')
        }),
        ('💰 Вартість', {
            'fields': ('cost',)
        }),
        ('🕐 Системні дані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Показує статус з кольором."""
        colors = {
            'scheduled': 'blue',
            'in_progress': 'orange',
            'completed': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="padding: 3px 10px; background-color: {}; color: white; border-radius: 3px;">{}</span>',
            color,
            dict(obj.STATUS_CHOICES).get(obj.status)
        )
    status_badge.short_description = 'Статус'


# ============================================================
# АДМІН ПАНЕЛЬ: ОГЛЯД
# ============================================================
@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    """Адмін для управління оглядами."""
    
    list_display = ['drone', 'inspection_date', 'result_badge', 'battery_health', 'inspector_name']
    list_filter = ['result', 'inspection_date', 'motor_status', 'camera_status']
    search_fields = ['drone__serial_number', 'inspector_name', 'issues_found']
    readonly_fields = ['created_at', 'inspection_date']
    
    fieldsets = (
        ('🔍 Основна інформація', {
            'fields': ('drone', 'inspection_date', 'inspector_name', 'result')
        }),
        ('🔋 Стан компонентів', {
            'fields': ('battery_health', 'motor_status', 'propeller_condition', 'camera_status', 'gimbal_status')
        }),
        ('⚠️ Проблеми та рекомендації', {
            'fields': ('issues_found', 'recommendations')
        }),
        ('🕐 Системні дані', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def result_badge(self, obj):
        """Показує результат з кольором."""
        colors = {
            'passed': 'green',
            'warning': 'orange',
            'failed': 'red',
        }
        color = colors.get(obj.result, 'blue')
        return format_html(
            '<span style="padding: 3px 10px; background-color: {}; color: white; border-radius: 3px;">{}</span>',
            color,
            dict(obj.RESULT_CHOICES).get(obj.result)
        )
    result_badge.short_description = 'Результат'
