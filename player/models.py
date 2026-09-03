import uuid
import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone

class StreamingToken(models.Model):
    """
    Time-limited cryptographically secure playback token protecting video URLs
    from direct scraping, link scraping, and hotlinking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streaming_tokens')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    content_type = models.CharField(max_length=20)  # 'MOVIE' or 'EPISODE'
    content_id = models.UUIDField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    expires_at = models.DateTimeField()
    is_consumed = models.BooleanField(default=False)

    def __str__(self):
        return f"Token for {self.user.email} [{self.content_type}]"

    @classmethod
    def generate_token(cls, user, content_type, content_id, ip_address='127.0.0.1', ttl_hours=6):
        raw_token = secrets.token_hex(32)
        expires_at = timezone.now() + timezone.timedelta(hours=ttl_hours)
        return cls.objects.create(
            user=user,
            token=raw_token,
            content_type=content_type,
            content_id=content_id,
            ip_address=ip_address,
            expires_at=expires_at
        )

    @property
    def is_valid(self):
        return timezone.now() < self.expires_at


class PlaybackSession(models.Model):
    """
    Active live streaming session recording device, bitrate, and concurrent streams.
    """
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playback_sessions')
    device_id = models.CharField(max_length=100)
    content_type = models.CharField(max_length=20)
    content_id = models.UUIDField()
    started_at = models.DateTimeField(auto_now_add=True)
    last_heartbeat = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-last_heartbeat']

    def __str__(self):
        return f"Session {self.session_id} - {self.user.email}"
