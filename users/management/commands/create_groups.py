from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

# Базові ролі системи
GROUPS = [
    'Адміністратор',  # повний доступ
    'Оператор',       # CRUD дронів (власних)
    'Технік',         # CRUD обслуговування та оглядів
    'Спостерігач',    # тільки читання
]


class Command(BaseCommand):
    help = 'Створює базові групи ролей у системі'

    def handle(self, *args, **options):
        for name in GROUPS:
            group, created = Group.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  [+] Створено групу: {name}'))
            else:
                self.stdout.write(f'  [=] Вже існує: {name}')
        self.stdout.write(self.style.SUCCESS('Готово.'))
