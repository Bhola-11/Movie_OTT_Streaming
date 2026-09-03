import os
import sys

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created: {path}")

# 1. Manage.py
manage_py = """#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
"""
create_file('manage.py', manage_py)

# 2. cineverse/settings.py
settings_py = '''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-cineverse-50k-production-grade-streaming-secret-key-2026')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # CineVerse Apps
    'accounts.apps.AccountsConfig',
    'genres.apps.GenresConfig',
    'people.apps.PeopleConfig',
    'movies.apps.MoviesConfig',
    'series.apps.SeriesConfig',
    'seasons.apps.SeasonsConfig',
    'episodes.apps.EpisodesConfig',
    'player.apps.PlayerConfig',
    'history.apps.HistoryConfig',
    'watchlist.apps.WatchlistConfig',
    'reviews.apps.ReviewsConfig',
    'recommendations.apps.RecommendationsConfig',
    'subscriptions.apps.SubscriptionsConfig',
    'payments.apps.PaymentsConfig',
    'notifications.apps.NotificationsConfig',
    'analytics.apps.AnalyticsConfig',
    'moderation.apps.ModerationConfig',
    'audit.apps.AuditConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cineverse.middleware.AuditMiddleware',
    'cineverse.middleware.DeviceDetectMiddleware',
    'cineverse.middleware.SubscriptionGateMiddleware',
    'cineverse.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'cineverse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cineverse.context_processors.cineverse_globals',
            ],
        },
    },
]

WSGI_APPLICATION = 'cineverse.wsgi.application'
ASGI_APPLICATION = 'cineverse.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'movies:browse'
LOGOUT_REDIRECT_URL = 'movies:browse'

# Session settings
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
SESSION_SAVE_EVERY_REQUEST = True

# Razorpay / Mock Gateway settings
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_cineverse123')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'mock_secret_cineverse_key')

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
'''
create_file('cineverse/settings.py', settings_py)

# 3. cineverse/celery.py
celery_py = '''import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')

app = Celery('cineverse')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
'''
create_file('cineverse/celery.py', celery_py)

# 4. cineverse/wsgi.py & asgi.py
wsgi_py = '''import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
application = get_wsgi_application()
'''
create_file('cineverse/wsgi.py', wsgi_py)

asgi_py = '''import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
application = get_asgi_application()
'''
create_file('cineverse/asgi.py', asgi_py)
create_file('cineverse/__init__.py', 'from .celery import app as celery_app\n__all__ = ("celery_app",)\n')

print("Phase 1 Core Configuration Files Created.")
'''
create_file('build_phase1.py', '')
