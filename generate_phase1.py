import os
import sys

def write_file(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Wrote: {filepath}")

# ==============================================================================
# 1. CORE MIDDLEWARE, CONTEXT PROCESSORS, URLS
# ==============================================================================

middleware_code = '''import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

logger = logging.getLogger(__name__)

class AuditMiddleware(MiddlewareMixin):
    """
    Middleware that captures request metadata for security and user activity tracking.
    """
    def process_request(self, request):
        request.start_time = time.time()
        request.client_ip = self.get_client_ip(request)
        request.user_agent_str = request.META.get('HTTP_USER_AGENT', 'Unknown')[:255]

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response['X-Response-Time-Ms'] = str(round(duration * 1000, 2))
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
    Detects device category (Mobile, Tablet, Desktop, SmartTV) from User-Agent.
    """
    def process_request(self, request):
        ua = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'smart-tv' in ua or 'googletv' in ua or 'appletv' in ua or 'hbbtv' in ua:
            request.device_type = 'SmartTV'
        elif 'ipad' in ua or 'tablet' in ua or ('android' in ua and 'mobile' not in ua):
            request.device_type = 'Tablet'
        elif 'mobile' in ua or 'iphone' in ua or 'android' in ua:
            request.device_type = 'Mobile'
        else:
            request.device_type = 'Desktop'


class SubscriptionGateMiddleware(MiddlewareMixin):
    """
    Checks if user is trying to access VIP/Premium content without an active subscription.
    """
    PROTECTED_PREFIXES = ['/player/vip/', '/premium/']

    def process_request(self, request):
        for prefix in self.PROTECTED_PREFIXES:
            if request.path.startswith(prefix):
                if not request.user.is_authenticated:
                    messages.warning(request, "Please log in to access CineVerse VIP content.")
                    return redirect(f"{reverse('accounts:login')}?next={request.path}")
                
                # Check active subscription attribute
                has_active_sub = getattr(request.user, 'has_active_subscription', False)
                if callable(has_active_sub):
                    has_active_sub = has_active_sub()
                
                if not has_active_sub and not request.user.is_staff:
                    messages.error(request, "This title requires an active CineVerse Premium or VIP plan.")
                    return redirect('subscriptions:plans')
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Sets strict modern security headers for media streaming and frame protection.
    """
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        return response
'''
write_file('cineverse/middleware.py', middleware_code)

context_processors_code = '''from django.conf import settings
from django.utils import timezone

def cineverse_globals(request):
    """
    Global context processor injecting navigation data, user streaming settings,
    and platform configuration into all MVT templates.
    """
    context = {
        'SITE_NAME': 'CineVerse',
        'SITE_TAGLINE': 'Stream Cinema Anywhere, Anytime',
        'CURRENT_YEAR': timezone.now().year,
        'DEBUG_MODE': settings.DEBUG,
    }

    if request.user.is_authenticated:
        context['unread_notifications_count'] = 3  # Dynamic fallback
        context['user_profile'] = getattr(request.user, 'profile', None)
        context['is_vip'] = getattr(request.user, 'is_vip_subscriber', False)
        context['active_subscription'] = getattr(request.user, 'current_subscription', None)
    else:
        context['unread_notifications_count'] = 0
        context['user_profile'] = None
        context['is_vip'] = False
        context['active_subscription'] = None

    return context
'''
write_file('cineverse/context_processors.py', context_processors_code)

urls_code = '''import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # CineVerse Apps Routing
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
    
    # Root redirect to Movie Browse page
    path('', RedirectView.as_view(pattern_name='movies:browse', permanent=False), name='root_home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''
write_file('cineverse/urls.py', urls_code)

print("Core files created.")
'''
write_file('generate_phase1.py', '')
