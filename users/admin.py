from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html, mark_safe


class DroneInline(admin.TabularInline):
    from drones.models import Drone
    model = Drone
    extra = 0
    fields = ['model_name', 'serial_number', 'status', 'hours_flown']
    readonly_fields = ['model_name', 'serial_number', 'status', 'hours_flown']
    show_change_link = True
    can_delete = False
    verbose_name_plural = 'Дрони користувача'


class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'full_name', 'is_staff_badge', 'is_active_badge', 'drone_count', 'date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    list_per_page = 25
    date_hierarchy = 'date_joined'
    inlines = [DroneInline]

    def full_name(self, obj):
        name = obj.get_full_name()
        return name if name else mark_safe('<span style="color:#aaa;font-style:italic">—</span>')
    full_name.short_description = "Повне ім'я"
    full_name.admin_order_field = 'first_name'

    def is_staff_badge(self, obj):
        if obj.is_superuser:
            return mark_safe('<span style="padding:3px 10px;background:#6f42c1;color:#fff;border-radius:12px;font-size:0.8em;font-weight:600">Супер</span>')
        if obj.is_staff:
            return mark_safe('<span style="padding:3px 10px;background:#007bff;color:#fff;border-radius:12px;font-size:0.8em;font-weight:600">Персонал</span>')
        return mark_safe('<span style="padding:3px 10px;background:#e9ecef;color:#555;border-radius:12px;font-size:0.8em">Користувач</span>')
    is_staff_badge.short_description = 'Роль'
    is_staff_badge.admin_order_field = 'is_staff'

    def is_active_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color:green;font-weight:600"><i class="fas fa-check-circle"></i> Активний</span>')
        return mark_safe('<span style="color:#dc3545;font-weight:600"><i class="fas fa-ban"></i> Заблокований</span>')
    is_active_badge.short_description = 'Стан'
    is_active_badge.admin_order_field = 'is_active'

    def drone_count(self, obj):
        count = obj.drones.count()
        color = '#007bff' if count > 0 else '#aaa'
        return format_html('<span style="color:{};font-weight:600"><i class="fas fa-helicopter"></i> {}</span>', color, count)
    drone_count.short_description = 'Дронів'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
