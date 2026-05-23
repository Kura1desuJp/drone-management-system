# Система обліку та технічного обслуговування дронів

Інформаційна система для управління дронами, реєстрації обслуговування та техніч огляд.

## 🚀 Старт

### 1. Встанов залежності

```bash
# Активуй віртуальне окружение
venv\Scripts\activate  # Windows

# Встанови залежності
pip install -r requirements.txt
```

### 2. Налашту базу даних

```bash
# Встанови PostgreSQL (якщо немає)
# https://www.postgresql.org/download/windows/

# Створи БД в psql
psql -U postgres
CREATE DATABASE drone_management;
```

### 3. Запусти міграції

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Створи супер-користувача (адміна)

```bash
python manage.py createsuperuser
```

### 5. Запусти сервер

```bash
python manage.py runserver
```

Адмін-панель: **http://localhost:8000/admin**

## 📋 Структура проекту

```
drone-management-system/
├── config/              # Конфігурація Django
├── drones/              # Додаток для дронів
│   ├── models.py        # Моделі DB
│   ├── admin.py         # Адмін-панель
│   └── urls.py
├── users/               # Додаток для користувачів
├── templates/           # HTML шаблони
├── manage.py            # Команди Django
├── requirements.txt     # Залежності
└── .env                 # Змінні окружения
```

## 🗄️ Сутності

- **Drone** - Інформація про дрон
- **Maintenance** - Обслуговування та ремонт
- **Inspection** - Технічний огляд/діагностика

## 📝 Коментарі

Весь код написаний із коментарями українською для зручності.
