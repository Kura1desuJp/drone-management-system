from rest_framework import serializers
from .models import Drone, Maintenance, Inspection


# ============================================================
# СЕРІАЛІЗАТОР: ДРОН
# ============================================================
class DroneSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для модел Drone.
    Включає всі основні поля та пов'язані дані.
    """
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Drone
        fields = [
            'id',
            'model_name',
            'serial_number',
            'status',
            'hours_flown',
            'purchase_date',
            'max_flight_time',
            'weight',
            'owner',
            'owner_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


# ============================================================
# СЕРІАЛІЗАТОР: ОБСЛУГОВУВАННЯ
# ============================================================
class MaintenanceSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для модель Maintenance.
    Включає детальну інформацію про робиці обслуговування.
    """
    drone_serial = serializers.CharField(source='drone.serial_number', read_only=True)
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Maintenance
        fields = [
            'id',
            'drone',
            'drone_serial',
            'maintenance_type',
            'description',
            'performed_by',
            'performed_by_username',
            'scheduled_date',
            'completed_date',
            'status',
            'cost',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================
# СЕРІАЛІЗАТОР: ОГЛЯД/ДІАГНОСТИКА
# ============================================================
class InspectionSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для модель Inspection.
    Включає результати технічного огляду та діагностики.
    """
    drone_serial = serializers.CharField(source='drone.serial_number', read_only=True)
    
    class Meta:
        model = Inspection
        fields = [
            'id',
            'drone',
            'drone_serial',
            'inspection_date',
            'inspector_name',
            'battery_health',
            'motor_status',
            'propeller_condition',
            'camera_status',
            'gimbal_status',
            'issues_found',
            'result',
            'recommendations',
            'created_at',
        ]
        read_only_fields = ['id', 'inspection_date', 'created_at']
