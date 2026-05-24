"""
Тести REST API endpoints: DroneViewSet, MaintenanceViewSet, InspectionViewSet.
Перевіряємо CRUD, custom actions, фільтрацію, пошук та пагінацію.
"""
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from drones.models import Drone, Maintenance, Inspection


# ── Хелпери ────────────────────────────────────────────────────────────────

def make_admin(username='admin'):
    return User.objects.create_superuser(username, password='adminpass')


def make_operator(username='operator'):
    user = User.objects.create_user(username, password='pass123')
    group, _ = Group.objects.get_or_create(name='Оператор')
    user.groups.add(group)
    return user


def make_drone(owner, serial='SN-001', status='active', hours=0.0):
    return Drone.objects.create(
        model_name='DJI Phantom 4',
        serial_number=serial,
        status=status,
        hours_flown=hours,
        purchase_date='2024-01-15',
        owner=owner,
    )


def make_maintenance(drone, mtype='routine', mstatus='scheduled'):
    return Maintenance.objects.create(
        drone=drone,
        maintenance_type=mtype,
        description='Тестове ТО',
        scheduled_date='2024-06-01T10:00:00Z',
        status=mstatus,
        cost=500,
    )


def make_inspection(drone, result='passed', battery=85):
    return Inspection.objects.create(
        drone=drone,
        inspector_name='Тест Інспектор',
        battery_health=battery,
        motor_status='ok',
        result=result,
    )


# ============================================================
# DRONE API
# ============================================================

class DroneAPITest(APITestCase):

    def setUp(self):
        self.admin = make_admin()
        self.operator = make_operator()
        self.drone = make_drone(self.admin)

    # ── Доступ ─────────────────────────────────────────────
    def test_unauthenticated_returns_403(self):
        r = self.client.get('/api/drones/drones/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_authenticated_can_list(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.get('/api/drones/drones/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('results', r.data)

    # ── Створення ──────────────────────────────────────────
    def test_operator_can_create(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.post('/api/drones/drones/', {
            'model_name': 'DJI Mavic 3',
            'serial_number': 'SN-002',
            'purchase_date': '2024-03-01',
            'status': 'active',
            'hours_flown': 0,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['serial_number'], 'SN-002')

    def test_perform_create_sets_owner(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.post('/api/drones/drones/', {
            'model_name': 'DJI Air',
            'serial_number': 'SN-003',
            'purchase_date': '2024-03-01',
            'status': 'active',
            'hours_flown': 0,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['owner'], self.operator.id)

    def test_duplicate_serial_returns_400(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/drones/drones/', {
            'model_name': 'DJI Mavic',
            'serial_number': 'SN-001',   # вже існує
            'purchase_date': '2024-01-01',
            'status': 'active',
            'hours_flown': 0,
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Читання ────────────────────────────────────────────
    def test_retrieve_single_drone(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get(f'/api/drones/drones/{self.drone.id}/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['serial_number'], 'SN-001')

    def test_404_for_nonexistent_drone(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/drones/99999/')
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    # ── Оновлення ──────────────────────────────────────────
    def test_patch_updates_hours(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.patch(f'/api/drones/drones/{self.drone.id}/', {'hours_flown': 150.5})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.drone.refresh_from_db()
        self.assertEqual(self.drone.hours_flown, 150.5)

    # ── Видалення ──────────────────────────────────────────
    def test_admin_can_delete(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.delete(f'/api/drones/drones/{self.drone.id}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Drone.objects.filter(id=self.drone.id).exists())

    # ── Custom actions ─────────────────────────────────────
    def test_active_drones_action(self):
        make_drone(self.admin, serial='SN-REPAIR', status='repair')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/drones/active_drones/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        serials = [d['serial_number'] for d in r.data]
        self.assertIn('SN-001', serials)
        self.assertNotIn('SN-REPAIR', serials)

    def test_mark_maintenance_sets_repair(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/drones/drones/{self.drone.id}/mark_maintenance/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.drone.refresh_from_db()
        self.assertEqual(self.drone.status, 'repair')

    def test_mark_active_sets_active(self):
        self.drone.status = 'repair'
        self.drone.save()
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/drones/drones/{self.drone.id}/mark_active/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.drone.refresh_from_db()
        self.assertEqual(self.drone.status, 'active')

    # ── Фільтрація / пошук ─────────────────────────────────
    def test_filter_by_status(self):
        make_drone(self.admin, serial='SN-STORAGE', status='storage')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/drones/?status=storage')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for d in r.data['results']:
            self.assertEqual(d['status'], 'storage')

    def test_search_by_serial(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/drones/?search=SN-001')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['serial_number'], 'SN-001')

    def test_pagination_returns_count(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/drones/')
        self.assertIn('count', r.data)
        self.assertIn('results', r.data)


# ============================================================
# MAINTENANCE API
# ============================================================

class MaintenanceAPITest(APITestCase):

    def setUp(self):
        self.admin = make_admin()
        self.drone = make_drone(self.admin)
        self.maintenance = make_maintenance(self.drone)

    def test_list_maintenance(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/maintenance/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 1)

    def test_create_maintenance(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/drones/maintenance/', {
            'drone': self.drone.id,
            'maintenance_type': 'repair',
            'description': 'Заміна пропелерів',
            'scheduled_date': '2024-08-01T09:00:00Z',
            'status': 'scheduled',
            'cost': 1200,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['maintenance_type'], 'repair')

    def test_pending_action(self):
        make_maintenance(self.drone, mstatus='completed')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/maintenance/pending/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for m in r.data:
            self.assertEqual(m['status'], 'scheduled')

    def test_completed_action(self):
        make_maintenance(self.drone, mstatus='completed')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/maintenance/completed/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for m in r.data:
            self.assertEqual(m['status'], 'completed')

    def test_mark_completed_action(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post(f'/api/drones/maintenance/{self.maintenance.id}/mark_completed/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.maintenance.refresh_from_db()
        self.assertEqual(self.maintenance.status, 'completed')
        self.assertEqual(self.maintenance.performed_by, self.admin)

    def test_filter_by_type(self):
        make_maintenance(self.drone, mtype='repair')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/maintenance/?maintenance_type=repair')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for m in r.data['results']:
            self.assertEqual(m['maintenance_type'], 'repair')


# ============================================================
# INSPECTION API
# ============================================================

class InspectionAPITest(APITestCase):

    def setUp(self):
        self.admin = make_admin()
        self.drone = make_drone(self.admin)
        self.inspection = make_inspection(self.drone, result='passed')

    def test_list_inspections(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/inspections/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 1)

    def test_create_inspection(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/drones/inspections/', {
            'drone': self.drone.id,
            'inspector_name': 'Олег Мороз',
            'battery_health': 92,
            'motor_status': 'ok',
            'propeller_condition': 'warning',
            'camera_status': 'ok',
            'gimbal_status': 'ok',
            'result': 'warning',
            'issues_found': 'Пропелер потребує заміни',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data['result'], 'warning')

    def test_passed_action(self):
        make_inspection(self.drone, result='failed')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/inspections/passed/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for i in r.data:
            self.assertEqual(i['result'], 'passed')

    def test_failed_action(self):
        make_inspection(self.drone, result='failed')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/inspections/failed/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(len(r.data) >= 1)

    def test_warnings_action(self):
        make_inspection(self.drone, result='warning')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/inspections/warnings/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for i in r.data:
            self.assertEqual(i['result'], 'warning')

    def test_filter_by_result(self):
        make_inspection(self.drone, result='failed')
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/inspections/?result=failed')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        for i in r.data['results']:
            self.assertEqual(i['result'], 'failed')

    def test_search_by_inspector_name(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/drones/inspections/?search=Тест+Інспектор')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(r.data['count'], 1)
