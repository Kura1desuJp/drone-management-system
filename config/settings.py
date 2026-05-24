import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-test-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'drones',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ====== БАЗА ДАНИХ SQLite ======
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'uk-ua'  # Українська мова
TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ====== Jazzmin Admin Theme ======
JAZZMIN_SETTINGS = {
    # ── Заголовки та брендинг ──────────────────────────
    "site_title": "DroneMS Admin",
    "site_header": "Система управління дронами",
    "site_brand": "✈ DroneMS",
    "site_logo": None,
    "login_logo": None,
    "site_icon": None,
    "welcome_sign": "Вітаємо в системі обліку та ТО дронів",
    "copyright": "DroneMS © 2026",

    # ── Глобальний пошук ───────────────────────────────
    "search_model": ["drones.drone", "drones.maintenance", "drones.inspection", "auth.user"],
    "user_avatar": None,

    # ── Верхнє меню ────────────────────────────────────
    "topmenu_links": [
        {"name": "Головна", "url": "admin:index"},
        {"name": "Дрони",   "url": "admin:drones_drone_changelist",       "new_window": False},
        {"name": "ТО",      "url": "admin:drones_maintenance_changelist", "new_window": False},
        {"name": "Огляди",  "url": "admin:drones_inspection_changelist",  "new_window": False},
        {"name": "SPA →",   "url": "/", "new_window": True},
    ],

    # ── Меню користувача (аватар) ──────────────────────
    "usermenu_links": [
        {"name": "Мій профіль", "url": "/admin/profile/", "new_window": False},
        {"name": "SPA →", "url": "/", "new_window": True},
    ],

    # ── Сайдбар ───────────────────────────────────────
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],

    # ── Порядок розділів у сайдбарі ───────────────────
    "order_with_respect_to": [
        "drones",
        "auth",
        "users",
    ],

    # ── Іконки (Font Awesome 6 Free) ──────────────────
    "icons": {
        "auth":                 "fas fa-shield-halved",
        "auth.user":            "fas fa-user-circle",
        "auth.Group":           "fas fa-users",
        "drones":               "fas fa-helicopter",
        "drones.drone":         "fas fa-helicopter",
        "drones.maintenance":   "fas fa-screwdriver-wrench",
        "drones.inspection":    "fas fa-magnifying-glass",
        "users":                "fas fa-users-gear",
        "users.user":           "fas fa-user",
        "users.group":          "fas fa-users",
    },

    "default_icon_parents":  "fas fa-folder",
    "default_icon_children": "fas fa-circle-dot",

    # ── Форми ─────────────────────────────────────────
    "related_modal_active": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "auth.user":        "collapsible",
        "auth.group":       "vertical_tabs",
        "drones.drone":     "horizontal_tabs",
        "drones.maintenance": "horizontal_tabs",
        "drones.inspection":  "horizontal_tabs",
    },

    # ── Custom CSS/JS ──────────────────────────────────
    "custom_css": "drones/admin_custom.css",
    "custom_js":  None,

    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    # ── Текстові розміри ───────────────────────────────
    "navbar_small_text":        False,
    "footer_small_text":        True,
    "body_small_text":          False,
    "brand_small_text":         False,

    # ── Кольорова схема ────────────────────────────────
    "brand_colour":             "navbar-primary",
    "accent":                   "accent-primary",
    "navbar":                   "navbar-dark",
    "no_navbar_border":         False,
    "navbar_fixed":             True,

    # ── Сайдбар ───────────────────────────────────────
    "sidebar_fixed":            True,
    "sidebar":                  "sidebar-dark-primary",
    "sidebar_nav_small_text":   False,
    "sidebar_disable_expand":   False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style":   False,

    # ── Лейаут ────────────────────────────────────────
    "layout_boxed":             False,
    "footer_fixed":             False,

    # ── Тема ──────────────────────────────────────────
    "theme":                    "flatly",
    "dark_mode_theme":          "darkly",

    # ── Кнопки ────────────────────────────────────────
    "button_classes": {
        "primary":   "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info":      "btn-info",
        "warning":   "btn-warning",
        "danger":    "btn-danger",
        "success":   "btn-success",
    },
}

# ====== REST Framework ======
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
