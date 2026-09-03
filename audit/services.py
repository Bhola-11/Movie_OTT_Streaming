from django.utils import timezone
from .models import AuditEntry

class AuditLoggerService:
    @staticmethod
    def log_action(actor, action_type, details, ip_address='127.0.0.1'):
        return AuditEntry.objects.create(
            actor=actor,
            action=action_type,
            details=details,
            ip_address=ip_address,
            timestamp=timezone.now()
        )
