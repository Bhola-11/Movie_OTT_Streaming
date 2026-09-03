import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created: {filepath}")

# manage.py
write('manage.py', '''#!/usr/bin/env python
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
''')

# cineverse/__init__.py
write('cineverse/__init__.py', '''from .celery import app as celery_app
__all__ = ('celery_app',)
''')

# cineverse/celery.py
write('cineverse/celery.py', '''import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')

app = Celery('cineverse')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Celery Request: {self.request!r}')
''')

# cineverse/wsgi.py
write('cineverse/wsgi.py', '''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
application = get_wsgi_application()
''')

# cineverse/asgi.py
write('cineverse/asgi.py', '''import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
application = get_asgi_application()
''')

# cineverse/settings.py
write('cineverse/settings.py', '''import os
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
    
    # CineVerse Core Domain Apps
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

SESSION_COOKIE_AGE = 86400 * 30
SESSION_SAVE_EVERY_REQUEST = True

# Payment Gateways Simulation
RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_cineverse123')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'mock_secret_cineverse_key')

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Email Backend for Notifications
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@cineverse-streaming.io'
''')

# cineverse/middleware.py
write('cineverse/middleware.py', '''import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

logger = logging.getLogger(__name__)

class AuditMiddleware(MiddlewareMixin):
    """
    Middleware that records telemetry, IP address, and execution duration for all HTTP requests.
    """
    def process_request(self, request):
        request.start_time = time.time()
        request.client_ip = self.get_client_ip(request)
        request.user_agent_str = request.META.get('HTTP_USER_AGENT', 'Unknown')[:255]

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Response-Time-Ms'] = str(round(duration * 1000, 2))
            response['X-CineVerse-Server'] = 'CineVerse-Node-Edge'
        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        return ip


class DeviceDetectMiddleware(MiddlewareMixin):
    """
    Classifies user client into Desktop, Mobile, Tablet, SmartTV, or Console.
    Used for video player bitrate adaptation and device restriction limits.
    """
    def process_request(self, request):
        ua = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(tv in ua for tv in ['smart-tv', 'googletv', 'appletv', 'hbbtv', 'tizen', 'webos', 'roku']):
            request.device_category = 'SmartTV'
        elif any(console in ua for console in ['playstation', 'xbox', 'nintendo']):
            request.device_category = 'Console'
        elif 'ipad' in ua or 'tablet' in ua or ('android' in ua and 'mobile' not in ua):
            request.device_category = 'Tablet'
        elif 'mobile' in ua or 'iphone' in ua or 'android' in ua:
            request.device_category = 'Mobile'
        else:
            request.device_category = 'Desktop'


class SubscriptionGateMiddleware(MiddlewareMixin):
    """
    Protects VIP and premium streaming routes against unverified or expired accounts.
    """
    PROTECTED_PREFIXES = ['/player/vip/', '/premium/exclusive/']

    def process_request(self, request):
        for prefix in self.PROTECTED_PREFIXES:
            if request.path.startswith(prefix):
                if not request.user.is_authenticated:
                    messages.warning(request, "Please sign in to access CineVerse VIP streams.")
                    return redirect(f"{reverse('accounts:login')}?next={request.path}")
                
                # Check VIP subscription
                is_vip = getattr(request.user, 'is_vip_subscriber', False)
                if not is_vip and not request.user.is_staff:
                    messages.info(request, "This 4K HDR stream is exclusive to CineVerse VIP members.")
                    return redirect('subscriptions:plans')
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Applies security headers preventing clickjacking, MIME-sniffing, and XSS.
    """
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        response['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
        return response
''')

# cineverse/context_processors.py
write('cineverse/context_processors.py', '''from django.conf import settings
from django.utils import timezone

def cineverse_globals(request):
    """
    Injects platform-wide configurations, genres, navigation links, and active subscriptions.
    """
    context = {
        'SITE_NAME': 'CineVerse',
        'SITE_TAGLINE': 'The Next-Gen Cinema & OTT Streaming Universe',
        'CURRENT_YEAR': timezone.now().year,
        'DEBUG_MODE': settings.DEBUG,
        'SUPPORTED_QUALITIES': ['4K UHD', '1080p FHD', '720p HD', '480p SD'],
        'NAV_CATEGORIES': [
            {'name': 'Movies', 'url_name': 'movies:browse'},
            {'name': 'TV Shows', 'url_name': 'series:browse'},
            {'name': 'Genres', 'url_name': 'genres:list'},
            {'name': 'People & Stars', 'url_name': 'people:list'},
            {'name': 'Plans & VIP', 'url_name': 'subscriptions:plans'},
        ],
    }

    if request.user.is_authenticated:
        context['unread_notifications_count'] = getattr(request.user, 'unread_notifications_count', 0)
        context['user_profile'] = getattr(request.user, 'profile', None)
        context['is_vip'] = getattr(request.user, 'is_vip_subscriber', False)
        context['active_subscription'] = getattr(request.user, 'current_subscription', None)
        context['watchlist_count'] = getattr(request.user, 'watchlist_count', 0)
    else:
        context['unread_notifications_count'] = 0
        context['user_profile'] = None
        context['is_vip'] = False
        context['active_subscription'] = None
        context['watchlist_count'] = 0

    return context
''')

# cineverse/urls.py
write('cineverse/urls.py', '''import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 18 App Routes
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('genres/', include('genres.urls', namespace='genres')),
    path('people/', include('people.urls', namespace='people')),
    path('movies/', include('movies.urls', namespace='movies')),
    path('series/', include('series.urls', namespace='series')),
    path('seasons/', include('seasons.urls', namespace='seasons')),
    path('episodes/', include('episodes.urls', namespace='episodes')),
    path('player/', include('player.urls', namespace='player')),
    path('history/', include('history.urls', namespace='history')),
    path('watchlist/', include('watchlist.urls', namespace='watchlist')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('recommendations/', include('recommendations.urls', namespace='recommendations')),
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('moderation/', include('moderation.urls', namespace='moderation')),
    path('audit/', include('audit.urls', namespace='audit')),
    
    # Homepage default redirect to movies catalog
    path('', RedirectView.as_view(pattern_name='movies:browse', permanent=False), name='root_home'),
]

if settings.DEBUG:
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
''')

print("build_core.py execution complete.")
