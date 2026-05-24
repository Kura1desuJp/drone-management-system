"""
Тести ролевої системи (RBAC).
Перевіряємо що кожна роль має рівно ті права які визначені в permissions.py:

  Спостерігач  → тільки читання
  Технік       → читання + запис maintenance & inspections (не видалення)
  Оператор     → читання + запис дронів (власних) (не видалення)
  Адміністратор → повний доступ
"""
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from drones.models import Drone, Maintenance, Inspection


# ── Хелпери ────────────────────────────────────────────────

def create_user_in_group(username, group_name):
    user = User.objects.create_user(username, password='pass123')
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)
    return user


def make_drone(owner, serial='SN-001'):
    return Drone.objects.create(
        model_name='DJI Test',
        serial_number=serial,
        purchase_date='2024-01-01',
        owner=owner,
        status='active',
        hours_flown=0,
    )


def make_maintenance(drone):
    return Maintenance.objects.create(
        drone=drone,
        maintenance_type='routine',
        description='Тест',
        scheduled_date='2024-06-01T00:00:00Z',
        status='scheduled',
    )


def make_inspection(drone):
    return Inspection.objects.create(
        drone=drone,
        inspector_name='Тест',
        battery_health=90,
        result='passed',
    )


# ============================================================
# СПОСТЕРІГАЧ — тільки читання
# ============================================================

class ViewerPermissionTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', password='pass')
        self.viewer = User.objects.create_user('viewer', password='pass')
        self.drone = make_drone(self.admin)
        self.maint = make_maintenance(self.drone)
        self.insp = make_inspection(self.drone)

    def test_viewer_can_read_drones(self):
        self.client.force_authenticate(user=self.viewer)
        r = self.client.get('/api/drones/drones/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_viewer_can_read_maintenance(self):
        self.client.force_authenticate(user=self.viewer)
        r = self.client.get('/api/drones/maintenance/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_viewer_can_read_inspections(self):
        self.client.force_authenticate(user=self.viewer)
        r = self.client.get('/api/drones/inspections/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_viewer_cannot_create_drone(self):
        self.client.force_authenticate(user=self.viewer)
        r = self.client.post('/api/drones/drones/', {
            'model_name': 'X', 'serial_number': 'V-001', 'purchase_date': '2024-01-01', 'hours_flown': 0,
        })
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_create_maintenance(self):
        self.client.force_authenticate(user=self.viewer)
        r = self.client.post('/api/drones/maintenance/', {
            'drone': self.drone.id, 'maintenance_type': 'routine',
            'description': 'X', 'scheduled_date': '2024-07-01T00:00:00Z',
        })
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_create_inspection(self):
        self.client.force_authenticate(user=self.viewer)
        r = self.client.post('/api/drones/inspections/', {
            'drone': self.drone.id, 'inspector_name': 'X', 'battery_health': 90, 'result': 'passed',
        })
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_delete_drone(self):
        self.client.force_authenticate(user=self.viewer)
        r = self.client.delete(f'/api/drones/drones/{self.drone.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_viewer_cannot_access_users_api(self):
        self.client.force_authenticate(user=self.viewer)
        r = self.client.get('/api/users/users/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


# ============================================================
# ТЕХНІК — CRUD maintenance & inspections, читання дронів
# ============================================================

class TechnicianPermissionTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', password='pass')
        self.technician = create_user_in_group('tech', 'Технік')
        self.drone = make_drone(self.admin)
        self.maint = make_maintenance(self.drone)
        self.insp = make_inspection(self.drone)

    def test_technician_can_read_drones(self):
        self.client.force_authenticate(user=self.technician)
        r = self.client.get('/api/drones/drones/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_technician_cannot_create_drone(self):
        self.client.force_authenticate(user=self.technician)
        r = self.client.post('/api/drones/drones/', {
            'model_name': 'X', 'serial_number': 'T-001',
            'purchase_date': '2024-01-01', 'hours_flown': 0,
        })
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_technician_can_create_maintenance(self):
        self.client.force_authenticate(user=self.technician)
        r = self.client.post('/api/drones/maintenance/', {
            'drone': self.drone.id,
            'maintenance_type': 'repair',
            'description': 'Ремонт мотора',
            'scheduled_date': '2024-08-01T10:00:00Z',
            'status': 'scheduled',
            'cost': 0,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_technician_can_update_maintenance(self):
        self.client.force_authenticate(user=self.technician)
        r = self.client.patch(
            f'/api/drones/maintenance/{self.maint.id}/',
            {'status': 'in_progress'},
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_technician_cannot_delete_maintenance(self):
        self.client.force_authenticate(user=self.technician)
        r = self.client.delete(f'/api/drones/maintenance/{self.maint.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_technician_can_create_inspection(self):
        self.client.force_authenticate(user=self.technician)
        r = self.client.post('/api/drones/inspections/', {
            'drone': self.drone.id,
            'inspector_name': 'Технік Тест',
            'battery_health': 78,
            'motor_status': 'ok',
            'result': 'passed',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_technician_cannot_delete_inspection(self):
        self.client.force_authenticate(user=self.technician)
        r = self.client.delete(f'/api/drones/inspections/{self.insp.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_technician_cannot_access_users_api(self):
        self.client.force_authenticate(user=self.technician)
        r = self.client.get('/api/users/users/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


# ============================================================
# ОПЕРАТОР — CRUD дронів (власних), читання інших
# ============================================================

class OperatorPermissionTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', password='pass')
        self.operator = create_user_in_group('oper', 'Оператор')
        self.other = User.objects.create_user('other', password='pass')

        # Дрон оператора
        self.own_drone = make_drone(self.operator, serial='SN-OWN')
        # Дрон іншого користувача
        self.other_drone = make_drone(self.other, serial='SN-OTHER')

        self.maint = make_maintenance(self.own_drone)
        self.insp = make_inspection(self.own_drone)

    def test_operator_can_create_drone(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.post('/api/drones/drones/', {
            'model_name': 'New Drone', 'serial_number': 'SN-NEW',
            'purchase_date': '2024-01-01', 'hours_flown': 0, 'status': 'active',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_operator_can_edit_own_drone(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.patch(
            f'/api/drones/drones/{self.own_drone.id}/',
            {'hours_flown': 25.0},
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_operator_cannot_edit_others_drone(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.patch(
            f'/api/drones/drones/{self.other_drone.id}/',
            {'hours_flown': 999.0},
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_operator_cannot_delete_drone(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.delete(f'/api/drones/drones/{self.own_drone.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_operator_can_read_maintenance(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.get('/api/drones/maintenance/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_operator_cannot_delete_maintenance(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.delete(f'/api/drones/maintenance/{self.maint.id}/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_operator_cannot_access_users_api(self):
        self.client.force_authenticate(user=self.operator)
        r = self.client.get('/api/users/users/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


# ============================================================
# АДМІНІСТРАТОР — повний доступ
# ============================================================

class AdminPermissionTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', password='pass')
        self.owner = User.objects.create_user('owner', password='pass')
        self.drone = make_drone(self.owner)
        self.maint = make_maintenance(self.drone)
        self.insp = make_inspection(self.drone)

    def test_admin_can_delete_drone(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.delete(f'/api/drones/drones/{self.drone.id}/')
        self.assertIn(r.status_code, [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK])

    def test_admin_can_delete_maintenance(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.delete(f'/api/drones/maintenance/{self.maint.id}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_delete_inspection(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.delete(f'/api/drones/inspections/{self.insp.id}/')
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_access_users_api(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/users/users/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_admin_can_access_groups_api(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/users/groups/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)
