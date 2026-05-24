"""
Тести endpoints авторизації та профілю користувача:
  POST /api/users/login/
  POST /api/users/logout/
  GET  /api/users/me/
  PATCH /api/users/me/
"""
from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status


class LoginViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='securepass123',
            email='test@drone.ua',
            is_active=True,
        )

    def test_login_success_returns_200(self):
        r = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'securepass123',
        })
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_login_success_returns_user_data(self):
        r = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'securepass123',
        })
        self.assertEqual(r.data['username'], 'testuser')
        self.assertNotIn('password', r.data)   # пароль не повертається

    def test_login_wrong_password_returns_401(self):
        r = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user_returns_401(self):
        r = self.client.post('/api/users/login/', {
            'username': 'nobody',
            'password': 'pass',
        })
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_empty_username_returns_400(self):
        r = self.client.post('/api/users/login/', {
            'username': '',
            'password': 'securepass123',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_empty_password_returns_400(self):
        r = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': '',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_body_returns_400(self):
        r = self.client.post('/api/users/login/', {})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user_returns_403(self):
        self.user.is_active = False
        self.user.save()
        r = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'securepass123',
        })
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_allowed_without_authentication(self):
        # endpoint відкритий (AllowAny)
        r = self.client.post('/api/users/login/', {
            'username': 'testuser',
            'password': 'securepass123',
        })
        self.assertNotEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class LogoutViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user('logoutuser', password='pass123')

    def test_logout_unauthenticated_returns_403(self):
        r = self.client.post('/api/users/logout/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_authenticated_returns_200(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.post('/api/users/logout/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_logout_response_has_detail(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.post('/api/users/logout/')
        self.assertIn('detail', r.data)


class MeViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='meuser',
            password='pass123',
            email='me@drone.ua',
            first_name='Іван',
            last_name='Дронов',
        )
        group, _ = Group.objects.get_or_create(name='Оператор')
        self.user.groups.add(group)

    # ── GET ────────────────────────────────────────────────
    def test_me_unauthenticated_returns_403(self):
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_returns_200(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_me_returns_correct_username(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.get('/api/users/me/')
        self.assertEqual(r.data['username'], 'meuser')

    def test_me_does_not_return_password(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.get('/api/users/me/')
        self.assertNotIn('password', r.data)

    # ── PATCH ──────────────────────────────────────────────
    def test_me_patch_updates_email(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.patch('/api/users/me/', {'email': 'new@drone.ua'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@drone.ua')

    def test_me_patch_updates_first_name(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.patch('/api/users/me/', {'first_name': 'Олег'})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Олег')

    def test_me_patch_cannot_escalate_is_staff(self):
        self.assertFalse(self.user.is_staff)
        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/users/me/', {'is_staff': True})
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)  # не повинно змінитись

    def test_me_patch_cannot_escalate_is_superuser(self):
        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/users/me/', {'is_superuser': True})
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_superuser)

    def test_me_patch_cannot_change_groups(self):
        initial_groups = list(self.user.groups.values_list('id', flat=True))
        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/users/me/', {'groups': []})
        self.user.refresh_from_db()
        current_groups = list(self.user.groups.values_list('id', flat=True))
        self.assertEqual(sorted(initial_groups), sorted(current_groups))

    def test_me_patch_cannot_deactivate_self(self):
        self.client.force_authenticate(user=self.user)
        self.client.patch('/api/users/me/', {'is_active': False})
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class UserManagementAPITest(APITestCase):
    """Перевіряємо що UserViewSet та GroupViewSet доступні лише адміну."""

    def setUp(self):
        self.admin = User.objects.create_superuser('admin', password='pass')
        self.regular = User.objects.create_user('regular', password='pass')

    def test_users_list_requires_admin(self):
        self.client.force_authenticate(user=self.regular)
        r = self.client.get('/api/users/users/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/users/users/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_admin_can_create_user(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/users/users/', {
            'username': 'newuser',
            'password': 'pass123456',
            'email': 'new@drone.ua',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_admin_can_list_groups(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.get('/api/users/groups/')
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_admin_can_create_group(self):
        self.client.force_authenticate(user=self.admin)
        r = self.client.post('/api/users/groups/', {'name': 'Тестова група'})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_regular_cannot_access_groups(self):
        self.client.force_authenticate(user=self.regular)
        r = self.client.get('/api/users/groups/')
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
