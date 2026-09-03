import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    """
    In-app alert informing subscribers of releases, payments, and account status.
    """
    class NotificationType(models.TextChoices):
        PAYMENT_SUCCESS = 'PAYMENT_SUCCESS', 'Payment Received'
        SUBSCRIPTION_RENEWAL = 'SUBSCRIPTION_RENEWAL', 'Subscription Renewal'
        NEW_RELEASE = 'NEW_RELEASE', 'New Movie or Episode Available'
        RECOMMENDATION = 'RECOMMENDATION', 'Recommended For You'
        SECURITY_ALERT = 'SECURITY_ALERT', 'Security Alert'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices, default=NotificationType.SYSTEM_ALERT if hasattr(NotificationType, 'SYSTEM_ALERT') else NotificationType.PAYMENT_SUCCESS)
    title = models.CharField(max_length=200)
    message = models.TextField()
    target_url = models.CharField(max_length=255, default='/')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.email} (Read: {self.is_read})"
