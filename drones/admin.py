from django.contrib import admin
from django.utils.html import format_html
from .models import Drone, Maintenance, Inspection


@admin.register(Drone)
class DroneAdmin(admin.ModelAdmin):
    list_display = ['serial_number', 'model_name', 'status_badge', 'hours_flown_display', 'owner', 'purchase_date']
    list_filter = ['status', 'purchase_date', 'owner']
    search_fields = ['serial_number', 'model_name', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'purchase_date'
    list_per_page = 20
    list_select_related = ['owner']
    ordering = ['-created_at']

    fieldsets = (
        ('Інформація про дрон', {
            'fields': ('model_name', 'serial_number', 'status', 'owner')
        }),
        ('Технічні характеристики', {
            'fields': ('hours_flown', 'max_flight_time', 'weight', 'purchase_date')
        }),
        ('Системні дані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        styles = {
            'active':   ('green',  'Активний'),
            'inactive': ('#6c757d', 'Неактивний'),
            'repair':   ('#dc3545', 'На ремонті'),
            'storage':  ('#fd7e14', 'На зберіганні'),
        }
        color, label = styles.get(obj.status, ('#007bff', obj.status))
        return format_html(
            '<span style="padding:4px 12px;background:{};color:#fff;border-radius:12px;'
            'font-size:0.82em;font-weight:600;letter-spacing:.4px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'

    def hours_flown_display(self, obj):
        icon = 'fa-battery-full' if obj.hours_flown < 200 else ('fa-battery-half' if obj.hours_flown < 500 else 'fa-battery-empty')
        color = 'green' if obj.hours_flown < 200 else ('orange' if obj.hours_flown < 500 else 'red')
        return format_html(
            '<span style="color:{}"><i class="fas {}"></i> {} год</span>',
            color, icon, obj.hours_flown
        )
    hours_flown_display.short_description = 'Льотні години'
    hours_flown_display.admin_order_field = 'hours_flown'


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ['drone', 'maintenance_type_display', 'status_badge', 'scheduled_date', 'cost_display', 'performed_by']
    list_filter = ['status', 'maintenance_type', 'scheduled_date']
    search_fields = ['drone__serial_number', 'description', 'performed_by__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'
    list_per_page = 25
    list_select_related = ['drone', 'performed_by']
    ordering = ['-scheduled_date']

    fieldsets = (
        ('Деталі обслуговування', {
            'fields': ('drone', 'maintenance_type', 'status', 'performed_by')
        }),
        ('Опис', {
            'fields': ('description',),
        }),
        ('Дати', {
            'fields': ('scheduled_date', 'completed_date')
        }),
        ('Вартість', {
            'fields': ('cost',)
        }),
        ('Системні дані', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        styles = {
            'scheduled':   ('#007bff', 'Заплановане'),
            'in_progress': ('#fd7e14', 'У процесі'),
            'completed':   ('green',   'Завершене'),
            'failed':      ('#dc3545', 'Не виконане'),
        }
        color, label = styles.get(obj.status, ('#6c757d', obj.status))
        return format_html(
            '<span style="padding:4px 12px;background:{};color:#fff;border-radius:12px;'
            'font-size:0.82em;font-weight:600;letter-spacing:.4px">{}</span>',
            color, label
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'

    def maintenance_type_display(self, obj):
        icons = {
            'routine':    'fa-tools',
            'repair':     'fa-wrench',
            'inspection': 'fa-search',
            'upgrade':    'fa-arrow-up',
        }
        icon = icons.get(obj.maintenance_type, 'fa-cog')
        return format_html(
            '<i class="fas {}"></i> {}',
            icon, obj.get_maintenance_type_display()
        )
    maintenance_type_display.short_description = 'Тип'
    maintenance_type_display.admin_order_field = 'maintenance_type'

    def cost_display(self, obj):
        color = 'green' if obj.cost == 0 else ('#dc3545' if obj.cost > 5000 else '#333')
        return format_html('<span style="color:{};font-weight:600">{} грн</span>', color, obj.cost)
    cost_display.short_description = 'Вартість'
    cost_display.admin_order_field = 'cost'


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ['drone', 'inspection_date', 'result_badge', 'battery_bar', 'inspector_name', 'components_summary']
    list_filter = ['result', 'inspection_date', 'motor_status', 'camera_status']
    search_fields = ['drone__serial_number', 'inspector_name', 'issues_found']
    readonly_fields = ['created_at', 'inspection_date']
    date_hierarchy = 'inspection_date'
    list_per_page = 25
    list_select_related = ['drone']
    ordering = ['-inspection_date']

    fieldsets = (
        ('Основна інформація', {
            'fields': ('drone', 'inspection_date', 'inspector_name', 'result')
        }),
        ('Стан компонентів', {
            'fields': ('battery_health', 'motor_status', 'propeller_condition', 'camera_status', 'gimbal_status')
        }),
        ('Проблеми та рекомендації', {
            'fields': ('issues_found', 'recommendations')
        }),
        ('Системні дані', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def result_badge(self, obj):
        styles = {
            'passed':  ('green',   'Пройшов'),
            'warning': ('#fd7e14', 'З попередженнями'),
            'failed':  ('#dc3545', 'Не пройшов'),
        }
        color, label = styles.get(obj.result, ('#6c757d', obj.result))
        return format_html(
            '<span style="padding:4px 12px;background:{};color:#fff;border-radius:12px;'
            'font-size:0.82em;font-weight:600;letter-spacing:.4px">{}</span>',
            color, label
        )
    result_badge.short_description = 'Результат'
    result_badge.admin_order_field = 'result'

    def battery_bar(self, obj):
        pct = obj.battery_health
        color = 'green' if pct >= 70 else ('orange' if pct >= 40 else '#dc3545')
        return format_html(
            '<div style="width:80px;background:#e9ecef;border-radius:4px;overflow:hidden">'
            '<div style="width:{pct}%;background:{color};height:14px;text-align:center;'
            'font-size:10px;color:#fff;line-height:14px">{pct}%</div></div>',
            pct=pct, color=color
        )
    battery_bar.short_description = 'Батарея'
    battery_bar.admin_order_field = 'battery_health'

    def components_summary(self, obj):
        icons = {'ok': ('fa-check-circle', 'green'), 'warning': ('fa-exclamation-circle', 'orange'), 'failed': ('fa-times-circle', 'red')}
        parts = [
            ('M', obj.motor_status),
            ('P', obj.propeller_condition),
            ('C', obj.camera_status),
            ('G', obj.gimbal_status),
        ]
        html = ''
        for label, status in parts:
            icon, color = icons.get(status, ('fa-question-circle', 'gray'))
            html += format_html(
                '<span title="{}" style="color:{};margin-right:4px"><i class="fas {}"></i></span>',
                label, color, icon
            )
        return format_html('<span>{}</span>', html)
    components_summary.short_description = 'Компоненти'
