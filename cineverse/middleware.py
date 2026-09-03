import time
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
