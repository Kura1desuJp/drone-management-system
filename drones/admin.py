import csv
from django.contrib import admin
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Drone, Maintenance, Inspection


def _csv_response(filename):
    """Повертає HttpResponse з правильними заголовками для CSV + BOM для Excel."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('﻿')  # BOM — коректне відкриття в Excel
    return response


# ============================================================
# ADMIN: ДРОНИ
# ============================================================

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
    actions = ['export_csv']

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
        colors = {
            'active':   ('green',    'Активний'),
            'inactive': ('#6c757d',  'Неактивний'),
            'repair':   ('#dc3545',  'На ремонті'),
            'storage':  ('#fd7e14',  'На зберіганні'),
        }
        color, label = colors.get(obj.status, ('#007bff', obj.status))
        return format_html(
            '<span style="padding:4px 12px;background:{};color:#fff;border-radius:12px;'
            'font-size:0.82em;font-weight:600;letter-spacing:.4px">{}</span>',
            color, label,
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'

    def hours_flown_display(self, obj):
        h = obj.hours_flown
        icon  = 'fa-battery-full'  if h < 200 else ('fa-battery-half'  if h < 500 else 'fa-battery-empty')
        color = '#22c55e'          if h < 200 else ('#f97316'          if h < 500 else '#ef4444')
        return format_html(
            '<span style="color:{};font-size:0.95em;display:inline-flex;align-items:center;gap:6px">'
            '<i class="fas {}" style="font-size:1.15em"></i>'
            '<strong>{}</strong> год'
            '</span>',
            color, icon, h,
        )
    hours_flown_display.short_description = 'Льотні години'
    hours_flown_display.admin_order_field = 'hours_flown'

    @admin.action(description='Експортувати в CSV')
    def export_csv(self, request, queryset):
        response = _csv_response('drones.csv')
        w = csv.writer(response)
        w.writerow(['Серійний номер', 'Модель', 'Статус', 'Льотні години',
                    'Макс. час польоту (хв)', 'Вага (г)', 'Дата придбання', 'Власник'])
        for d in queryset.select_related('owner'):
            w.writerow([
                d.serial_number,
                d.model_name,
                d.get_status_display(),
                d.hours_flown,
                d.max_flight_time,
                d.weight,
                d.purchase_date.strftime('%d.%m.%Y') if d.purchase_date else '',
                d.owner.username if d.owner else '',
            ])
        return response


# ============================================================
# ADMIN: ОБСЛУГОВУВАННЯ
# ============================================================

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
    actions = ['export_csv']

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
        colors = {
            'scheduled':   ('#007bff', 'Заплановане'),
            'in_progress': ('#fd7e14', 'У процесі'),
            'completed':   ('green',   'Завершене'),
            'failed':      ('#dc3545', 'Не виконане'),
        }
        color, label = colors.get(obj.status, ('#6c757d', obj.status))
        return format_html(
            '<span style="padding:4px 12px;background:{};color:#fff;border-radius:12px;'
            'font-size:0.82em;font-weight:600;letter-spacing:.4px">{}</span>',
            color, label,
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'

    def maintenance_type_display(self, obj):
        icons = {
            'routine':    ('fa-screwdriver-wrench', '#6366f1'),
            'repair':     ('fa-wrench',             '#f59e0b'),
            'inspection': ('fa-magnifying-glass',   '#0ea5e9'),
            'upgrade':    ('fa-arrow-up',           '#22c55e'),
        }
        icon, color = icons.get(obj.maintenance_type, ('fa-gear', '#6b7280'))
        return format_html(
            '<span style="display:inline-flex;align-items:center;gap:7px">'
            '<i class="fas {}" style="font-size:1.1em;color:{}"></i>'
            '{}'
            '</span>',
            icon, color, obj.get_maintenance_type_display(),
        )
    maintenance_type_display.short_description = 'Тип'
    maintenance_type_display.admin_order_field = 'maintenance_type'

    def cost_display(self, obj):
        color = 'green' if obj.cost == 0 else ('#dc3545' if obj.cost > 5000 else '#333')
        return format_html('<span style="color:{};font-weight:600">{} грн</span>', color, obj.cost)
    cost_display.short_description = 'Вартість'
    cost_display.admin_order_field = 'cost'

    @admin.action(description='Експортувати в CSV')
    def export_csv(self, request, queryset):
        response = _csv_response('maintenance.csv')
        w = csv.writer(response)
        w.writerow(['Дрон', 'Тип', 'Статус', 'Виконавець',
                    'Запланована дата', 'Дата завершення', 'Вартість (грн)', 'Опис'])
        for m in queryset.select_related('drone', 'performed_by'):
            w.writerow([
                m.drone.serial_number if m.drone else '',
                m.get_maintenance_type_display(),
                m.get_status_display(),
                m.performed_by.username if m.performed_by else '',
                m.scheduled_date.strftime('%d.%m.%Y %H:%M') if m.scheduled_date else '',
                m.completed_date.strftime('%d.%m.%Y %H:%M') if m.completed_date else '',
                m.cost,
                m.description,
            ])
        return response


# ============================================================
# ADMIN: ОГЛЯДИ
# ============================================================

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
    actions = ['export_csv']

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
        colors = {
            'passed':  ('green',   'Пройшов'),
            'warning': ('#fd7e14', 'З попередженнями'),
            'failed':  ('#dc3545', 'Не пройшов'),
        }
        color, label = colors.get(obj.result, ('#6c757d', obj.result))
        return format_html(
            '<span style="padding:4px 12px;background:{};color:#fff;border-radius:12px;'
            'font-size:0.82em;font-weight:600;letter-spacing:.4px">{}</span>',
            color, label,
        )
    result_badge.short_description = 'Результат'
    result_badge.admin_order_field = 'result'

    def battery_bar(self, obj):
        pct = obj.battery_health
        color = '#22c55e' if pct >= 70 else ('#f97316' if pct >= 40 else '#ef4444')
        # Ширина тексту: при pct < 20 — показуємо текст поруч
        bar_text   = f'{pct}%' if pct >= 20 else ''
        after_text = f'{pct}%' if pct < 20 else ''
        return format_html(
            '<div style="display:flex;align-items:center;gap:6px">'
            '<div style="width:90px;background:#e9ecef;border-radius:6px;overflow:hidden;'
            'box-shadow:inset 0 1px 3px rgba(0,0,0,.2)">'
            '<div style="width:{pct}%;background:{color};height:16px;text-align:center;'
            'font-size:10px;font-weight:700;color:#fff;line-height:16px;'
            'transition:width .3s">{bar_text}</div>'
            '</div>'
            '<span style="font-size:11px;color:{color};font-weight:600">{after_text}</span>'
            '</div>',
            pct=pct, color=color, bar_text=bar_text, after_text=after_text,
        )
    battery_bar.short_description = 'Батарея'
    battery_bar.admin_order_field = 'battery_health'

    def components_summary(self, obj):
        status_icons = {
            'ok':      ('fa-circle-check',        '#22c55e'),
            'warning': ('fa-triangle-exclamation', '#f97316'),
            'failed':  ('fa-circle-xmark',         '#ef4444'),
        }
        parts = [
            ('Мотор',    obj.motor_status),
            ('Пропелер', obj.propeller_condition),
            ('Камера',   obj.camera_status),
            ('Гімбал',   obj.gimbal_status),
        ]
        spans = []
        for label, status in parts:
            icon, color = status_icons.get(status, ('fa-circle-question', '#9ca3af'))
            spans.append(format_html(
                '<span title="{}: {}" style="color:{};margin-right:5px;cursor:default">'
                '<i class="fas {}" style="font-size:1.2em;vertical-align:middle"></i>'
                '</span>',
                label, status, color, icon,
            ))
        return mark_safe(''.join(spans))
    components_summary.short_description = 'Компоненти (М П К Г)'

    @admin.action(description='Експортувати звіт в CSV')
    def export_csv(self, request, queryset):
        response = _csv_response('inspections_report.csv')
        w = csv.writer(response)
        w.writerow([
            'Дрон', 'Дата огляду', 'Інспектор', 'Результат',
            'Заряд батареї (%)', 'Мотор', 'Пропелер', 'Камера', 'Гімбал',
            'Виявлені проблеми', 'Рекомендації',
        ])
        for ins in queryset.select_related('drone'):
            w.writerow([
                ins.drone.serial_number if ins.drone else '',
                ins.inspection_date.strftime('%d.%m.%Y %H:%M') if ins.inspection_date else '',
                ins.inspector_name,
                ins.get_result_display(),
                ins.battery_health,
                ins.get_motor_status_display(),
                ins.get_propeller_condition_display(),
                ins.get_camera_status_display(),
                ins.get_gimbal_status_display(),
                ins.issues_found,
                ins.recommendations,
            ])
        return response
