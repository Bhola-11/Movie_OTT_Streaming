import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class AuditEntry(models.Model):
    """
    Security and administrative audit trail recording critical platform mutations.
    """
    class ActionChoices(models.TextChoices):
        USER_LOGIN = 'USER_LOGIN', 'User Sign In'
        USER_REGISTER = 'USER_REGISTER', 'User Registration'
        SUBSCRIPTION_UPGRADE = 'SUBSCRIPTION_UPGRADE', 'Subscription Upgraded'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Password Reset Initiated'
        CONTENT_PUBLISHED = 'CONTENT_PUBLISHED', 'Content Published'
        REPORT_RESOLVED = 'REPORT_RESOLVED', 'Moderation Report Resolved'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_actions')
    action = models.CharField(max_length=50, choices=ActionChoices.choices, default=ActionChoices.USER_LOGIN)
    details = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Audit Entries'

    def __str__(self):
        actor_email = self.actor.email if self.actor else 'System'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {actor_email} -> {self.action}"
