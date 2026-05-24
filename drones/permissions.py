from rest_framework.permissions import BasePermission, SAFE_METHODS


def _in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def _is_admin(user):
    return user.is_staff or user.is_superuser or _in_group(user, 'Адміністратор')


def _is_operator_or_above(user):
    return _is_admin(user) or _in_group(user, 'Оператор')


def _is_technician_or_above(user):
    return _is_operator_or_above(user) or _in_group(user, 'Технік')


class DronePermission(BasePermission):
    """
    Дрони:
    • читання   — всі авторизовані
    • запис     — Оператор та вище (або власник дрона)
    • видалення — лише Адміністратор
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE':
            return _is_admin(request.user)
        return _is_operator_or_above(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE':
            return _is_admin(request.user)
        # Оператор може редагувати лише власні дрони; адмін — будь-які
        return _is_admin(request.user) or (
            _in_group(request.user, 'Оператор') and obj.owner == request.user
        )


class MaintenancePermission(BasePermission):
    """
    Обслуговування:
    • читання   — всі авторизовані
    • запис     — Технік та вище
    • видалення — лише Адміністратор
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE':
            return _is_admin(request.user)
        return _is_technician_or_above(request.user)


class InspectionPermission(BasePermission):
    """
    Огляди:
    • читання   — всі авторизовані
    • запис     — Технік та вище
    • видалення — лише Адміністратор
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE':
            return _is_admin(request.user)
        return _is_technician_or_above(request.user)


class AdminOnlyPermission(BasePermission):
    """Повний доступ лише для Адміністраторів."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            _is_admin(request.user)
        )
