"""
Тести моделей: Drone, Maintenance, Inspection.
Перевіряємо коректність полів, валідаторів, str() та зв'язків між моделями.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from drones.models import Drone, Maintenance, Inspection


def make_user(username='testuser', password='pass123'):
    return User.objects.create_user(username=username, password=password)


def make_drone(owner, serial='SN-001', model='DJI Phantom 4', status='active', hours=0.0):
    return Drone.objects.create(
        model_name=model,
        serial_number=serial,
        status=status,
        hours_flown=hours,
        purchase_date='2024-01-15',
        owner=owner,
    )


# ============================================================
# DRONE
# ============================================================

class DroneModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.drone = make_drone(self.user)

    def test_str(self):
        self.assertEqual(str(self.drone), 'DJI Phantom 4 (SN-001)')

    def test_default_status(self):
        self.assertEqual(self.drone.status, 'active')

    def test_default_max_flight_time(self):
        self.assertEqual(self.drone.max_flight_time, 30)

    def test_default_weight(self):
        self.assertEqual(self.drone.weight, 0)

    def test_serial_number_unique(self):
        with self.assertRaises(IntegrityError):
            make_drone(self.user, serial='SN-001', model='DJI Mavic')

    def test_hours_flown_cannot_be_negative(self):
        drone = Drone(
            model_name='Test',
            serial_number='SN-NEG',
            hours_flown=-1.0,
            purchase_date='2024-01-01',
            owner=self.user,
        )
        with self.assertRaises(ValidationError):
            drone.full_clean()

    def test_created_at_auto_set(self):
        self.assertIsNotNone(self.drone.created_at)

    def test_updated_at_changes_on_save(self):
        old_updated = self.drone.updated_at
        self.drone.hours_flown = 50
        self.drone.save()
        self.drone.refresh_from_db()
        self.assertGreaterEqual(self.drone.updated_at, old_updated)

    def test_ordering_newest_first(self):
        drone2 = make_drone(self.user, serial='SN-002', model='DJI Mavic')
        drones = list(Drone.objects.all())
        self.assertEqual(drones[0], drone2)

    def test_status_choices(self):
        valid_statuses = ['active', 'inactive', 'repair', 'storage']
        for s in valid_statuses:
            self.drone.status = s
            self.drone.full_clean()  # не повинно кидати помилки

    def test_owner_relationship(self):
        self.assertEqual(self.drone.owner, self.user)
        self.assertIn(self.drone, self.user.drones.all())


# ============================================================
# MAINTENANCE
# ============================================================

class MaintenanceModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.drone = make_drone(self.user)
        self.maintenance = Maintenance.objects.create(
            drone=self.drone,
            maintenance_type='routine',
            description='Планове технічне обслуговування',
            scheduled_date='2024-06-01T10:00:00Z',
            status='scheduled',
        )

    def test_str_contains_serial_and_type(self):
        result = str(self.maintenance)
        self.assertIn('SN-001', result)
        self.assertIn('Планове', result)

    def test_default_status(self):
        self.assertEqual(self.maintenance.status, 'scheduled')

    def test_default_cost_is_zero(self):
        self.assertEqual(self.maintenance.cost, 0)

    def test_completed_date_optional(self):
        self.assertIsNone(self.maintenance.completed_date)

    def test_performed_by_optional(self):
        self.assertIsNone(self.maintenance.performed_by)

    def test_drone_cascade_delete(self):
        drone_id = self.drone.id
        maint_id = self.maintenance.id
        self.drone.delete()
        self.assertFalse(Maintenance.objects.filter(id=maint_id).exists())

    def test_cost_cannot_be_negative(self):
        maint = Maintenance(
            drone=self.drone,
            maintenance_type='repair',
            description='Ремонт',
            scheduled_date='2024-07-01T00:00:00Z',
            cost=-100,
        )
        with self.assertRaises(ValidationError):
            maint.full_clean()

    def test_maintenance_type_choices(self):
        for t in ['routine', 'repair', 'inspection', 'upgrade']:
            self.maintenance.maintenance_type = t
            self.maintenance.full_clean()


# ============================================================
# INSPECTION
# ============================================================

class InspectionModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.drone = make_drone(self.user)
        self.inspection = Inspection.objects.create(
            drone=self.drone,
            inspector_name='Іван Петренко',
            battery_health=85,
            motor_status='ok',
            propeller_condition='ok',
            camera_status='ok',
            gimbal_status='ok',
            result='passed',
        )

    def test_str_contains_serial(self):
        self.assertIn('SN-001', str(self.inspection))

    def test_inspection_date_auto_set(self):
        self.assertIsNotNone(self.inspection.inspection_date)

    def test_default_component_statuses(self):
        insp = Inspection.objects.create(
            drone=self.drone,
            inspector_name='Test',
            battery_health=100,
            result='passed',
        )
        self.assertEqual(insp.motor_status, 'ok')
        self.assertEqual(insp.propeller_condition, 'ok')
        self.assertEqual(insp.camera_status, 'ok')

    def test_battery_health_max_100(self):
        insp = Inspection(
            drone=self.drone,
            inspector_name='Test',
            battery_health=150,
            result='passed',
        )
        with self.assertRaises(ValidationError):
            insp.full_clean()

    def test_battery_health_min_0(self):
        insp = Inspection(
            drone=self.drone,
            inspector_name='Test',
            battery_health=-5,
            result='passed',
        )
        with self.assertRaises(ValidationError):
            insp.full_clean()

    def test_result_choices(self):
        for r in ['passed', 'failed', 'warning']:
            self.inspection.result = r
            self.inspection.full_clean()

    def test_issues_found_optional(self):
        self.assertEqual(self.inspection.issues_found, '')

    def test_drone_cascade_delete(self):
        insp_id = self.inspection.id
        self.drone.delete()
        self.assertFalse(Inspection.objects.filter(id=insp_id).exists())

    def test_ordering_newest_first(self):
        insp2 = Inspection.objects.create(
            drone=make_drone(self.user, serial='SN-002'),
            inspector_name='Другий',
            battery_health=70,
            result='warning',
        )
        inspections = list(Inspection.objects.all())
        self.assertEqual(inspections[0], insp2)
