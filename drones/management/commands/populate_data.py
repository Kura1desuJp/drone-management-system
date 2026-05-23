from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from drones.models import Drone, Maintenance, Inspection
from datetime import datetime, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Заповнити базу тестовими даними для демонстрації'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Заповнення тестових даних...'))

        # Створити адміна якщо не існує
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@drone.local',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✅ Адміністратор створен'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Адміністратор вже існує'))

        # Створити тестові користувачі
        tech_user, _ = User.objects.get_or_create(
            username='tech_ivan',
            defaults={
                'email': 'ivan@drone.local',
                'first_name': 'Іван',
                'last_name': 'Петренко',
            }
        )
        tech_user2, _ = User.objects.get_or_create(
            username='tech_maria',
            defaults={
                'email': 'maria@drone.local',
                'first_name': 'Марія',
                'last_name': 'Сидоренко',
            }
        )
        self.stdout.write(self.style.SUCCESS('✅ Користувачі створені'))

        # Створити дрони
        drones_data = [
            {
                'model_name': 'DJI Phantom 4 Pro',
                'serial_number': 'SN-001-DJI-P4P',
                'status': 'active',
                'hours_flown': 245.5,
                'purchase_date': datetime(2022, 3, 15).date(),
                'max_flight_time': 30,
                'weight': 1375.0,
                'owner': admin_user,
            },
            {
                'model_name': 'DJI Mavic 3',
                'serial_number': 'SN-002-DJI-M3',
                'status': 'active',
                'hours_flown': 128.3,
                'purchase_date': datetime(2023, 6, 20).date(),
                'max_flight_time': 46,
                'weight': 920.0,
                'owner': admin_user,
            },
            {
                'model_name': 'Auterion Skynode',
                'serial_number': 'SN-003-AUT-SN',
                'status': 'repair',
                'hours_flown': 512.0,
                'purchase_date': datetime(2021, 1, 10).date(),
                'max_flight_time': 60,
                'weight': 2500.0,
                'owner': tech_user,
            },
            {
                'model_name': 'Parrot Anafi',
                'serial_number': 'SN-004-PAR-AF',
                'status': 'active',
                'hours_flown': 89.7,
                'purchase_date': datetime(2023, 9, 5).date(),
                'max_flight_time': 25,
                'weight': 320.0,
                'owner': tech_user,
            },
            {
                'model_name': 'DJI Air 3S',
                'serial_number': 'SN-005-DJI-A3S',
                'status': 'storage',
                'hours_flown': 0.0,
                'purchase_date': datetime(2024, 2, 1).date(),
                'max_flight_time': 46,
                'weight': 750.0,
                'owner': admin_user,
            },
        ]

        drones = {}
        for drone_data in drones_data:
            drone, created = Drone.objects.get_or_create(
                serial_number=drone_data['serial_number'],
                defaults=drone_data
            )
            drones[drone_data['serial_number']] = drone
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Дрон створен: {drone.model_name}'))

        # Створити запис обслуговування
        maintenance_data = [
            {
                'drone': drones['SN-001-DJI-P4P'],
                'maintenance_type': 'routine',
                'description': 'Планове обслуговування: перевірка моторів, очищення камери, оновлення прошивки',
                'performed_by': tech_user,
                'scheduled_date': datetime.now() - timedelta(days=5),
                'completed_date': datetime.now() - timedelta(days=4),
                'status': 'completed',
                'cost': Decimal('1500.00'),
            },
            {
                'drone': drones['SN-002-DJI-M3'],
                'maintenance_type': 'repair',
                'description': 'Ремонт гімбалу після падіння. Заміна механізму.',
                'performed_by': tech_user2,
                'scheduled_date': datetime.now() - timedelta(days=10),
                'completed_date': datetime.now() - timedelta(days=8),
                'status': 'completed',
                'cost': Decimal('3200.00'),
            },
            {
                'drone': drones['SN-003-AUT-SN'],
                'maintenance_type': 'repair',
                'description': 'Заміна батареї та електроніки. Серйозна поломка.',
                'performed_by': tech_user2,
                'scheduled_date': datetime.now() - timedelta(days=2),
                'completed_date': None,
                'status': 'in_progress',
                'cost': Decimal('5800.00'),
            },
            {
                'drone': drones['SN-004-PAR-AF'],
                'maintenance_type': 'inspection',
                'description': 'Периодична технічна експертиза перед сезонними польотами',
                'performed_by': tech_user,
                'scheduled_date': datetime.now() + timedelta(days=3),
                'completed_date': None,
                'status': 'scheduled',
                'cost': Decimal('800.00'),
            },
        ]

        for maint_data in maintenance_data:
            maint, created = Maintenance.objects.get_or_create(
                drone=maint_data['drone'],
                scheduled_date=maint_data['scheduled_date'],
                defaults=maint_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Запис обслуговування створен для {maint.drone.model_name}'))

        # Створити огляди
        inspection_data = [
            {
                'drone': drones['SN-001-DJI-P4P'],
                'inspector_name': 'Іван Петренко',
                'battery_health': 92,
                'motor_status': 'ok',
                'propeller_condition': 'ok',
                'camera_status': 'ok',
                'gimbal_status': 'ok',
                'issues_found': 'Нічого не знайдено',
                'result': 'passed',
                'recommendations': 'Дрон у відмінному стані. Продовжувати регулярне обслуговування.',
            },
            {
                'drone': drones['SN-002-DJI-M3'],
                'inspector_name': 'Марія Сидоренко',
                'battery_health': 78,
                'motor_status': 'warning',
                'propeller_condition': 'warning',
                'camera_status': 'ok',
                'gimbal_status': 'warning',
                'issues_found': 'Пропелери мають мікротріщини. Гімбал слабко рухається.',
                'result': 'warning',
                'recommendations': 'Замінити пропелери та оцінити гімбал. Рекомендується сервіс.',
            },
            {
                'drone': drones['SN-004-PAR-AF'],
                'inspector_name': 'Іван Петренко',
                'battery_health': 95,
                'motor_status': 'ok',
                'propeller_condition': 'ok',
                'camera_status': 'ok',
                'gimbal_status': '',
                'issues_found': '',
                'result': 'passed',
                'recommendations': 'Готовий до використання.',
            },
        ]

        for insp_data in inspection_data:
            insp, created = Inspection.objects.get_or_create(
                drone=insp_data['drone'],
                inspection_date=datetime.now() - timedelta(days=1),
                defaults={
                    **insp_data,
                    'inspection_date': datetime.now() - timedelta(days=1),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Огляд створен для {insp.drone.model_name}'))

        self.stdout.write(self.style.SUCCESS('\n✨ Всі тестові дані завантажені успішно!\n'))
        self.stdout.write(self.style.WARNING('📊 Статистика:'))
        self.stdout.write(f'   - Дронів: {Drone.objects.count()}')
        self.stdout.write(f'   - Записів обслуговування: {Maintenance.objects.count()}')
        self.stdout.write(f'   - Оглядів: {Inspection.objects.count()}')
        self.stdout.write(f'   - Користувачів: {User.objects.count()}\n')
        self.stdout.write(self.style.SUCCESS('🚀 Тепер система готова до демонстрації!'))
