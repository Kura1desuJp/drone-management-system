from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# ============================================================
# МОДЕЛЬ: ДРОН
# ============================================================
class Drone(models.Model):
    """
    Модель для зберігання інформації про дрони.
    """
    
    # Статус дрона
    STATUS_CHOICES = [
        ('active', 'Активний'),
        ('inactive', 'Неактивний'),
        ('repair', 'На ремонті'),
        ('storage', 'На зберіганні'),
    ]
    
    # Основні поля
    model_name = models.CharField(
        max_length=100,
        verbose_name='Модель дрона',
        help_text='Наприклад: DJI Phantom 4, DJI Mavic 3'
    )
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Серійний номер',
        help_text='Унікальний серійний номер дрона'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Статус'
    )
    hours_flown = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Години льоту',
        help_text='Загальна кількість годин польотів'
    )
    purchase_date = models.DateField(
        verbose_name='Дата покупки'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='Власник',
        related_name='drones'
    )
    
    # Технічні характеристики
    max_flight_time = models.IntegerField(
        default=30,
        verbose_name='Макс. час польоту (хв)',
        help_text='Максимальний час польоту у хвилинах'
    )
    weight = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Вага (г)',
        help_text='Вага дрона в грамах'
    )
    
    # Системні поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    
    class Meta:
        verbose_name = 'Дрон'
        verbose_name_plural = 'Дрони'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.model_name} ({self.serial_number})"


# ============================================================
# МОДЕЛЬ: ОБСЛУГОВУВАННЯ
# ============================================================
class Maintenance(models.Model):
    """
    Модель для реєстрації робіт з обслуговування та ремонту дрона.
    """
    
    TYPE_CHOICES = [
        ('routine', 'Планове обслуговування'),
        ('repair', 'Ремонт'),
        ('inspection', 'Експертиза'),
        ('upgrade', 'Модернізація'),
    ]
    
    STATUS_CHOICES = [
        ('scheduled', 'Заплановане'),
        ('in_progress', 'У процесі'),
        ('completed', 'Завершене'),
        ('failed', 'Не виконане'),
    ]
    
    # Основні поля
    drone = models.ForeignKey(
        Drone,
        on_delete=models.CASCADE,
        verbose_name='Дрон',
        related_name='maintenance_records'
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Тип обслуговування'
    )
    description = models.TextField(
        verbose_name='Опис робіт',
        help_text='Детальне описання того, що було зроблено'
    )
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Виконано',
        related_name='maintenance_performed',
        help_text='Технік хто виконав роботи'
    )
    
    # Дати
    scheduled_date = models.DateTimeField(
        verbose_name='Запланована дата'
    )
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Дата завершення'
    )
    
    # Статус та вартість
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Статус'
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Вартість (грн)',
        help_text='Вартість обслуговування'
    )
    
    # Системні поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')
    
    class Meta:
        verbose_name = 'Обслуговування'
        verbose_name_plural = 'Обслуговування'
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['drone', 'status']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.drone.serial_number} - {self.get_maintenance_type_display()}"


# ============================================================
# МОДЕЛЬ: ОГЛЯД/ДІАГНОСТИКА
# ============================================================
class Inspection(models.Model):
    """
    Модель для запису результатів технічного огляду та діагностики дрона.
    """
    
    RESULT_CHOICES = [
        ('passed', 'Пройшов огляд'),
        ('failed', 'Не пройшов'),
        ('warning', 'З попередженнями'),
    ]
    
    COMPONENT_STATUS = [
        ('ok', 'OK'),
        ('warning', 'Попередження'),
        ('failed', 'Несправний'),
    ]
    
    # Основні поля
    drone = models.ForeignKey(
        Drone,
        on_delete=models.CASCADE,
        verbose_name='Дрон',
        related_name='inspections'
    )
    inspection_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата огляду'
    )
    inspector_name = models.CharField(
        max_length=100,
        verbose_name='Ім\'я інспектора'
    )
    
    # Стан компонентів
    battery_health = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='Здоров\'я батареї (%)'
    )
    motor_status = models.CharField(
        max_length=20,
        choices=COMPONENT_STATUS,
        default='ok',
        verbose_name='Стан моторів'
    )
    propeller_condition = models.CharField(
        max_length=20,
        choices=COMPONENT_STATUS,
        default='ok',
        verbose_name='Стан пропелерів'
    )
    camera_status = models.CharField(
        max_length=20,
        choices=COMPONENT_STATUS,
        default='ok',
        verbose_name='Стан камери'
    )
    gimbal_status = models.CharField(
        max_length=20,
        choices=COMPONENT_STATUS,
        default='ok',
        verbose_name='Стан підвісу',
        blank=True
    )
    
    # Результати
    issues_found = models.TextField(
        blank=True,
        verbose_name='Знайдені проблеми',
        help_text='Детальний список виявлених проблем'
    )
    result = models.CharField(
        max_length=20,
        choices=RESULT_CHOICES,
        verbose_name='Результат огляду'
    )
    
    # Рекомендації
    recommendations = models.TextField(
        blank=True,
        verbose_name='Рекомендації',
        help_text='Рекомендовані дії'
    )
    
    # Системні поля
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')
    
    class Meta:
        verbose_name = 'Огляд'
        verbose_name_plural = 'Огляди'
        ordering = ['-inspection_date']
        indexes = [
            models.Index(fields=['drone', 'result']),
            models.Index(fields=['inspection_date']),
        ]
    
    def __str__(self):
        return f"Огляд {self.drone.serial_number} - {self.inspection_date.date()}"
