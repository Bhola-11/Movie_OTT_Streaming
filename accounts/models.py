import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    """
    Primary User model for CineVerse.
    Email acts as the unique login credential.
    """
    class RoleChoices(models.TextChoices):
        VIEWER = 'VIEWER', _('Viewer')
        CREATOR = 'CREATOR', _('Content Creator')
        MODERATOR = 'MODERATOR', _('Content Moderator')
        ADMIN = 'ADMIN', _('Administrator')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    username = models.CharField(_('username'), max_length=150, unique=True, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.VIEWER)
    
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_active_at = models.DateTimeField(default=timezone.now)
    
    country = models.CharField(max_length=100, default='United States')
    preferred_language = models.CharField(max_length=10, default='en')
    max_active_streams = models.PositiveSmallIntegerField(default=2)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['is_active', 'is_verified']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else (self.username or self.email.split('@')[0])

    @property
    def is_admin(self):
        return self.role == self.RoleChoices.ADMIN or self.is_superuser

    @property
    def is_creator(self):
        return self.role in [self.RoleChoices.CREATOR, self.RoleChoices.ADMIN]

    @property
    def is_moderator(self):
        return self.role in [self.RoleChoices.MODERATOR, self.RoleChoices.ADMIN]

    @property
    def is_vip_subscriber(self):
        """
        Calculates if the user currently holds an active VIP or Premium subscription tier.
        """
        active_sub = self.subscriptions.filter(status='ACTIVE', expires_at__gt=timezone.now()).first() if hasattr(self, 'subscriptions') else None
        if active_sub and active_sub.plan.tier_code in ['VIP', 'PREMIUM', 'ULTRA_4K']:
            return True
        return self.is_staff

    @property
    def current_subscription(self):
        if hasattr(self, 'subscriptions'):
            return self.subscriptions.filter(status='ACTIVE', expires_at__gt=timezone.now()).select_related('plan').first()
        return None

    def get_absolute_url(self):
        return reverse('accounts:profile')


class UserProfile(models.Model):
    """
    Detailed profile preferences controlling OTT video player behaviors,
    parental locks, audio/subtitle tracks, and playback bandwidth.
    """
    class QualityChoices(models.TextChoices):
        AUTO = 'AUTO', _('Auto (Adaptive)')
        UHD_4K = '4K', _('4K Ultra HD')
        FHD_1080P = '1080P', _('1080p Full HD')
        HD_720P = '720P', _('720p HD')
        SD_480P = '480P', _('480p Standard')

    class RatingLimitChoices(models.TextChoices):
        ALL = 'ALL', _('All Content (18+)')
        TEEN = 'PG-13', _('Teens (PG-13 / TV-14)')
        KIDS = 'PG', _('Kids & Family (G / PG / TV-Y7)')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    preferred_quality = models.CharField(max_length=10, choices=QualityChoices.choices, default=QualityChoices.AUTO)
    preferred_audio_lang = models.CharField(max_length=20, default='English')
    preferred_subtitle_lang = models.CharField(max_length=20, default='English')
    subtitles_enabled = models.BooleanField(default=True)
    auto_play_next = models.BooleanField(default=True)
    auto_play_trailers = models.BooleanField(default=True)
    data_saver_mode = models.BooleanField(default=False)
    
    # Parental & Kids Controls
    is_kids_mode = models.BooleanField(default=False)
    parental_pin = models.CharField(max_length=6, blank=True, null=True)
    content_rating_limit = models.CharField(max_length=10, choices=RatingLimitChoices.choices, default=RatingLimitChoices.ALL)

    # Notifications Preferences
    email_new_releases = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    browser_push_notifications = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"


class UserDevice(models.Model):
    """
    Tracks registered active devices per account to enforce concurrent stream limits.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=128, db_index=True)
    device_name = models.CharField(max_length=150, default='Web Browser')
    device_type = models.CharField(max_length=50, default='Desktop')
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'device_id')
        ordering = ['-last_used_at']

    def __str__(self):
        return f"{self.device_name} ({self.device_type}) - {self.user.email}"


class LoginHistory(models.Model):
    """
    Security audit log for sign-ins, IP tracking, and geo-heuristics.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_records')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    location_city = models.CharField(max_length=100, default='Unknown City')
    location_country = models.CharField(max_length=100, default='Unknown Country')
    status = models.CharField(max_length=20, default='SUCCESS')
    login_time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-login_time']
        verbose_name_plural = 'Login Histories'

    def __str__(self):
        return f"{self.user.email} - {self.status} at {self.login_time.strftime('%Y-%m-%d %H:%M')}"


class SecurityLog(models.Model):
    """
    Captures sensitive credential changes, 2FA updates, and access revocations.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs')
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.user.email}"
