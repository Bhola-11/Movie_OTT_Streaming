import uuid
from django.utils import timezone
from .models import UserDevice, LoginHistory, SecurityLog

class AuthService:
    """
    Encapsulates session creation, device registration, and security logging.
    """
    @staticmethod
    def register_login_event(request, user, status='SUCCESS'):
        ip = getattr(request, 'client_ip', '127.0.0.1')
        ua = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        LoginHistory.objects.create(
            user=user,
            ip_address=ip,
            user_agent=ua[:500],
            status=status,
            login_time=timezone.now()
        )

        # Update last active timestamp
        user.last_active_at = timezone.now()
        user.save(update_fields=['last_active_at'])

        # Register or refresh device
        device_id = request.COOKIES.get('cineverse_device_id') or str(uuid.uuid4())
        device_type = getattr(request, 'device_category', 'Desktop')
        
        device, _ = UserDevice.objects.get_or_create(
            user=user,
            device_id=device_id,
            defaults={
                'device_name': f"{device_type} - {ua.split('(')[0].strip()[:50]}",
                'device_type': device_type,
                'ip_address': ip,
                'last_used_at': timezone.now()
            }
        )
        if not _:
            device.last_used_at = timezone.now()
            device.ip_address = ip
            device.save(update_fields=['last_used_at', 'ip_address'])

        return device_id

    @staticmethod
    def log_security_event(user, event_type, description, ip='127.0.0.1'):
        SecurityLog.objects.create(
            user=user,
            event_type=event_type,
            description=description,
            ip_address=ip
        )
